# -*- coding: utf-8 -*-
import json
from collections import Counter

data = json.load(open('C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/data/processed/vr_scanned_results.json', encoding='utf-8'))

print('=== VR扫描数据分析 ===')
print(f'总扫描: {len(data)} 个VR')
print()

platforms = Counter(x['platform'] for x in data)
print('平台分布:')
for p, c in platforms.most_common():
    print(f'  {p}: {c}')

print()
print(f'总浏览量: {sum(x["views"] for x in data):,}')
with_rooms = sum(1 for x in data if x.get('rooms'))
print(f'提取到房间信息: {with_rooms}/{len(data)}')

print()
designers = Counter()
for item in data:
    raw = item.get('designer_raw') or '未知'
    d = raw.replace('DESIGN by Sy','').replace('18767151413','').replace('：18767151413','').strip(' :')
    designers[d] += 1
print('设计师分布:')
for d, c in designers.most_common(5):
    print(f'  {d}: {c}')

print()
all_rooms = []
for item in data:
    for r in item['rooms']:
        all_rooms.append(r)
rc = Counter(all_rooms)
print(f'房间类型 (共{len(rc)}种, {len(all_rooms)}个标签):')
for r, c in rc.most_common(15):
    print(f'  {r}: {c}')

print()
top5 = sorted(data, key=lambda x: x['views'], reverse=True)[:5]
print('TOP5浏览量:')
for i, item in enumerate(top5, 1):
    title = item.get('title') or item['url']
    print(f'  {i}. {title} | {item["platform"]} | {item["views"]:,} views | {len(item["rooms"])} rooms')
