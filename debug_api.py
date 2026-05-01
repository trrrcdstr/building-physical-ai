"""Debug: 检查标准化是否正确"""
import json, numpy as np, torch

DATA = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\cleaned'
CKPT = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\checkpoints\spatial_encoder_best.pt'

# 加载数据
with open(DATA + '\\scene_graph_real.json', encoding='utf-8') as f:
    sg = json.load(f)

nodes = np.array(sg['node_features'], dtype=np.float32)
mean = np.array(sg.get('mean', [0]*9), dtype=np.float32)
std = np.array(sg.get('std', [1]*9), dtype=np.float32)
positions = sg['node_positions']

print(f'Nodes: {nodes.shape}')
print(f'Mean: {mean}')
print(f'Std: {std}')
print(f'Node[0] raw: {nodes[0]}')
print(f'Node[0] after server norm: {(nodes[0] - mean) / (std + 1e-8)}')

# 检查 node_features 是否已经标准化
print(f'\nNode[0] stats: mean={nodes[0].mean():.3f}, std={nodes[0].std():.3f}')
print(f'All nodes mean: {nodes.mean(axis=0)}')
print(f'All nodes std: {nodes.std(axis=0)}')

# 加载模型
import torch.nn as nn

class SpatialEncoder(nn.Module):
    def __init__(self, input_dim=9, embed_dim=64):
        super().__init__()
        self.pos_net = nn.Sequential(
            nn.Linear(3, 32), nn.LayerNorm(32), nn.GELU(), nn.Linear(32, 32))
        self.geo_net = nn.Sequential(
            nn.Linear(input_dim - 3, 32), nn.LayerNorm(32), nn.GELU(), nn.Linear(32, 32))
        self.combine = nn.Sequential(
            nn.Linear(32 + 32, embed_dim), nn.LayerNorm(embed_dim), nn.GELU(),
            nn.Dropout(0.05), nn.Linear(embed_dim, embed_dim))
        self.link_head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim), nn.GELU(), nn.Linear(embed_dim, 1))
        self.dist_head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim), nn.GELU(), nn.Linear(embed_dim, 1))

    def encode(self, x):
        pos = self.pos_net(x[:, :3])
        geo = self.geo_net(x[:, 3:])
        return self.combine(torch.cat([pos, geo], dim=-1))

    def forward(self, fi, fj):
        ei = self.encode(fi)
        ej = self.encode(fj)
        cat = torch.cat([ei, ej, ei * ej], dim=-1)
        link = self.link_head(cat).squeeze(-1)
        dist = self.dist_head(cat).squeeze(-1)
        return {'link_prob': torch.sigmoid(link), 'dist_pred': dist}

ckpt = torch.load(CKPT, map_location='cpu', weights_only=False)
model = SpatialEncoder(input_dim=9, embed_dim=64)
model.load_state_dict(ckpt['model_state'])
model.eval()

# 测试：直接用 raw features（已经是标准化的）
print('\n=== 直接用 raw features（已标准化）===')
for i, j in [(0, 1), (0, 10), (0, 50), (0, 100)]:
    fi = torch.tensor([nodes[i]], dtype=torch.float32)
    fj = torch.tensor([nodes[j]], dtype=torch.float32)
    out = model(fi, fj)
    p = out['link_prob'].item()
    pos_i = positions[i]
    pos_j = positions[j]
    d = np.sqrt(sum((a-b)**2 for a,b in zip(pos_i, pos_j)))
    print(f'  Node {i} vs {j}: dist={d:.1f}m, p={p:.4f}')

# 测试：再次标准化（double normalization）
print('\n=== 再次标准化（double norm）===')
for i, j in [(0, 1), (0, 10), (0, 50), (0, 100)]:
    fi = torch.tensor([(nodes[i] - mean) / (std + 1e-8)], dtype=torch.float32)
    fj = torch.tensor([(nodes[j] - mean) / (std + 1e-8)], dtype=torch.float32)
    out = model(fi, fj)
    p = out['link_prob'].item()
    pos_i = positions[i]
    pos_j = positions[j]
    d = np.sqrt(sum((a-b)**2 for a,b in zip(pos_i, pos_j)))
    print(f'  Node {i} vs {j}: dist={d:.1f}m, p={p:.4f}')
