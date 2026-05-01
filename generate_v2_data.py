"""
生成 scene_graph_v2 和 link_prediction_data（不依赖 SceneGraphBuilder）
"""
import json
import numpy as np
import random

base = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed'

# 加载清洗后的数据
with open(f'{base}\\scene_graph_training_clean.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

nf_clean = np.array(d['node_features'], dtype=np.float32)
edge_index = np.array(d['edge_index'])
edge_features = np.array(d['edge_features'])
labels = np.array(d['labels'])
useful_dims = d['useful_dims']

print(f'Loaded: {nf_clean.shape}, dims={useful_dims}')

# ============================================================
# 生成 scene_graph_v2：基于清洗后的特征 + 细分类别
# ============================================================
print('Generating scene_graph_v2...')

# 使用原始 building_objects 的信息来构建更细的节点
with open(f'{base}\\building_objects.json', 'r', encoding='utf-8') as f:
    objs = json.load(f)

# 读取 vr_links_structured 获取场景-节点映射
with open(f'{base}\\vr_links_structured.json', 'r', encoding='utf-8') as f:
    vr_data = json.load(f)

# 构建新场景（从 VR 数据提取）
new_scenes = []
node_idx = 0

# 类别名称映射（粗->细）
LABEL_MAP = {
    'appliance': '电器',
    'door_window': '门窗',
    'furniture': '家具',
}

for vr in vr_data:
    scene_id = vr.get('id', '')
    rooms = vr.get('rooms', [])
    
    for room in rooms:
        room_id = f"{scene_id}_{room.get('id', 'room')}"
        objects = room.get('objects', [])
        
        nodes = []
        for obj in objects:
            name = obj.get('name', '')
            dims = obj.get('dimensions', {})
            pos = obj.get('position', [0, 0, 0])
            
            # 推断细分类别
            kw = name + ' ' + obj.get('type', '') + ' ' + obj.get('style', '')
            if any(k in kw for k in ['门', 'door']):
                cat = '门'
            elif any(k in kw for k in ['窗', 'window']):
                cat = '窗'
            elif any(k in kw for k in ['灯', 'lamp', 'light']):
                cat = '灯具'
            elif any(k in kw for k in ['沙', 'sofa']):
                cat = '沙发'
            elif any(k in kw for k in ['桌', 'table']):
                cat = '桌子'
            elif any(k in kw for k in ['椅', 'chair', 'seat']):
                cat = '椅子'
            elif any(k in kw for k in ['床', 'bed']):
                cat = '床'
            elif any(k in kw for k in ['柜', 'cabinet', 'shelf']):
                cat = '柜子'
            elif any(k in kw for k in ['楼梯', 'stair']):
                cat = '楼梯'
            elif any(k in kw for k in ['墙', 'wall']):
                cat = '墙体'
            else:
                cat = '其他'
            
            nodes.append({
                'id': f'node_{node_idx}',
                'name': name,
                'category': cat,
                'position': pos,
                'dimensions': [dims.get('w', 1), dims.get('h', 1), dims.get('d', 1)],
                'bbox': [dims.get('w', 1), dims.get('h', 1), dims.get('d', 1)],
            })
            node_idx += 1
        
        if len(nodes) >= 2:
            new_scenes.append({
                'scene_id': scene_id,
                'room_id': room_id,
                'nodes': nodes,
            })

print(f'Scene graph v2: {len(new_scenes)} scenes, {node_idx} nodes')

with open(f'{base}\\scene_graph_v2.json', 'w', encoding='utf-8') as f:
    json.dump({'scenes': new_scenes, 'num_scenes': len(new_scenes)}, f, ensure_ascii=False, indent=2)
print('[OK] scene_graph_v2.json saved')

# ============================================================
# 生成 Link Prediction 数据
# ============================================================
print('Generating link_prediction_data...')

# 使用清洗后的节点特征（248节点，标准化后）
all_nodes_features = nf_clean.tolist()

# 生成正样本和负样本
positive_pairs = edge_index.tolist()  # (2, N) -> list of (i, j)
negative_pairs = []

all_node_ids = list(range(len(all_nodes_features)))
random.seed(42)

for _ in range(len(positive_pairs)):
    i, j = random.sample(all_node_ids, 2)
    negative_pairs.append([i, j])

print(f'Link Prediction: {len(positive_pairs)} pos + {len(negative_pairs)} neg')

lp_data = {
    'num_nodes': len(all_nodes_features),
    'positive_pairs': positive_pairs,
    'negative_pairs': negative_pairs,
    'node_features': all_nodes_features,
    'useful_dims': useful_dims,
    'feature_stats': {
        'mean': d['feature_mean'],
        'std': d['feature_std'],
    }
}

with open(f'{base}\\link_prediction_data.json', 'w', encoding='utf-8') as f:
    json.dump(lp_data, f, ensure_ascii=False, indent=2)
print('[OK] link_prediction_data.json saved')

# ============================================================
# 同时：生成适合 RelationTransformer 训练的数据
# 任务：Link Prediction（边存在预测）
# ============================================================
print('Updating RelationTransformer training data...')

# 合并正负样本
all_pairs = []
for i, j in positive_pairs:
    all_pairs.append({'node_i': int(i), 'node_j': int(j), 'label': 1})
for i, j in negative_pairs:
    all_pairs.append({'node_i': int(i), 'node_j': int(j), 'label': 0})

random.shuffle(all_pairs)
n_total = len(all_pairs)
n_train = int(n_total * 0.8)

rel_data = {
    'num_nodes': len(all_nodes_features),
    'num_train': n_train,
    'num_val': n_total - n_train,
    'node_features': all_nodes_features,
    'pairs': all_pairs,
    'useful_dims': useful_dims,
    'task': 'link_prediction',
}

with open(f'{base}\\relation_training_data.json', 'w', encoding='utf-8') as f:
    json.dump(rel_data, f, ensure_ascii=False, indent=2)
print(f'[OK] relation_training_data.json saved ({n_total} samples: {n_train} train, {n_total-n_train} val)')

print('All data files generated successfully!')
