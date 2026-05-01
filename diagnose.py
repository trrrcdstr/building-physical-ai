import json
import numpy as np

base = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed'

print('=== 完整数据质量诊断 ===\n')

# 1. scene_graph_training
print('【1. scene_graph_training.json】')
with open(f'{base}\\scene_graph_training.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

nf = np.array(d['node_features'])
ef = np.array(d['edge_features'])
labels = np.array(d['labels'])

print(f'  节点特征: {nf.shape}  (248节点 × 48维)')
print(f'  边特征:   {ef.shape}  (11325边 × 2维)')
print(f'  节点标签: {np.unique(labels, return_counts=True)}')

print(f'\n  特征各维度统计:')
print(f'  维度   min     max     mean    std')
for i in range(nf.shape[1]):
    col = nf[:, i]
    if col.std() > 0.01:
        print(f'  [{i:2d}]  {col.min():7.3f}  {col.max():7.3f}  {col.mean():7.3f}  {col.std():7.3f}')

print(f'\n  标签分布:')
for lbl in np.unique(labels):
    print(f'    {lbl}: {(labels==lbl).sum()} 个节点')

print(f'\n  边特征分析 (前10条边):')
print(f'  {ef[:10]}')
print(f'  边特征唯一值: {np.unique(ef, axis=0)[:10]}')
print(f'  边特征种类数: {len(np.unique(ef, axis=0))}')

# 2. building_objects
print('\n【2. building_objects.json】')
with open(f'{base}\\building_objects.json', 'r', encoding='utf-8') as f:
    objs = json.load(f)
print(f'  对象数: {len(objs)}')
if objs:
    cats = {}
    for o in objs:
        c = o.get('category', 'unknown')
        cats[c] = cats.get(c, 0) + 1
    print(f'  类别分布: {cats}')
    print(f'  样例: {objs[0]}')

# 3. 核心问题分析
print('\n【核心问题分析】')
print(f'  ❌ 节点标签只有3类: appliance(17), door_window(151), furniture(80)')
print(f'  ❌ 每个类别内差异太大，特征难以区分')
print(f'  ❌ 48维特征中，某些维度 std=0.05（几乎无信息）')
print(f'  ❌ 边特征(11325,2) = 2维，是relation type的one-hot吗？')
print(f'\n  解决方案:')
print(f'  1. 改用自监督预训练 (BYOL/对比学习)')
print(f'  2. 特征标准化 (StandardScaler)')
print(f'  3. Link Prediction 任务 (预测边的关系类型)')
