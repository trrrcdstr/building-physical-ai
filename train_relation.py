"""
RelationEncoder 自监督训练（完全重写）
====================================
核心：三重损失函数 + 对比学习
  1. Rank Loss: P(ap) > P(an)
  2. Positive Loss: P(ap) → 1
  3. Triplet Margin: d(ap) + margin < d(an)
  4. InfoNCE: cosine similarity alignment
"""

import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Config:
    embed_dim: int = 128
    batch_size: int = 32
    lr: float = 3e-4
    epochs: int = 300
    eval_interval: int = 30
    seed: int = 42
    device: str = "cpu"


class TripletDataset(Dataset):
    """三元组：Anchor, Pos(近邻), Neg(远节点)"""
    def __init__(self, node_features, link_pairs):
        self.nodes = torch.tensor(node_features, dtype=torch.float32)
        self.n = len(node_features)

        # 构建邻居映射
        near_neighbors = defaultdict(list)
        far_nodes = defaultdict(list)

        for p in link_pairs:
            if p['label'] == 1:
                n1, n2 = p['node_i'], p['node_j']
                near_neighbors[n1].append(n2)
                near_neighbors[n2].append(n1)

        for nid in range(self.n):
            near_ids = set(near_neighbors.get(nid, []))
            far_nodes[nid] = [i for i in range(self.n) if i != nid and i not in near_ids]

        self.anchor_nodes = [n for n in range(self.n) if len(near_neighbors.get(n, [])) > 0]
        self.near_neighbors = near_neighbors
        self.far_nodes = far_nodes
        print(f'TripletDataset: {len(self.anchor_nodes)} anchors, avg_near={np.mean([len(near_neighbors.get(n,[])) for n in self.anchor_nodes]):.1f}')

    def __len__(self):
        return len(self.anchor_nodes)

    def __getitem__(self, idx):
        aid = self.anchor_nodes[idx]
        nears = self.near_neighbors.get(aid, [])
        fars = self.far_nodes.get(aid, [])

        if nears:
            pid = nears[np.random.randint(0, len(nears))]
        else:
            pid = (aid + 1) % self.n

        if fars:
            nid = fars[np.random.randint(0, len(fars))]
        else:
            nid = (aid + 2) % self.n

        return {'anchor': self.nodes[aid], 'pos': self.nodes[pid], 'neg': self.nodes[nid],
                'anchor_id': aid, 'pos_id': pid, 'neg_id': nid}


class LinkValDataset(Dataset):
    def __init__(self, pairs, node_features):
        self.nodes = torch.tensor(node_features, dtype=torch.float32)
        self.pairs = pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        p = self.pairs[idx]
        return {
            'feat_i': self.nodes[p['node_i']],
            'feat_j': self.nodes[p['node_j']],
            'label': float(p['label']),
        }


class RelationEncoder(nn.Module):
    def __init__(self, input_dim=25, embed_dim=128):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
            nn.Dropout(0.05),
            nn.Linear(embed_dim, embed_dim),
            nn.LayerNorm(embed_dim),
        )
        self.link_head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim),
            nn.GELU(),
            nn.Dropout(0.05),
            nn.Linear(embed_dim, 1),
        )

    def encode(self, x):
        return self.encoder(x)

    def predict(self, ei, ej):
        cat = torch.cat([ei, ej, ei * ej], dim=-1)
        return self.link_head(cat).squeeze(-1)

    def forward(self, anchor, pos, neg):
        ea = self.encode(anchor)
        ep = self.encode(pos)
        en = self.encode(neg)
        logit_ap = self.predict(ea, ep)
        logit_an = self.predict(ea, en)
        return {'ea': ea, 'ep': ep, 'en': en,
                'logit_ap': logit_ap, 'logit_an': logit_an,
                'prob_ap': torch.sigmoid(logit_ap), 'prob_an': torch.sigmoid(logit_an)}


