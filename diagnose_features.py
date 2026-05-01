"""诊断节点特征的信息量"""
import json
import numpy as np

base = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\cleaned'

with open(base + '\\scene_graph_clean.json', encoding='utf-8') as f:
    sg = json.load(f)
with open(base + '\\link_data_clean.json', encoding='utf-8') as f:
    ld = json.load(f)

nodes = np.array(sg['node_features'], dtype=np.float32)
pairs = ld['pairs']
n_train = ld['num_train']

print(f'Nodes: {nodes.shape}')

# 标准化
mean = nodes.mean(axis=0)
std = nodes.std(axis=0) + 1e-8
nodes_norm = (nodes - mean) / std

print(f'\nFeature stats after normalization:')
for i in range(nodes.shape[1]):
    v = nodes_norm[:, i]
    print(f'  dim[{i:2d}]: mean={v.mean():+.3f} std={v.std():.3f} min={v.min():.2f} max={v.max():.2f}')

# 分析标签和特征的相关性
labels = np.array([p['label'] for p in pairs])
pos_idx = set()
neg_idx = set()
for p in pairs[:n_train]:
    if p['label'] == 1:
        pos_idx.add(p['node_i'])
        pos_idx.add(p['node_j'])
    else:
        neg_idx.add(p['node_i'])
        neg_idx.add(p['node_j'])

print(f'\nPos nodes: {len(pos_idx)}, Neg nodes: {len(neg_idx)}')
print(f'Overlap: {len(pos_idx & neg_idx)}')

# 特征对标签的区分力（t-test）
print('\nFeature discriminative power (t-test pos vs neg on nodes):')
pos_nodes = np.array(list(pos_idx))
neg_nodes = np.array(list(neg_idx))
for i in range(min(nodes.shape[1], 15)):
    pos_mean = nodes_norm[pos_nodes, i].mean()
    neg_mean = nodes_norm[neg_nodes, i].mean()
    diff = abs(pos_mean - neg_mean)
    print(f'  dim[{i:2d}]: pos_mean={pos_mean:+.3f} neg_mean={neg_mean:+.3f} diff={diff:.3f}')

# 检查特征的前几个维度（可能是 bbox）
print(f'\nFirst 6 dims (likely bbox):')
for i in range(6):
    vals = nodes[:, i]
    print(f'  dim[{i}]: mean={vals.mean():.3f}, std={vals.std():.3f}, range=[{vals.min():.2f}, {vals.max():.2f}]')
