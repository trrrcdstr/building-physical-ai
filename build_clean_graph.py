"""
重建干净的场景图数据
====================
核心洞察：
  1. 当前 edge_index 是"全连接"噪音（同一VR内所有物体两两相连）
  2. 真正有意义的边 = 物理空间关系（接触/靠近/包含）
  3. edge_features[0] = distance (m)，但很多值不合理（>50m）

清洗策略：
  A. 只保留 distance < 30m 的边（同一房间内的边）
  B. 对每个类别内部，采样负样本（距离 > 15m）
  C. Link Prediction: same_room(close) vs diff_room(far)
  D. Distance Regression: 只在 valid 边上做
"""

import json
import numpy as np
from pathlib import Path

base = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed')
out_base = base / 'cleaned'

# Load raw data
with open(base / 'scene_graph_training.json', encoding='utf-8') as f:
    d = json.load(f)

nodes = np.array(d['node_features'], dtype=np.float32)  # (248, 48)
edge_index_raw = np.array(d['edge_index'])               # (N, 2)
edge_features_raw = np.array(d['edge_features'], dtype=np.float32)  # (N, 2)
labels = np.array(d['labels'])
scene_ids = d['scene_ids']

print(f'Raw: {nodes.shape[0]} nodes, {edge_index_raw.shape[0]} edges')
print(f'Distance range: [{edge_features_raw[:,0].min():.1f}, {edge_features_raw[:,0].max():.1f}]m')

# ─── Step 1: 分析 scene 分布 ─────────────────────────
# 节点按哪个 scene 排列？scene_ids 有113个，但节点只有248个
# 113 scenes vs 248 nodes → 大约每个scene 2个节点（全连接图）
# 实际上：这113个scene是VR，每个VR里的物体互相全连接

# 分析：每个scene有多少物体？
# 方法：看看 edge_index 里哪些边在同一个 scene 内
# 113 scenes / 248 nodes ≈ 2.2 nodes/scene → 几乎每个scene只有2个物体，全连接

# ─── Step 2: 过滤无效边（距离 > 30m = 肯定不是同一房间）───
MAX_SAME_ROOM_DIST = 30.0  # 米
valid_mask = edge_features_raw[:, 0] < MAX_SAME_ROOM_DIST
valid_edges = edge_index_raw[valid_mask]
valid_dists = edge_features_raw[valid_mask, 0]

print(f'\nAfter distance filter (< {MAX_SAME_ROOM_DIST}m): {len(valid_edges)} / {len(edge_index_raw)} edges remain')

# ─── Step 3: 重新定义"边" ─────────────────────────────
# 原始边 = 无意义的全连接
# 新边 = 距离 < 30m 的物体对（物理上有意义）
# 节点对按距离从小到大排序，取 top-K

# 按距离排序
sort_idx = np.argsort(valid_dists)
sorted_edges = valid_edges[sort_idx]
sorted_dists = valid_dists[sort_idx]

# 取距离最近的边（top 500）
TOP_K = 500
selected_edges = sorted_edges[:TOP_K]
selected_dists = sorted_dists[:TOP_K]

print(f'Selected top {TOP_K} closest edges:')
print(f'  Distance range: [{selected_dists.min():.1f}, {selected_dists.max():.1f}]m')

# 构建节点-边映射
node_to_edges = {}
for i, (n1, n2) in enumerate(selected_edges):
    node_to_edges.setdefault(n1, []).append((n2, selected_dists[i]))
    node_to_edges.setdefault(n2, []).append((n1, selected_dists[i]))

# 统计每个节点的连接度
degrees = [len(node_to_edges.get(i, [])) for i in range(nodes.shape[0])]
degrees = np.array(degrees)
print(f'\nNode degree stats (cleaned):')
print(f'  mean={degrees.mean():.1f}, max={degrees.max()}, zero_degree_nodes={(degrees==0).sum()}')

# ─── Step 4: 构建训练样本 ───────────────────────────────
# 正样本：同一个 scene 内的近距离物体对（按距离采样）
# 负样本：不同 scene 的物体对

# 假设节点按 scene 分组（每个 scene 约 2-3 个节点）
# 从 edge_index 中提取 scene 信息：同一批节点在同一 scene
# 但我们不知道具体哪个节点在哪个 scene...

# 简化方法：用位置聚类
# 距离 < 5m 的节点 → 可能同一房间
# 距离 > 15m 的节点 → 不同房间

CLOSE_THRESHOLD = 5.0   # 同一房间
FAR_THRESHOLD = 15.0   # 不同房间

# 构建正样本：近距离边（< 5m）
close_mask = valid_dists < CLOSE_THRESHOLD
pos_pairs = valid_edges[close_mask]      # (N_pos, 2)
pos_dists = valid_dists[close_mask]       # (N_pos,)

# 构建负样本：中等距离（5-30m），随机采样
medium_mask = (valid_dists >= CLOSE_THRESHOLD) & (valid_dists < MAX_SAME_ROOM_DIST)
medium_edges = valid_edges[medium_mask]
medium_dists = valid_dists[medium_mask]

