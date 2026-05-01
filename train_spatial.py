"""
Spatial Relation Learning（真实位置数据）
=========================================
数据：151个门/窗，9维特征（位置XYZ + bbox + type）
正样本：2-4m（同房间），负样本：6-296m
"""
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    embed_dim: int = 64
    batch_size: int = 32
    lr: float = 1e-3
    epochs: int = 500
    eval_interval: int = 50
    seed: int = 42
    device: str = "cpu"


class SpatialDataset(Dataset):
    """空间关系数据集"""
    def __init__(self, pairs, nodes, is_train=True):
        self.nodes = torch.tensor(nodes, dtype=torch.float32)
        self.pairs = pairs
        self.is_train = is_train

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        p = self.pairs[idx]
        return {
            'feat_i': self.nodes[p['node_i']],
            'feat_j': self.nodes[p['node_j']],
            'label': float(p['label']),
            'dist': p['distance'],
            'dist_horiz': p.get('distance_horiz', p['distance']),
            'rel': p.get('relation', 'unknown'),
        }


class SpatialEncoder(nn.Module):
    """
    空间关系编码器
    关键：position特征（XYZ）是最重要的信息来源
    """
    def __init__(self, input_dim=9, embed_dim=64):
        super().__init__()
        # 分别处理位置特征和几何特征
        self.pos_net = nn.Sequential(
            nn.Linear(3, 32),  # 位置XYZ
            nn.LayerNorm(32),
            nn.GELU(),
            nn.Linear(32, 32),
        )
        self.geo_net = nn.Sequential(
            nn.Linear(input_dim - 3, 32),  # bbox + type
            nn.LayerNorm(32),
            nn.GELU(),
            nn.Linear(32, 32),
        )
        # 组合头（pos 32D + geo 32D = 64D）
        self.combine = nn.Sequential(
            nn.Linear(32 + 32, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
            nn.Dropout(0.05),
            nn.Linear(embed_dim, embed_dim),
        )
        # 链接预测
        self.link_head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, 1),
        )
        # 距离预测
        self.dist_head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, 1),
        )

    def encode(self, x):
        pos = self.pos_net(x[:, :3])       # XYZ
        geo = self.geo_net(x[:, 3:])      # bbox + type
        combined = torch.cat([pos, geo], dim=-1)
        return self.combine(combined)

    def forward(self, fi, fj):
        ei = self.encode(fi)
        ej = self.encode(fj)
        cat = torch.cat([ei, ej, ei * ej], dim=-1)
        link = self.link_head(cat).squeeze(-1)
        dist = self.dist_head(cat).squeeze(-1)
        return {
            'ei': ei, 'ej': ej,
            'link_prob': torch.sigmoid(link),
            'link_logit': link,
            'dist_pred': dist,
        }


def train(config: Config):
    base = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\cleaned')

    with open(base / 'link_data_real.json', encoding='utf-8') as f:
        link_data = json.load(f)
    with open(base / 'scene_graph_real.json', encoding='utf-8') as f:
        sg = json.load(f)

    nodes = np.array(sg['node_features'], dtype=np.float32)
    pairs = link_data['pairs']
    n_train = link_data['num_train']

    # 分离位置特征（XYZ）和几何特征
    positions = np.array(sg['node_positions'], dtype=np.float32)
    node_types = sg['node_types']

    print(f'Nodes: {nodes.shape}')
    print(f'  Position range X: [{positions[:,0].min():.1f}, {positions[:,0].max():.1f}]')
    print(f'  Types: door={node_types.count("door")}, window={node_types.count("window")}')
    print(f'Train: {n_train}, Val: {len(pairs) - n_train}')

    pos_dist = [p['distance'] for p in pairs if p['label'] == 1]
    neg_dist = [p['distance'] for p in pairs if p['label'] == 0]
    print(f'Pos dist: mean={np.mean(pos_dist):.1f}m')
    print(f'Neg dist: mean={np.mean(neg_dist):.1f}m')

    # 标准化
    mean = nodes.mean(axis=0)
    std = nodes.std(axis=0) + 1e-8
    nodes_norm = (nodes - mean) / std

    train_ds = SpatialDataset(pairs[:n_train], nodes_norm)
    val_ds = SpatialDataset(pairs[n_train:], nodes_norm, is_train=False)
    train_loader = DataLoader(train_ds, batch_size=config.batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size)

    device = torch.device(config.device)
    model = SpatialEncoder(input_dim=nodes.shape[1], embed_dim=config.embed_dim).to(device)
    print(f'Model params: {sum(p.numel() for p in model.parameters()):,}')

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs)

    criterion = nn.BCEWithLogitsLoss()
    best_acc = 0.0
    best_epoch = 0
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)

    print(f'\nTraining SpatialEncoder...')
    print('=' * 80)

    for epoch in range(1, config.epochs + 1):
        model.train()
        total_loss = 0

        for batch in train_loader:
            fi = batch['feat_i'].to(device)
            fj = batch['feat_j'].to(device)
            labels = batch['label'].to(device)
            dist_horiz = batch['dist_horiz'].to(device)

            out = model(fi, fj)

            # Link loss
            link_loss = criterion(out['link_logit'], labels)

            # Distance regression (L1 smooth)
            dist_loss = F.smooth_l1_loss(out['dist_pred'], torch.log1p(dist_horiz))

            loss = link_loss + 0.3 * dist_loss

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        scheduler.step()

        if epoch % config.eval_interval == 0 or epoch == 1:
            model.eval()
            tp = fp = tn = fn = 0
            dist_errors = []

            with torch.no_grad():
                for batch in val_loader:
                    fi = batch['feat_i'].to(device)
                    fj = batch['feat_j'].to(device)
                    labels = batch['label']
                    dist_horiz = batch['dist_horiz']

                    out = model(fi, fj)
                    probs = out['link_prob'].cpu()

                    for prob, label, d in zip(probs, labels, dist_horiz):
                        if prob > 0.5:
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

            avg_loss = total_loss / len(train_loader)
            print(f'Ep{epoch:3d} | L={avg_loss:.4f} | Acc={acc:.3f} P={prec:.3f} R={rec:.3f} F1={f1:.3f} | TP={tp} TN={tn} FP={fp} FN={fn} | Best={best_acc:.3f}@{best_epoch}')

            if acc >= best_acc:
                best_acc = acc
                best_epoch = epoch
                save_model(model, config, epoch, best_acc)

    print(f'\nBest: Val Acc={best_acc:.3f} @ Epoch {best_epoch}')
    return model


def save_model(model, config, epoch, acc):
    out_dir = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\checkpoints')
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / 'spatial_encoder_best.pt'
    torch.save({
        'epoch': epoch, 'acc': acc,
        'model_state': model.state_dict(),
        'config': {'embed_dim': config.embed_dim, 'input_dim': 9},
    }, path)
    print(f'  [STAR] Saved: {path.name} (acc={acc:.3f})')


if __name__ == '__main__':
    train(Config())
