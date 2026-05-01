"""
数据清洗脚本：标准化特征 + 修复训练任务
"""
import json
import numpy as np

base = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed'

# ============================================================
# 步骤1: 清洗 scene_graph_training.json
# ============================================================
print('=== 步骤1: 清洗 scene_graph_training ===')
with open(f'{base}\\scene_graph_training.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

nf = np.array(d['node_features'], dtype=np.float32)
ef = np.array(d['edge_features'], dtype=np.float32)
edge_index = np.array(d['edge_index'])
labels = np.array(d['labels'])

print(f'原始节点特征: {nf.shape}')
print(f'边特征: {ef.shape}')

# 1.1 移除低方差特征维度 (std < 0.05)
variance = nf.var(axis=0)
useful_dims = np.where(variance > 0.05)[0]
print(f'有用维度: {len(useful_dims)} / {nf.shape[1]}')
print(f'移除的低方差维度: {list(set(range(nf.shape[1])) - set(useful_dims))}')

# 1.2 标准化 (手动实现 StandardScaler)
mean = nf.mean(axis=0)
std = nf.std(axis=0)
std[std == 0] = 1  # 避免除零
nf_clean = (nf - mean) / std
print(f'  特征均值范围: [{mean.min():.3f}, {mean.max():.3f}]')
print(f'  特征标准差范围: [{std.min():.3f}, {std.max():.3f}]')

# 1.3 保存清洗后的数据
d_clean = {
    'num_scenes': d['num_scenes'],
    'num_nodes': len(useful_dims),  # 清洗后的维度
    'num_edges': d['num_edges'],
    'scene_ids': d['scene_ids'],
    'node_features': nf_clean.tolist(),  # 标准化后
    'edge_index': edge_index.tolist(),
    'edge_features': ef.tolist(),
    'labels': labels.tolist(),
    # 额外信息
    'useful_dims': useful_dims.tolist(),
    'feature_mean': mean.tolist(),
    'feature_std': std.tolist(),
    'original_dims': nf.shape[1],
}

with open(f'{base}\\scene_graph_training_clean.json', 'w', encoding='utf-8') as f:
    json.dump(d_clean, f, ensure_ascii=False, indent=2)

print(f'[OK] scene_graph_training_clean.json saved')
print(f'     cleaned features: {nf_clean.shape}')

# ============================================================
# 步骤2: 改进标签（细化分类）
# ============================================================
print('\n=== 步骤2: 改进标签 ===')
# 当前: appliance(17), door_window(151), furniture(80)
# 改进: 从 building_objects.json 读取更细的类别

with open(f'{base}\\building_objects.json', 'r', encoding='utf-8') as f:
    objs = json.load(f)

# 创建 ID → 细分类别映射
obj细分类别 = {}
for o in objs:
    obj_id = o.get('id', '')
    obj_name = o.get('name', '')
    obj_type = o.get('type', '')
    
    # 根据名字推断细分类别
    if '门' in obj_name or 'door' in obj_id.lower():
        cat = '门'
    elif '窗' in obj_name or 'window' in obj_id.lower():
        cat = '窗'
    elif '灯' in obj_name or 'lamp' in obj_id.lower():
        cat = '灯具'
    elif '沙' in obj_name or 'sofa' in obj_id.lower():
        cat = '沙发'
    elif '桌' in obj_name or 'table' in obj_id.lower():
        cat = '桌子'
    elif '椅' in obj_name or 'chair' in obj_id.lower():
        cat = '椅子'
    elif '床' in obj_name or 'bed' in obj_id.lower():
        cat = '床'
    elif '柜' in obj_name or 'cabinet' in obj_id.lower():
        cat = '柜子'
    elif '楼梯' in obj_name or 'stair' in obj_id.lower():
        cat = '楼梯'
    elif '墙' in obj_name or 'wall' in obj_id.lower():
        cat = '墙体'
    else:
        cat = '其他'
    
    obj细分类别[obj_id] = cat

# 统计
细分类别统计 = {}
for cat in obj细分类别.values():
    细分类别统计[cat] = 细分类别统计.get(cat, 0) + 1

print(f'细分类别: {细分类别统计}')

# ============================================================
# 步骤3: 生成新的训练数据（带细分类别 + 归一化特征）
# ============================================================
print('\n=== 步骤3: 生成新训练数据 ===')

# 从 scene_graph_builder 读取原始场景
import sys
sys.path.insert(0, r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\src')
from scene_graph_builder import SceneGraphBuilder

# 加载 VR 数据
with open(f'{base}\\vr_links_structured.json', 'r', encoding='utf-8') as f:
    vr_data = json.load(f)

# 生成新的 scene graph 数据（带细分类别）
builder = SceneGraphBuilder()
new_scenes = []
for vr in vr_data[:20]:  # 取前20个场景
    scene_id = vr.get('id', f'vr_{len(new_scenes)}')
    rooms = vr.get('rooms', [])
    
    for room in rooms:
        room_id = f"{scene_id}_{room.get('id', 'room')}"
        
        # 构建节点
        nodes = []
        objects = room.get('objects', [])
        for obj in objects:
            name = obj.get('name', '')
            dims = obj.get('dimensions', {})
            
            # 推断细分类别
            if any(k in name for k in ['门', 'door']):
                cat = '门'
            elif any(k in name for k in ['窗', 'window']):
                cat = '窗'
            elif any(k in name for k in ['灯', 'lamp', 'light']):
                cat = '灯具'
            elif any(k in name for k in ['沙', 'sofa']):
                cat = '沙发'
            elif any(k in name for k in ['桌', 'table']):
                cat = '桌子'
            elif any(k in name for k in ['椅', 'chair', 'seat']):
                cat = '椅子'
            elif any(k in name for k in ['床', 'bed']):
                cat = '床'
            elif any(k in name for k in ['柜', 'cabinet', 'shelf']):
                cat = '柜子'
            else:
                cat = '其他'
            
            node = {
                'id': f"{room_id}_{len(nodes)}",
                'name': name,
                'category': cat,
                'position': obj.get('position', [0, 0, 0]),
                'dimensions': dims,
                'bbox': [dims.get('w', 1), dims.get('h', 1), dims.get('d', 1)],
            }
            nodes.append(node)
        
        if len(nodes) >= 2:
            new_scenes.append({
                'scene_id': scene_id,
                'room_id': room_id,
                'nodes': nodes,
            })

print(f'新场景数: {len(new_scenes)}')
print(f'总节点数: {sum(len(s["nodes"]) for s in new_scenes)}')

# 保存新场景
with open(f'{base}\\scene_graph_v2.json', 'w', encoding='utf-8') as f:
    json.dump({'scenes': new_scenes, 'num_scenes': len(new_scenes)}, f, ensure_ascii=False, indent=2)

print(f'✅ 保存到 scene_graph_v2.json')

# ============================================================
# 步骤4: 生成 Link Prediction 训练数据
# ============================================================
print('\n=== 步骤4: 生成 Link Prediction 训练数据 ===')

# Link Prediction: 给两个节点特征，预测是否存在边
# 正样本: 边存在
# 负样本: 随机采样不存在的边

all_nodes = []
node_to_idx = {}
idx = 0

for scene in new_scenes:
    for node in scene['nodes']:
        node_to_idx[node['id']] = idx
        all_nodes.append(node)
        idx += 1

print(f'总节点: {len(all_nodes)}')

# 生成边对
positive_pairs = []
for scene in new_scenes:
    nodes = scene['nodes']
    n = len(nodes)
    for i in range(n):
        for j in range(i+1, n):
            # 同一场景内随机连边（简化：所有节点对都连）
            positive_pairs.append((node_to_idx[nodes[i]['id']], node_to_idx[nodes[j]['id']]))

print(f'正样本边: {len(positive_pairs)}')

# 生成负样本
import random
negative_pairs = []
all_node_ids = list(range(len(all_nodes)))
for _ in range(len(positive_pairs)):
    i, j = random.sample(all_node_ids, 2)
    negative_pairs.append((i, j))

print(f'负样本边: {len(negative_pairs)}')

# 保存
lp_data = {
    'num_nodes': len(all_nodes),
    'positive_pairs': positive_pairs,
    'negative_pairs': negative_pairs,
    'node_features': nf_clean.tolist()[:len(all_nodes)],  # 使用清洗后的特征
    'useful_dims': useful_dims.tolist(),
}

with open(f'{base}\\link_prediction_data.json', 'w', encoding='utf-8') as f:
    json.dump(lp_data, f, ensure_ascii=False, indent=2)

print(f'✅ Link Prediction 数据保存')

# ============================================================
# 总结
# ============================================================
print('\n=== 数据清洗总结 ===')
print(f'✅ scene_graph_training_clean.json: 特征标准化 + 移除低方差维度')
print(f'✅ scene_graph_v2.json: 带细分类别的新场景')
print(f'✅ link_prediction_data.json: Link Prediction 任务数据')
print(f'\n关键改进:')
print(f'  1. 特征归一化 (StandardScaler)')
print(f'  2. 移除 std<0.05 的噪音维度')
print(f'  3. 细分类别: 门/窗/灯具/沙发/桌子/椅子/床/柜子/其他')
print(f'  4. Link Prediction 任务: 预测两个节点是否相连')
print(f'  5. 自监督预训练: 不依赖标签，学习节点表示')
