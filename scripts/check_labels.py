import json

with open('data/processed/scene_graph_training_clean.json', encoding='utf-8') as f:
    data = json.load(f)

print('Keys:', list(data.keys()))

labels = data.get('labels', [])
edge_feat = data.get('edge_features', [])
n_pos = sum(1 for l in labels if l == 1)
n_neg = sum(1 for l in labels if l == 0)
print(f'标签: 正={n_pos}, 负={n_neg}, 总={len(labels)}')

if edge_feat:
    print('\n边特征示例 (前10条):')
    for k in range(min(10, len(edge_feat))):
        ef = edge_feat[k]
        lbl = labels[k]
        dist = ef[-1] if ef else 0
        delta = ef[:3] if ef else []
        print(f'  [{k}] label={lbl}, dist={dist:.2f}m, delta={delta}')