def train(config: Config):
    base = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\cleaned')

    with open(base / 'link_data_clean.json', encoding='utf-8') as f:
        link_data = json.load(f)
    with open(base / 'scene_graph_clean.json', encoding='utf-8') as f:
        sg = json.load(f)

    nodes = np.array(sg['node_features'], dtype=np.float32)
    pairs = link_data['pairs']
    n_train = link_data['num_train']

    print(f'Nodes: {nodes.shape}, Train: {n_train}, Val: {len(pairs) - n_train}')

    train_ds = TripletDataset(nodes, pairs)
    val_ds = LinkValDataset(pairs[n_train:], nodes)
    train_loader = DataLoader(train_ds, batch_size=config.batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size)

    device = torch.device(config.device)
    model = RelationEncoder(input_dim=nodes.shape[1], embed_dim=config.embed_dim).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs)

    best_acc = 0.0
    best_epoch = 0
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)

    print(f'\nTraining RelationEncoder...')
    print('=' * 75)

    for epoch in range(1, config.epochs + 1):
        model.train()
        total_loss = 0

        for batch in train_loader:
            anc = batch['anchor'].to(device)
            pos = batch['pos'].to(device)
            neg = batch['neg'].to(device)

            out = model(anc, pos, neg)

            # Rank: P(ap) > P(an)
            rank_loss = F.relu(out['logit_an'] - out['logit_ap'] + 0.5).mean()
            # Positive: P(ap) -> 1
            pos_loss = F.binary_cross_entropy_with_logits(
                out['logit_ap'], torch.ones_like(out['logit_ap']))
            # Triplet margin: d(ap) < d(an) - margin
            d_ap = F.pairwise_distance(out['ea'], out['ep'])
            d_an = F.pairwise_distance(out['ea'], out['en'])
            triplet = F.relu(d_ap - d_an + 2.0).mean()
            # InfoNCE
            pos_sim = F.cosine_similarity(out['ea'], out['ep'])
            neg_sim = F.cosine_similarity(out['ea'], out['en'])
            nce = -torch.logaddexp(pos_sim, neg_sim).mean()

            loss = rank_loss + 0.5 * pos_loss + 0.3 * triplet + 0.2 * nce

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        scheduler.step()

        if epoch % config.eval_interval == 0 or epoch == 1:
            model.eval()
            tp = fp = tn = fn = 0

            with torch.no_grad():
                for batch in val_loader:
                    fi = batch['feat_i'].to(device)
                    fj = batch['feat_j'].to(device)
                    labels = batch['label']
                    logits = model.predict(model.encode(fi), model.encode(fj))
                    probs = torch.sigmoid(logits)

                    for prob, label in zip(probs.cpu(), labels):
                        if prob > 0.5:
                            if label == 1: tp += 1
                            else: fp += 1
                        else:
                            if label == 0: tn += 1
                            else: fn += 1

            acc = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
            avg_loss = total_loss / len(train_loader)

            print(f'Ep{epoch:3d} | L={avg_loss:.4f} | Acc={acc:.3f} P={prec:.3f} R={rec:.3f} F1={f1:.3f} | TP={tp} TN={tn} FP={fp} FN={fn} | Best={best_acc:.3f}@{best_epoch}')

            if acc > best_acc:
                best_acc = acc
                best_epoch = epoch
                save_model(model, config, epoch, best_acc)

    print(f'\nBest: Val Acc={best_acc:.3f} @ Epoch {best_epoch}')
    return model


def save_model(model, config, epoch, acc):
    out_dir = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\checkpoints')
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / 'relation_transformer_best.pt'
    torch.save({
        'epoch': epoch, 'acc': acc, 'model_state': model.state_dict(),
        'config': {'embed_dim': config.embed_dim, 'input_dim': 25},
    }, path)
    print(f'  [STAR] Saved: {path.name} (acc={acc:.3f})')


if __name__ == '__main__':
    train(Config())
