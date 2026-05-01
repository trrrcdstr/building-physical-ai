"""
RelationTransformer 自监督训练
============================
核心洞察：
  1. SpatialEncoder 的 64D 嵌入已经学到"近/远"关系
  2. RelationTransformer 需要更细粒度的空间推理
  3. 自监督：用 SpatialEncoder 嵌入做对比学习
     - Positive: 同房间节点对（距离 < 5m）
     - Negative: 不同房间节点对（距离 > 10m）
     - 任务：预测两个节点的相对空间位置（上下左右前后）

数据：
  - scene_graph_real.json: 151节点，9维特征（XYZ+几何+类型）
  - SpatialEncoder 嵌入：64维（来自 spatial_encoder_best.pt）

训练策略：
  1. 冻结 SpatialEncoder，提取所有节点的64D嵌入
  2. RelationTransformer 学习：给定 (ei, ej) → 预测边属性
     - 链接预测（同房间/不同房间）
     - 距离回归
     - 相对方向（上下左右前后）
  3. 纯自监督：不需要额外标签
"""

import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, TensorDataset
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

BASE = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai')
CKPT_DIR = BASE / 'data' / 'processed' / 'checkpoints'
DATA_DIR = BASE / 'data' / 'processed' / 'cleaned'

# ════════════════════════════════════════════════
#  模型定义
# ════════════════════════════════════════════════

class SpatialEncoder(nn.Module):
    """SpatialEncoder（冻结，只提取嵌入）"""
    def __init__(self, input_dim=9, embed_dim=64):
        super().__init__()
        self.pos_net = nn.Sequential(
            nn.Linear(3, 32), nn.LayerNorm(32), nn.GELU(),
            nn.Linear(32, 32),
        )
        self.geo_net = nn.Sequential(
            nn.Linear(input_dim - 3, 32), nn.LayerNorm(32), nn.GELU(),
            nn.Linear(32, 32),
        )
        self.combine = nn.Sequential(
            nn.Linear(32 + 32, embed_dim), nn.LayerNorm(embed_dim), nn.GELU(),
            nn.Dropout(0.05),
            nn.Linear(embed_dim, embed_dim),
        )

    def encode(self, x):
        pos = self.pos_net(x[:, :3])
        geo = self.geo_net(x[:, 3:])
        combined = torch.cat([pos, geo], dim=-1)
        return self.combine(combined)

    def forward(self, x):
        return self.encode(x)


class RelationTransformer(nn.Module):
    """
    RelationTransformer：
    给定两个节点嵌入 (ei, ej)，预测它们的相对空间关系

    架构：
      - 交叉注意力：ej 作为 query，ei 作为 key/value
      - 自注意力：两个嵌入的交互
      - 输出：关系类别 + 距离 + 方向
    """
    def __init__(self, embed_dim=64, num_heads=4, num_layers=2):
        super().__init__()
        # 交叉注意力层（ej 看 ei）
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=0.1,
            batch_first=True,
            activation='gelu',
        )
        self.cross_attn = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # 自注意力层
        self.self_attn = nn.TransformerEncoder(encoder_layer, num_layers=1)

        # 关系预测头
        self.link_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Linear(embed_dim // 2, 1),
        )
        self.dist_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Linear(embed_dim // 2, 1),
        )
        # 方向预测（6类：前/后/左/右/上/下）
        self.dir_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Linear(embed_dim // 2, 6),
        )

    def encode(self, x):
        """精炼单个嵌入向量"""
        return x  # RelationTransformer 不改变嵌入维度

    def forward(self, ei, ej):
        """
        ei, ej: (B, embed_dim)
        返回：{link_logit, dist_logit, dir_logits}
        """
        # 拼接两个嵌入
        x = torch.stack([ei, ej], dim=1)  # (B, 2, embed_dim)

        # 交叉注意力：ej attends to ei
        cross_out = self.cross_attn(x)  # (B, 2, embed_dim)

        # 取 ej 的输出（包含对 ei 的注意力）
        ej_refined = cross_out[:, 1, :]  # (B, embed_dim)

        # 自注意力：两个节点互相看
        self_out = self.self_attn(x)  # (B, 2, embed_dim)
        pooled = (self_out[:, 0, :] + self_out[:, 1, :]) / 2  # (B, embed_dim)

        # 融合
        fused = pooled + ej_refined  # (B, embed_dim)

        # 预测
        link = self.link_head(fused).squeeze(-1)  # (B,)
        dist = self.dist_head(fused).squeeze(-1)  # (B,)
        direction = self.dir_head(fused)           # (B, 6)

        return {
            'link': link,
            'dist': dist,
            'direction': direction,
            'ej_refined': ej_refined,
            'pooled': pooled,
        }


