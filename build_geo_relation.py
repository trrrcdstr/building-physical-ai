"""从真实坐标计算建筑对象间的空间关系"""
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from itertools import combinations

base = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed')
out = base / 'cleaned'
out.mkdir(exist_ok=True)

# 加载 building_objects（151个有真实位置的对象）
with open(base / 'building_objects.json', encoding='utf-8') as f:
    objects = json.load(f)

print(f'Objects: {len(objects)}')

# 检查有多少有真实位置
with_pos = [o for o in objects if 'position' in o and o['position']]
print(f'With position: {len(with_pos)}')

# 分析类型分布
types = defaultdict(list)
for o in objects:
    t = o.get('type', 'unknown')
    types[t].append(o)

print('\nType distribution:')
for t, objs in sorted(types.items(), key=lambda x: -len(x[1])):
    print(f'  {t}: {len(objs)}')

# ============================================================
# 策略：用物体中心点之间的距离计算空间关系
# ============================================================
print('\nComputing spatial relationships...')

# 解析所有对象的位置
# 注意：position 可能是 [x, y, z] 或 {x, y, z} 格式
parsed = []
for o in objects:
    pos = o.get('position', [])
    if isinstance(pos, list) and len(pos) >= 3:
        x, y, z = pos[0], pos[1], pos[2]
        dim = o.get('dimensions', {})
        w = dim.get('width', 1.0)
        h = dim.get('height', 1.0)
        d = dim.get('depth', 1.0)
        parsed.append({
            'id': o.get('id', f'obj-{len(parsed)}'),
            'name': o.get('name', ''),
            'type': o.get('type', 'unknown'),
            'category': o.get('category', 'unknown'),
            'x': x, 'y': y, 'z': z,
            'w': w, 'h': h, 'd': d,
        })

print(f'Parsed: {len(parsed)} objects with valid positions')

# 计算两两距离
positions = np.array([[o['x'], o['y'], o['z']] for o in parsed], dtype=np.float32)

print(f'Position range:')
print(f'  X: [{positions[:,0].min():.1f}, {positions[:,0].max():.1f}]')
print(f'  Y: [{positions[:,1].min():.1f}, {positions[:,1].max():.1f}]')
print(f'  Z: [{positions[:,2].min():.1f}, {positions[:,2].max():.1f}]')

# ============================================================
# 定义空间关系类型
# ============================================================
THRESHOLDS = {
    'adjacent': 0.5,       # 紧邻（物体边缘相距 < 0.5m）
    'near': 2.0,           # 近邻（中心距 < 2m）
    'same_room': 5.0,      # 同房间（中心距 < 5m）
    'diff_room': 10.0,     # 不同房间（> 10m）
}

def dist3d(i, j):
    return np.sqrt(np.sum((positions[i] - positions[j]) ** 2))

def get_relation(i, j):
    d = dist3d(i, j)
    oi, oj = parsed[i], parsed[j]
    
    # 水平距离（忽略高度差）
    d_horiz = np.sqrt((oi['x'] - oj['x'])**2 + (oi['z'] - oj['z'])**2)
    dy = abs(oi['y'] - oj['y'])
    
    # 关系分类
    if d < THRESHOLDS['adjacent']:
        rel = 'adjacent'
    elif d < THRESHOLDS['near']:
        rel = 'near'
    elif d < THRESHOLDS['same_room']:
        rel = 'same_room'
    else:
        rel = 'far'
    
    # 相对位置（水平面）
    dx = oj['x'] - oi['x']
    dz = oj['z'] - oi['z']
    if abs(dx) > abs(dz):
        h_dir = 'right' if dx > 0 else 'left'
    else:
        h_dir = 'front' if dz > 0 else 'behind'
    
    # 垂直关系
    v_dir = 'above' if dy > 1.0 else ('below' if dy < -1.0 else 'same_level')
    
    return {
        'node_i': i,
        'node_j': j,
        'distance': float(d),
        'distance_horiz': float(d_horiz),
        'relation': rel,
        'direction': h_dir,
        'vertical': v_dir,
        'type_i': oi['type'],
        'type_j': oj['type'],
        'label': 1 if rel in ('adjacent', 'near', 'same_room') else 0,
    }

# 构建所有关系
all_relations = []
n = len(parsed)
for i in range(n):
    for j in range(i + 1, n):
        rel = get_relation(i, j)
        all_relations.append(rel)

