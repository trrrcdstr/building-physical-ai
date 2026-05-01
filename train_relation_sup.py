"""
RelationTransformer 自监督训练
============================
策略：冻结 SpatialEncoder 提取64D嵌入，用对比学习训练 RelationTransformer

输入：SpatialEncoder 的64D嵌入（已编码"近/远"关系）
任务：学习更细粒度的空间关系
  1. Link Prediction: 同房间(close) vs 不同房间(far)
  2. Distance Regression: 预测物理距离
  3. Direction Prediction: 预测相对方向（6类）

数据：scene_graph_real.json
  - 151节点（门/窗），沿墙排列，X=[0, 300]m
  - 正样本（< 5m）= 相邻门
  - 负样本（> 15m）= 远距离门
"""

import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from dataclasses import dataclass

BASE = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai')
CKPT_DIR = BASE / 'data' / 'processed' / 'checkpoints'
DATA_DIR = BASE / 'data' / 'processed' / 'cleaned'


# ════════════════════════════════════════════════
#  模型
# ════════════════════════════════════════════════

class SpatialEncoder(nn.Module):
    """SpatialEncoder（冻结）— 与 train_spatial.py 保存的模型结构完全一致"""
    def __init__(self, input_dim=9, embed_dim=64):
        super().__init__()
        self.pos_net = nn.Sequential(
            nn.Linear(3, 32), nn.LayerNorm(32), nn.GELU(),
            nn.Linear(32, 32))
        self.geo_net = nn.Sequential(
            nn.Linear(input_dim - 3, 32), nn.LayerNorm(32), nn.GELU(),
            nn.Linear(32, 32))
        self.combine = nn.Sequential(
            nn.Linear(32 + 32, embed_dim), nn.LayerNorm(embed_dim), nn.GELU(),
            nn.Dropout(0.05), nn.Linear(embed_dim, embed_dim))
        # 预测头（与 checkpoint 匹配）
        self.link_head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim), nn.GELU(),
            nn.Linear(embed_dim, 1))
        self.dist_head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim), nn.GELU(),
            nn.Linear(embed_dim, 1))

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
    给定两个节点的 64D 嵌入，用 Transformer 预测它们的空间关系

    架构：
      - 交叉注意力：ej attends to ei
      - 自注意力：节点对内部交互
      - 输出：链接 + 距离 + 方向
    """
    def __init__(self, embed_dim=64, num_heads=4, num_layers=2):
        super().__init__()

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=num_heads,
            dim_feedforward=embed_dim * 4, dropout=0.1,
            batch_first=True, activation='gelu',
        )

        # 交叉注意力（ej attends to ei）
        self.cross_attn = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        # 自注意力
        self.self_attn = nn.TransformerEncoder(encoder_layer, num_layers=1)

        # 预测头
        self.link_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2), nn.GELU(),
            nn.Linear(embed_dim // 2, 1),
        )
        self.dist_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2), nn.GELU(),
            nn.Linear(embed_dim // 2, 1),
        )
        # 方向（6类：front/behind/right/left/above/below）
        self.dir_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2), nn.GELU(),
            nn.Linear(embed_dim // 2, 6),
        )

    def forward(self, ei, ej):
        """ei, ej: (B, 64)"""
        x = torch.stack([ei, ej], dim=1)  # (B, 2, 64)

        # 交叉注意力
        cross_out = self.cross_attn(x)[:, 1, :]  # (B, 64) — ej 的精炼表示

        # 自注意力 + 平均池化
        self_out = self.self_attn(x).mean(dim=1)  # (B, 64)

        # 融合
        fused = cross_out + self_out  # (B, 64)

        return {
            'link_logit': self.link_head(fused).squeeze(-1),
            'dist': self.dist_head(fused).squeeze(-1),
            'direction': self.dir_head(fused),  # (B, 6)
        }


# ════════════════════════════════════════════════
#  数据集
# ════════════════════════════════════════════════

class RelationDataset(Dataset):
    """
    关系数据集（自监督）
    - 传入64D嵌入和真实位置
    - 正样本：dist < 5m（同房间）
    - 负样本：dist > 15m（不同房间）
    - 方向：ej 相对于 ei 的水平主方向
    """
    DIR_NAMES = ['front', 'behind', 'right', 'left', 'above', 'below']

    def __init__(self, raw_features, positions, names,
                 threshold_close=5.0, threshold_far=15.0):
        self.embeddings = torch.tensor(raw_features, dtype=torch.float32)
        self.positions = np.array(positions, dtype=np.float32)
        self.names = names
        self.n = len(positions)

        # 构建正样本和负样本
        pos_pairs = []
        neg_pairs = []

        for i in range(self.n):
            for j in range(i + 1, self.n):
                pi = self.positions[i]
                pj = self.positions[j]
                dx = pj[0] - pi[0]
                dy = pj[1] - pi[1]
                dz = pj[2] - pi[2]
                dist = float(np.sqrt(dx*dx + dy*dy + dz*dz))

                if dist < threshold_close and dist > 0.1:
                    dir_idx = self._direction(dx, dy, dz)
                    pos_pairs.append((i, j, dist, dir_idx))
                elif dist > threshold_far:
                    neg_pairs.append((i, j, dist))

        # 平衡采样：负样本最多 = 3x 正样本数量
        np.random.seed(42)
        if len(neg_pairs) > len(pos_pairs) * 3:
            chosen = np.random.choice(len(neg_pairs), len(pos_pairs) * 3, replace=False)
            neg_pairs = [neg_pairs[c] for c in chosen]

        self.pos_pairs = pos_pairs
        self.neg_pairs = neg_pairs  # 都是 (i, j, dist) 元组

        print(f'RelationDataset: {len(pos_pairs)} pos, {len(neg_pairs)} neg')
        if pos_pairs:
            d = [p[2] for p in pos_pairs]
            print(f'  Pos dist: [{min(d):.1f}, {max(d):.1f}], mean={np.mean(d):.1f}m')

    def _direction(self, dx, dy, dz):
        # 垂直优先（高度差 > 1m）
        if abs(dy) > 1.0:
            return 4 if dy > 0 else 5
        # 水平主方向
        if abs(dz) >= abs(dx):
            return 0 if dz >= 0 else 1
        return 2 if dx >= 0 else 3

    def __len__(self):
        return len(self.pos_pairs) + len(self.neg_pairs)

    def __getitem__(self, idx):
        if idx < len(self.pos_pairs):
            i, j, dist, direction = self.pos_pairs[idx]
            link_label = 1.0
        else:
            k = idx - len(self.pos_pairs)
            i, j, dist = self.neg_pairs[k]
            link_label = 0.0
            direction = 0

        return {
            'feat_i': self.embeddings[i],
            'feat_j': self.embeddings[j],
            'link_label': link_label,
            'dist': dist,
            'direction': direction,
            'name_i': self.names[i] if i < len(self.names) else f'obj-{i}',
            'name_j': self.names[j] if j < len(self.names) else f'obj-{j}',
        }

    def _neg_at(self, k):
        """获取负样本对"""
        i = np.random.randint(0, self.n)
        j = np.random.randint(0, self.n)
        while abs(i - j) < 10:  # 确保足够远
            j = np.random.randint(0, self.n)
        pi = self.positions[i]
        pj = self.positions[j]
        dist = float(np.sqrt(sum((a-b)**2 for a, b in zip(pi, pj))))
        return (i, j, dist)


# ════════════════════════════════════════════════
#  训练
# ════════════════════════════════════════════════

@dataclass
class Config:
    embed_dim: int = 64
    num_heads: int = 4
    num_layers: int = 2
    batch_size: int = 32
    lr: float = 5e-4
    epochs: int = 500
    eval_interval: int = 30
    seed: int = 42


def train(config: Config):
    print('='*60)
    print('RelationTransformer Self-Supervised Training')
    print('='*60)

    # ── 加载 SpatialEncoder（冻结）────────────────────
    ckpt_path = CKPT_DIR / 'spatial_encoder_best.pt'
    if not ckpt_path.exists():
        print(f'[!!] spatial_encoder_best.pt not found at {ckpt_path}')
        return

    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    spatial = SpatialEncoder(input_dim=9, embed_dim=config.embed_dim)
    spatial.load_state_dict(ckpt['model_state'])
    spatial.eval()
    for p in spatial.parameters():
        p.requires_grad = False
    print(f'[OK] SpatialEncoder loaded (frozen, embed_dim={config.embed_dim})')

    # ── 加载原始特征 + 位置 ─────────────────────────────
    with open(DATA_DIR / 'scene_graph_real.json', encoding='utf-8') as f:
        sg = json.load(f)

    raw_features = np.array(sg['node_features'], dtype=np.float32)  # (151, 9)
    positions = sg['node_positions']                                  # (151, 3)
    names = sg.get('node_names', [])

    print(f'[OK] Scene: {len(raw_features)} nodes')

    # ── 提取所有节点的 64D 嵌入 ─────────────────────────
    with torch.no_grad():
        all_embeddings = spatial(torch.tensor(raw_features, dtype=torch.float32)).numpy()

    print(f'[OK] Extracted {all_embeddings.shape} embeddings from SpatialEncoder')

    # 保存嵌入和元数据
    emb_out = DATA_DIR / 'spatial_embeddings.npy'
    np.save(emb_out, all_embeddings)
    print(f'[OK] Saved: {emb_out}')

    # ── 创建数据集 ────────────────────────────────────
    dataset = RelationDataset(
        raw_features=all_embeddings,  # 64D 嵌入
        positions=positions,
        names=names,
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

    print(f'[OK] Train: {n_train}, Val: {n_val}')

    # ── RelationTransformer ────────────────────────────
    model = RelationTransformer(
        embed_dim=config.embed_dim,
        num_heads=config.num_heads,
        num_layers=config.num_layers,
    )
    n_params = sum(p.numel() for p in model.parameters())
    print(f'[OK] RelationTransformer: {n_params:,} params')

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs)

    criterion_link = nn.BCEWithLogitsLoss()
    criterion_dir = nn.CrossEntropyLoss()

    best_acc = 0.0
    best_epoch = 0
    torch.manual_seed(config.seed)

    print(f'\nTraining {config.epochs} epochs...')
    print('='*80)

    for epoch in range(1, config.epochs + 1):
        model.train()
        total_link = total_dist = total_dir = total_loss = 0
        n_batches = 0

        for batch in train_loader:
            ei = batch['feat_i']
            ej = batch['feat_j']
            labels = batch['link_label']
            dists = batch['dist']
            dirs = batch['direction']

            out = model(ei, ej)

            # Link loss
            link_loss = criterion_link(out['link_logit'], labels)

            # Distance regression（正样本用 L1）
            pos_mask = labels.float()
            dist_loss = (torch.abs(out['dist'] - torch.log1p(dists)) * pos_mask).mean()

            # 方向损失（正样本）
            dir_loss = criterion_dir(out['direction'], dirs.long())

            loss = link_loss + 0.3 * dist_loss + 0.2 * dir_loss

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_link += link_loss.item()
            total_dist += dist_loss.item()
            total_dir += dir_loss.item()
            total_loss += loss.item()
            n_batches += 1

        scheduler.step()

        if epoch % config.eval_interval == 0 or epoch == 1:
            model.eval()
            tp = tn = fp = fn = 0

            with torch.no_grad():
                for batch in val_loader:
                    ei = batch['feat_i']
                    ej = batch['feat_j']
                    labels = batch['link_label']

                    out = model(ei, ej)
                    probs = torch.sigmoid(out['link_logit'])

                    for p, label in zip(probs.cpu(), labels):
                        if float(p) > 0.5:
                            if label == 1: tp += 1
                            else: fp += 1
                        else:
                            if label == 0: tn += 1
                            else: fn += 1

            total = tp + tn + fp + fn
            acc = (tp + tn) / total if total > 0 else 0
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0

            avg_link = total_link / n_batches
            avg_total = total_loss / n_batches

            print(f'Ep{epoch:3d} | L={avg_total:.4f} Link={avg_link:.4f} | '
                  f'Acc={acc:.3f} P={prec:.3f} R={rec:.3f} F1={f1:.3f} | '
                  f'TP={tp} TN={tn} FP={fp} FN={fn} | Best={best_acc:.3f}@{best_epoch}')

            if acc > best_acc:
                best_acc = acc
                best_epoch = epoch
                save_checkpoint(model, spatial, config, epoch, best_acc)

    print(f'\n[OK] Best: Val Acc={best_acc:.3f} @ Epoch {best_epoch}')

    # 保存嵌入和元数据
    meta = {
        'num_nodes': len(all_embeddings),
        'embed_dim': config.embed_dim,
        'best_epoch': best_epoch,
        'best_acc': float(best_acc),
        'positions': positions,
        'types': sg.get('node_types', []),
        'names': names,
    }
    meta_out = DATA_DIR / 'relation_meta.json'
    with open(meta_out, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'[OK] Saved meta: {meta_out}')

    return model, spatial


def save_checkpoint(model, spatial, config, epoch, acc):
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