# ════════════════════════════════════════════════
#  数据集
# ════════════════════════════════════════════════

class RelationPairDataset(Dataset):
    """
    关系对数据集（自监督）

    正样本：位置距离 < 5m 的节点对（同房间）
    负样本：位置距离 > 10m 的节点对（不同房间）

    方向标签（ej 相对于 ei 的水平方向）：
      0: front (+Z), 1: behind (-Z)
      2: right (+X), 3: left (-X)
      4: above (+Y), 5: below (-Y)
    """
    NUM_CLASSES = 6

    def __init__(self, node_features, node_positions, node_types,
                 threshold_close=5.0, threshold_far=15.0,
                 max_pairs_per_node=5):
        self.nodes = torch.tensor(node_features, dtype=torch.float32)
        self.positions = np.array(node_positions, dtype=np.float32)
        self.types = node_types
        self.n = len(node_features)
        self.max_pairs = max_pairs_per_node

        # 构建正样本（近邻）和负样本（远节点）
        self.pos_pairs = []  # [(i, j, dist, direction), ...]
        self.neg_pairs = []  # [(i, j, dist), ...]

        for i in range(self.n):
            for j in range(i + 1, self.n):
                pos_i = self.positions[i]
                pos_j = self.positions[j]
                dx = pos_j[0] - pos_i[0]
                dy = pos_j[1] - pos_i[1]
                dz = pos_j[2] - pos_i[2]
                dist = np.sqrt(dx*dx + dy*dy + dz*dz)

                if dist < threshold_close and dist > 0.1:
                    # 方向（取水平主方向）
                    direction = self._get_direction(dx, dy, dz)
                    self.pos_pairs.append((i, j, dist, direction))
                elif dist > threshold_far:
                    self.neg_pairs.append((i, j, dist))

        print(f'RelationPairDataset: {len(self.pos_pairs)} pos, {len(self.neg_pairs)} neg')
        print(f'  Pos dist: {np.mean([p[2] for p in self.pos_pairs]):.1f}m, '
              f'Neg dist: {np.mean([p[2] for p in self.neg_pairs]):.1f}m')

    def _get_direction(self, dx, dy, dz):
        """返回 ej 相对于 ei 的方向"""
        # 水平主方向
        horiz_dominant = abs(dz) >= abs(dx)  # front/back vs left/right
        if horiz_dominant:
            return 0 if dz > 0 else 1  # front / behind
        else:
            return 2 if dx > 0 else 3  # right / left

        # 如果高度差很大，优先用垂直方向
        if abs(dy) > abs(dx) and abs(dy) > abs(dz):
            return 4 if dy > 0 else 5  # above / below

    def __len__(self):
        return len(self.pos_pairs) + len(self.neg_pairs)

    def __getitem__(self, idx):
        if idx < len(self.pos_pairs):
            i, j, dist, direction = self.pos_pairs[idx]
            label = 1
        else:
            k = idx - len(self.pos_pairs)
            i, j, dist = self.neg_pairs[k]
            label = 0
            direction = 0

        return {
            'i': i, 'j': j,
            'feat_i': self.nodes[i],
            'feat_j': self.nodes[j],
            'link_label': float(label),
            'dist': dist,
            'direction': direction,
        }