# 随机采样负样本（和正样本一样多）
np.random.seed(42)
n_pos = len(pos_pairs)
perm = np.random.permutation(len(medium_edges))[:n_pos]
neg_pairs = medium_edges[perm]
neg_dists = medium_dists[perm]

print(f'\nTraining samples:')
print(f'  Positive (close < {CLOSE_THRESHOLD}m): {len(pos_pairs)}')
print(f'  Negative (medium {CLOSE_THRESHOLD}-{MAX_SAME_ROOM_DIST}m): {len(neg_pairs)}')

# ─── Step 5: 构建节点特征 ───────────────────────────────
# 特征已经标准化了（所有维度 ~1.0 variance）
# 但某些维度是噪音，检查并过滤

variances = np.var(nodes, axis=0)
useful_dims = [i for i in range(nodes.shape[1]) if variances[i] > 0.001]
print(f'\nUseful feature dims: {len(useful_dims)} / {nodes.shape[1]}')
print(f'  Dims: {useful_dims}')

# 过滤后的特征
nodes_filtered = nodes[:, useful_dims]
print(f'Filtered node features: {nodes_filtered.shape}')

# ─── Step 6: 保存清洗后的数据 ───────────────────────────
out_base.mkdir(exist_ok=True)

# A. 场景图（用于 GraphSAGE/GCN）
scene_graph = {
    'num_nodes': nodes_filtered.shape[0],
    'num_features': nodes_filtered.shape[1],
    'node_features': nodes_filtered.tolist(),
    'edge_index': selected_edges.tolist(),      # top-K 最近的边
    'edge_distances': selected_dists.tolist(),
    'labels': labels.tolist(),
    'useful_dims': useful_dims,
    'scene_ids': scene_ids,
}
with open(out_base / 'scene_graph_clean.json', 'w', encoding='utf-8') as f:
    json.dump(scene_graph, f, indent=2, ensure_ascii=False)

# B. Link Prediction 数据（正负样本平衡）
all_pairs = []
for n1, n2 in pos_pairs:
    all_pairs.append({'node_i': int(n1), 'node_j': int(n2), 'label': 1, 'distance': float(pos_dists[list(pos_pairs[:,0]).index(n1) if n1 < len(pos_pairs) else 0])})

# 重建 pos_pairs distances 映射
pos_dist_map = {}
for i in range(len(pos_pairs)):
    n1, n2 = pos_pairs[i]
    pos_dist_map[(int(n1), int(n2))] = float(pos_dists[i])

neg_dist_map = {}
for i in range(len(neg_pairs)):
    n1, n2 = neg_pairs[i]
    neg_dist_map[(int(n1), int(n2))] = float(neg_dists[i])

link_pairs = []
for i in range(len(pos_pairs)):
    n1, n2 = int(pos_pairs[i,0]), int(pos_pairs[i,1])
    d = pos_dist_map.get((n1,n2)) or pos_dist_map.get((n2,n1)) or 0.0
    link_pairs.append({'node_i': n1, 'node_j': n2, 'label': 1, 'distance': d})

for i in range(len(neg_pairs)):
    n1, n2 = int(neg_pairs[i,0]), int(neg_pairs[i,1])
    d = neg_dist_map.get((n1,n2)) or neg_dist_map.get((n2,n1)) or 0.0
    link_pairs.append({'node_i': n1, 'node_j': n2, 'label': 0, 'distance': d})

n_train = len(link_pairs) * 80 // 100

link_data = {
    'num_nodes': nodes_filtered.shape[0],
    'num_train': n_train,
    'pairs': link_pairs,
}
with open(out_base / 'link_data_clean.json', 'w', encoding='utf-8') as f:
    json.dump(link_data, f, indent=2)

# C. Distance Regression 数据（只用有效边）
dist_pairs = []
for i in range(len(selected_edges)):
    n1, n2 = int(selected_edges[i,0]), int(selected_edges[i,1])
    dist_pairs.append({'node_i': n1, 'node_j': n2, 'distance': float(selected_dists[i])})

dist_data = {
    'num_nodes': nodes_filtered.shape[0],
    'pairs': dist_pairs,
    'distance_stats': {
        'mean': float(selected_dists.mean()),
        'std': float(selected_dists.std()),
        'min': float(selected_dists.min()),
        'max': float(selected_dists.max()),
    }
}
with open(out_base / 'distance_data_clean.json', 'w', encoding='utf-8') as f:
    json.dump(dist_data, f, indent=2)

print(f'\n[OK] Saved:')
print(f'  scene_graph_clean.json: {nodes_filtered.shape[0]} nodes, {len(selected_edges)} edges')
print(f'  link_data_clean.json: {len(link_pairs)} pairs ({n_train} train)')
print(f'  distance_data_clean.json: {len(dist_pairs)} pairs')
print(f'\nReady for RelationTransformer training!')
