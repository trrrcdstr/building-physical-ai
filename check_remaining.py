# -*- coding: utf-8 -*-
import json
data = json.load(open('C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/data/processed/vr_remaining.json', encoding='utf-8'))
print(f'Remaining: {len(data)}')
for l in data:
    print(f"Index {l['index']:3d} | {l['platform']:10} | {l['url']}")
