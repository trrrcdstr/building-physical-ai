# -*- coding: utf-8 -*-
"""
build_scene_graph_real.py
从 building_objects.json 生成 scene_graph_real.json
用距离阈值（同房间 < 5m, 不同房间 >= 5m）
"""

import json, numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
BUILDING_OBJS = BASE / 'data' / 'processed' / 'building_objects.json'
OUTPUT_PATH   = BASE / 'data' / 'processed' / 'cleaned' / 'scene_graph_real.json'

print("=" * 60)
print("生成 scene_graph_real.json")
print("=" * 60)

with open(BUILDING_OBJS, encoding='utf-8') as f:
    objs = json.load(f)

print(f"加载 {len(objs)} 个建筑对象")

# ── 1. 构建9D特征 ────────────────────────────────────────────────────────────
def build_features(obj):
    pos = obj.get('position', [0, 0, 0])
    dim = obj.get('dimensions', {})
    x, y, z = pos[0], pos[1], pos[2]
    w = dim.get('width', 1.0)
    h = dim.get('height', 2.0)
    d = dim.get('depth', 0.1)
    area = w * h
    volume = w * h * d
    is_door = 1.0 if obj.get('type') == 'door' else 0.0
    is_window = 1.0 if obj.get('type') == 'window' else 0.0
    return [x, y, z, w, h, area, volume, is_door, is_window]

features   = [build_features(o) for o in objs]
positions  = [o.get('position', [0,0,0]) for o in objs]
names      = [o.get('name', o.get('id', f'obj-{i}')) for i, o in enumerate(objs)]
types_list = [o.get('type', 'unknown') for o in objs]
obj_ids    = [o.get('id', f'obj-{i}') for i, o in enumerate(objs)]

# ── 2. 用距离阈值构建边 ───────────────────────────────────────────────────────
print("\n用距离阈值构建空间关系边...")
ROOM_THRESH = 5.0  # 同房间 < 5m

positions_np = np.array(positions, dtype=np.float32)
n = len(positions_np)

same_room_pairs = []
diff_room_pairs = []

for i in range(n):
    for j in range(i + 1, n):
        d = float(np.linalg.norm(positions_np[i] - positions_np[j]))
        if d < ROOM_THRESH:
            same_room_pairs.append((i, j, d))
        else:
            diff_room_pairs.append((i, j, d))

print(f"  同房间 (<{ROOM_THRESH}m): {len(same_room_pairs)}")
print(f"  不同房间 (>={ROOM_THRESH}m): {len(diff_room_pairs)}")

# 1:1 平衡采样
np.random.seed(42)
n_pos = len(same_room_pairs)
n_neg = min(len(diff_room_pairs), n_pos * 2)  # 最多2倍
neg_indices = np.random.choice(len(diff_room_pairs), n_neg, replace=False)
neg_sampled = [diff_room_pairs[idx] for idx in neg_indices]

all_edges = same_room_pairs + neg_sampled
edge_labels = [1] * len(same_room_pairs) + [0] * len(neg_sampled)

print(f"  平衡后: 正={len(same_room_pairs)}, 负={len(neg_sampled)}, 总={len(all_edges)}")

# ── 3. 标准化 ─────────────────────────────────────────────────────────────────
feat_array = np.array(features, dtype=np.float32)
mean = feat_array.mean(axis=0)
std  = feat_array.std(axis=0) + 1e-8
feat_normalized = (feat_array - mean) / std

# ── 4. 构建边特征 ─────────────────────────────────────────────────────────────
edge_index   = [[i, j] for i, j, _ in all_edges]
edge_features = []
for i, j, d in all_edges:
    pos_i = positions_np[i]
    pos_j = positions_np[j]
    delta = (pos_j - pos_i)
    delta_norm = (delta / (d + 1e-6)).tolist()
    edge_features.append(delta_norm + [d])

# ── 5. 保存 ───────────────────────────────────────────────────────────────────
scene_graph = {
    "description": "建筑物理AI场景图谱 - 151个门/窗对象",
    "num_nodes": n,
    "num_edges": len(all_edges),
    "num_train": len(all_edges),
    "node_features": feat_normalized.tolist(),
    "node_features_raw": features,
    "node_names": names,
    "node_types": types_list,
    "node_positions": positions,
    "node_ids": obj_ids,
    "edge_index": edge_index,
    "edge_features": edge_features,
    "labels": edge_labels,
    "mean": mean.tolist(),
    "std": std.tolist(),
    "feature_dims": ["pos_x", "pos_y", "pos_z", "width", "height", "area", "volume", "is_door", "is_window"],
    "useful_dims": list(range(9)),
    "generated_at": "2026-04-15",
    "room_threshold": ROOM_THRESH,
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(scene_graph, f, ensure_ascii=False, indent=2)

size_kb = OUTPUT_PATH.stat().st_size / 1024
n_rooms_est = len(set(tuple(positions[i]) for i, j, d in same_room_pairs if d < 2.5))
print(f"\n✅ 保存: {OUTPUT_PATH} ({size_kb:.1f}KB)")
print(f"   节点: {n}, 边: {len(all_edges)} (正:{len(same_room_pairs)} 负:{len(neg_sampled)})")