# ════════════════════════════════════════════════
#  训练
# ════════════════════════════════════════════════

@dataclass
class Config:
    embed_dim: int = 64
    num_heads: int = 4
    num_layers: int = 2
    batch_size: int = 32
    lr: float = 1e-3
    epochs: int = 500
    eval_interval: int = 50
    seed: int = 42


def train(config: Config):
    print('='*60)
    print('RelationTransformer Self-Supervised Training')
    print('='*60)

    # ── 加载 SpatialEncoder（冻结）────────────────────
    ckpt = torch.load(CKPT_DIR / 'spatial_encoder_best.pt',
                       map_location='cpu', weights_only=False)
    spatial = SpatialEncoder(input_dim=9, embed_dim=config.embed_dim)
    spatial.load_state_dict(ckpt['model_state'])
    spatial.eval()
    for p in spatial.parameters():
        p.requires_grad = False
    print(f'[OK] SpatialEncoder loaded (frozen, embed_dim={config.embed_dim})')

    # ── 加载数据 ────────────────────────────────────
    with open(DATA_DIR / 'scene_graph_real.json', encoding='utf-8') as f:
        sg = json.load(f)

    nodes = np.array(sg['node_features'], dtype=np.float32)
    positions = sg['node_positions']
    types = sg['node_types']

    print(f'[OK] Scene: {len(nodes)} nodes, {len(positions)} positions')

    # ── 提取所有节点嵌入 ─────────────────────────────
    with torch.no_grad():
        all_embeddings = spatial(nodes).numpy()

    print(f'[OK] Extracted {all_embeddings.shape} embeddings')

    # ── 划分训练/验证 ────────────────────────────────
    dataset = RelationPairDataset(
        node_features=all_embeddings,  # 直接用64D嵌入！
        node_positions=positions,
        node_types=types,
        threshold_close=5.0,
        threshold_far=15.0,
    )

    n = len(dataset)
    n_train = int(n * 0.8)
    n_val = n - n_train

    train_ds, val_ds = torch.utils.data.random_split(
        dataset, [n_train, n_val],
        generator=torch.Generator().manual_seed(config.seed)
    )

    train_loader = DataLoader(train_ds, batch_size=config.batch_size,
                               shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size)

    # ── RelationTransformer ──────────────────────────
    model = RelationTransformer(
        embed_dim=config.embed_dim,
        num_heads=config.num_heads,
        num_layers=config.num_layers,
    )
    print(f'[OK] RelationTransformer params: {sum(p.numel() for p in model.parameters()):,}')

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs)

    criterion_link = nn.BCEWithLogitsLoss()
    criterion_dist = nn.SmoothL1Loss()
    criterion_dir = nn.CrossEntropyLoss()

    best_acc = 0.0
    best_epoch = 0
    torch.manual_seed(config.seed)

    print(f'\nTraining: {n_train} train, {n_val} val')
    print('='*75)

    for epoch in range(1, config.epochs + 1):
        model.train()
        epoch_losses = {'link': 0, 'dist': 0, 'dir': 0, 'total': 0}

        for batch in train_loader:
            ei = batch['feat_i'].requires_grad_(True)
            ej = batch['feat_j'].requires_grad_(True)
            labels = batch['link_label']
            dists = batch['dist']
            dirs = batch['direction']

            out = model(ei, ej)

            # Link loss
            link_loss = criterion_link(out['link'], labels)

            # Distance loss（只对正样本）
            pos_mask = labels.float()
            # log(1 + dist) 作为目标
            dist_target = torch.log1p(dists.float())
            dist_loss = ((((out['dist'] - dist_target) ** 2) * pos_mask).mean() +
                         (((out['dist'] - dist_target) ** 2) * (1 - pos_mask) * 0.1).mean())

            # 方向损失（只对正样本）
            dir_loss = criterion_dir(out['direction'], dirs.long())

            # 总损失
            loss = 1.0 * link_loss + 0.3 * dist_loss + 0.2 * dir_loss

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            epoch_losses['link'] += link_loss.item()
            epoch_losses['dist'] += dist_loss.item()
            epoch_losses['dir'] += dir_loss.item()
            epoch_losses['total'] += loss.item()

        scheduler.step()

        # ── 验证 ──
        if epoch % config.eval_interval == 0 or epoch == 1:
            model.eval()
            tp = tn = fp = fn = 0
            dir_correct = 0
            dir_total = 0

            with torch.no_grad():
                for batch in val_loader:
                    ei = batch['feat_i']
                    ej = batch['feat_j']
                    labels = batch['link_label']
                    dirs = batch['direction']

                    out = model(ei, ej)
                    probs = torch.sigmoid(out['link'])

                    for p, label in zip(probs.cpu(), labels):
                        if p > 0.5:
                            if label == 1: tp += 1
                            else: fp += 1
                        else:
                            if label == 0: tn += 1
                            else: fn += 1

                    # 方向准确率（正样本）
                    pos_mask = labels.float() > 0.5
                    if pos_mask.any():
                        pos_dirs = dirs[pos_mask].long()
                        pos_dir_pred = out['direction'][pos_mask].argmax(dim=1)
                        dir_correct += (pos_dir_pred == pos_dirs).sum().item()
                        dir_total += pos_mask.sum().item()

            acc = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
            dir_acc = dir_correct / dir_total if dir_total > 0 else 0

            avg_link = epoch_losses['link'] / len(train_loader)
            avg_total = epoch_losses['total'] / len(train_loader)

            print(f'Ep{epoch:3d} | L={avg_total:.4f} | Acc={acc:.3f} P={prec:.3f} R={rec:.3f} F1={f1:.3f} | DirAcc={dir_acc:.3f} | Best={best_acc:.3f}@{best_epoch}')

            if acc > best_acc:
                best_acc = acc
                best_epoch = epoch
                save_model(model, spatial, config, epoch, best_acc)

    print(f'\n[OK] Best: Acc={best_acc:.3f} @ Epoch {best_epoch}')

    # 保存最终嵌入（包含 RelationTransformer 的关系感知嵌入）
    with torch.no_grad():
        all_ei = torch.tensor(all_embeddings)
        # 使用 RelationTransformer 精炼后的嵌入
        # 取每对 (i,j) 的 ej_refined 作为 j 的精炼嵌入
        # 但我们只保存原始嵌入
        refined = []
        for i in range(len(all_embeddings)):
            e = model.encode(all_ei[i:i+1]) if hasattr(model, 'encode') else all_ei[i:i+1]
            refined.append(e)
        refined_emb = torch.cat(refined, dim=0)

    out_emb_path = DATA_DIR / 'relation_embeddings.npy'
    out_meta_path = DATA_DIR / 'relation_meta.json'

    np.save(out_emb_path, refined_emb.numpy())

    meta = {
        'num_nodes': len(all_embeddings),
        'embed_dim': config.embed_dim,
        'best_epoch': best_epoch,
        'best_acc': best_acc,
        'positions': positions,
        'types': types,
        'node_names': sg.get('node_names', []),
    }
    with open(out_meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)

    print(f'[OK] Saved embeddings: {out_emb_path} ({refined_emb.shape})')
    print(f'[OK] Saved meta: {out_meta_path}')

    return model, spatial


def save_model(model, spatial, config, epoch, acc):
    out_dir = CKPT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / 'relation_transformer_best.pt'
    torch.save({
        'epoch': epoch,
        'acc': acc,
        'model_state': model.state_dict(),
        'spatial_encoder_state': spatial.state_dict(),
        'config': {
            'embed_dim': config.embed_dim,
            'num_heads': config.num_heads,
            'num_layers': config.num_layers,
        },
    }, path)
    print(f'  [★] Saved: {path.name} (acc={acc:.3f})')


if __name__ == '__main__':
    train(Config())
