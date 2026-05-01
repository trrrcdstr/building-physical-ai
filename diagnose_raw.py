"""Deep data diagnostic"""
import json
import numpy as np

base = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed'

# Load scene_graph_training.json
with open(base + '\\scene_graph_training.json', encoding='utf-8') as f:
    d = json.load(f)

print(f'Scenes: {d["num_scenes"]}')
print(f'Nodes: {d["num_nodes"]}')
print(f'Edges: {d["num_edges"]}')

# Analyze edge_index format
ei = d['edge_index']
print(f'\nEdge index format:')
print(f'  Type: {type(ei)}')
print(f'  Length: {len(ei)}')
print(f'  [0]: {ei[0]}')

# Analyze edge_features format
ef = d['edge_features']
print(f'\nEdge features format:')
print(f'  Type: {type(ef)}')
print(f'  Length: {len(ef)}')
print(f'  [0]: {ef[0]}')

# Try to extract distances
distances = []
for e in ef:
    if isinstance(e, dict):
        distances.append(e.get('distance', 0))
    elif isinstance(e, list):
        distances.append(sum(e) / len(e) if e else 0)
    else:
        distances.append(float(e))

distances = np.array(distances)
print(f'  Distances: mean={distances.mean():.1f}m, min={distances.min():.1f}m, max={distances.max():.1f}m')
print(f'  Zero-dist edges: {(distances == 0).sum()}')
print(f'  Large-dist edges (>50m): {(distances > 50).sum()}')

# Labels
labels = d['labels']
print(f'\nLabels:')
print(f'  Type: {type(labels)}, Length: {len(labels)}')
print(f'  [0]: {labels[0]}')

# Nodes
nodes = d['node_features']
print(f'\nNodes:')
print(f'  Type: {type(nodes)}, Length: {len(nodes)}')
print(f'  [0]: {str(nodes[0])[:200]}')

# Scene IDs
scene_ids = d['scene_ids']
print(f'\nScene IDs:')
print(f'  Length: {len(scene_ids)}')
print(f'  [0..4]: {scene_ids[0:5]}')
