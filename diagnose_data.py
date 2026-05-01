"""数据诊断脚本"""
import json
import numpy as np
from pathlib import Path

base = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed'

# 1. scene_graph_training_clean
with open(f'{base}\\scene_graph_training_clean.json', encoding='utf-8') as f:
    d = json.load(f)

nf = np.array(d['node_features'], dtype=np.float32)
ei = np.array(d['edge_index'])
ef = np.array(d['edge_features'], dtype=np.float32)
labels = np.array(d['labels'])

print('=== Scene Graph Training (Clean) ===')
print(f'Nodes: {nf.shape}, Edges: {ei.shape}, Edge features: {ef.shape}')
print(f'Labels: {labels.shape}')

print('\nLabel distribution:')
unique, counts = np.unique(labels, return_counts=True)
for u, c in zip(unique, counts):
    print(f'  {u}: {c}')

print('\nTop feature dims by variance:')
variances = np.var(nf, axis=0)
for i, (dim, var) in enumerate(sorted(enumerate(variances), key=lambda x: -x[1])[:15]):
    print(f'  dim[{dim}]: var={var:.6f}')

print(f'\nEdge feature stats: mean={ef.mean():.4f}, std={ef.std():.4f}, range=[{ef.min():.4f}, {ef.max():.4f}]')
print(f'Non-zero ratio: {(ef != 0).mean():.2%}')

# 2. relation_training_data
print('\n=== Relation Training Data ===')
with open(f'{base}\\relation_training_data.json', encoding='utf-8') as f:
    rd = json.load(f)
print(f'Total pairs: {len(rd["pairs"])}')
pairs = rd['pairs']
pos = [p for p in pairs if p['label'] == 1]
neg = [p for p in pairs if p['label'] == 0]
print(f'Positive (same-scene edge): {len(pos)}, Negative (random): {len(neg)}')

# 3. building_objects
print('\n=== Building Objects ===')
with open(f'{base}\\building_objects.json', encoding='utf-8') as f:
    objs = json.load(f)
print(f'Total objects: {len(objs)}')

# Check coverage
types = {}
for o in objs:
    t = o.get('category', 'unknown')
    types[t] = types.get(t, 0) + 1
print('Category distribution:')
for k, v in sorted(types.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')

# 4. VR links structured
print('\n=== VR Links ===')
with open(f'{base}\\vr_links_structured.json', encoding='utf-8') as f:
    vr = json.load(f)
print(f'VRs: {len(vr)}, rooms: {sum(len(x.get("rooms", [])) for x in vr)}')