print(f'\nAll pairwise relations: {len(all_relations)}')
print(f'Positive (near): {sum(1 for r in all_relations if r["label"] == 1)}')
print(f'Negative (far): {sum(1 for r in all_relations if r["label"] == 0)}')

# 关系类型分布
rel_types = defaultdict(int)
for r in all_relations:
    rel_types[r['relation']] += 1
print('\nRelation type distribution:')
for k, v in sorted(rel_types.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

# ============================================================
# 构建特征：几何特征 + 位置特征
# ============================================================
def object_to_feature(obj, positions):
    """
    对象的特征向量：
    - 几何: bbox(6) + volume(1)
    - 位置: xyz(3)  -- 这是关键！位置信息
    - 材质/类型编码(10)
    """
    f = []
    # 几何特征
    f.append(obj['w'])
    f.append(obj['h'])
    f.append(obj['d'])
    f.append(obj['w'] * obj['d'])          # footprint
    f.append(obj['w'] * obj['h'] * obj['d'])  # volume
    f.append(obj['x'])                      # 位置X
    f.append(obj['y'])                      # 位置Y
    f.append(obj['z'])                      # 位置Z
    
    # 类型编码
    type_map = {'door': 0, 'window': 1, 'wall': 2, 'floor': 3, 
                 'ceiling': 4, 'sofa': 5, 'table': 6, 'chair': 7,
                 'bed': 8, 'cabinet': 9}
    f.append(float(type_map.get(obj['type'], 10)))
    
    return f

# 构建节点特征
node_features = [object_to_feature(o, positions) for o in parsed]
node_features = np.array(node_features, dtype=np.float32)
print(f'\nNode features: {node_features.shape}')
print(f'  dims: bbox(5) + position(3) + type(1) = 9')

# 标准化（位置特征也要标准化）
mean = node_features.mean(axis=0)
std = node_features.std(axis=0) + 1e-8
node_features_norm = (node_features - mean) / std

# ============================================================
# 构建训练数据
# ============================================================
# 正样本：near + adjacent + same_room
# 负样本：far（距离 > 10m）

pos_relations = [r for r in all_relations if r['label'] == 1 and r['distance'] > 0.1]
neg_relations = [r for r in all_relations if r['label'] == 0]

# 平衡采样：负样本是5倍
np.random.seed(42)
neg_sample = list(np.random.choice(len(neg_relations), min(len(neg_relations), len(pos_relations) * 5), replace=False))
neg_relations_sampled = [neg_relations[i] for i in neg_sample]

all_pairs = pos_relations + neg_relations_sampled
np.random.shuffle(all_pairs)

n_train = int(len(all_pairs) * 0.8)
n_val = len(all_pairs) - n_train

print(f'\nTraining data: {n_train} train, {n_val} val')
print(f'  Pos: {len(pos_relations)}, Neg: {len(neg_relations_sampled)}')

# ============================================================
# 保存
# ============================================================
# A. Scene graph（用于推理）
scene_graph = {
    'num_nodes': len(parsed),
    'num_features': node_features_norm.shape[1],
    'node_features': node_features_norm.tolist(),
    'node_names': [o['name'] for o in parsed],
    'node_types': [o['type'] for o in parsed],
    'node_positions': positions.tolist(),
    'all_relations': all_relations,
    'mean': mean.tolist(),
    'std': std.tolist(),
}
with open(out / 'scene_graph_real.json', 'w', encoding='utf-8') as f:
    json.dump(scene_graph, f, indent=2, ensure_ascii=False)

# B. Link prediction 数据
link_data = {
    'num_nodes': len(parsed),
    'num_train': n_train,
    'pairs': all_pairs,
}
with open(out / 'link_data_real.json', 'w', encoding='utf-8') as f:
    json.dump(link_data, f, indent=2, ensure_ascii=False)

print(f'\n[OK] Saved:')
print(f'  scene_graph_real.json: {len(parsed)} nodes, {node_features_norm.shape[1]}D features')
print(f'  link_data_real.json: {n_train} train + {n_val} val')
print(f'\nPos dist range: [{min(r["distance"] for r in pos_relations):.2f}, {max(r["distance"] for r in pos_relations):.2f}]m')
print(f'Neg dist range: [{min(r["distance"] for r in neg_relations_sampled):.2f}, {max(r["distance"] for r in neg_relations_sampled):.2f}]m')
print(f'\n特征包含真实位置！模型可以学习空间关系！')
