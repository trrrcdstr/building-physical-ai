# -*- coding: utf-8 -*-
import json, os

paths = [
    'data/processed/scene_graph_v2.json',
    'data/processed/scene_graph_training_clean.json',
    'data/processed/cleaned/scene_graph_clean.json',
    'data/processed/scene_graph_training.json',
]
for p in paths:
    fp = os.path.join('C:', 'Users', 'Administrator', '.qclaw', 'workspace', 'projects', 'building-physical-ai', p.replace('/', os.sep))
    if os.path.exists(fp):
        try:
            with open(fp, 'r', encoding='utf-8-sig') as f:
                d = json.load(f)
            print(f'OK {p}: nodes={d.get("num_nodes")}, features={d.get("num_features")}, positions={len(d.get("node_positions",[]))}')
            if d.get('node_positions'):
                print(f'   first pos: {d["node_positions"][0]}')
        except Exception as e:
            print(f'ERR {p}: {e}')
    else:
        print(f'MISSING {p}')