import json
from collections import Counter

try:
    with open(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_scanned_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    print(f'已扫描: {len(results)} 个VR')
    print()
    platforms = Counter(r['platform'] for r in results)
    total_views = sum(r.get('views', 0) for r in results)
    rooms_found = sum(len(r.get('rooms', [])) for r in results)
    print(f'平台: {dict(platforms)}')
    print(f'总浏览量: {total_views}')
    print(f'识别房间数: {rooms_found}')
    print()
    print('样本:')
    for r in results[:8]:
        title = r.get('title') or 'N/A'
        rooms = r.get('rooms', [])
        print(f"  [{r['index']}] {title} | {r['platform']} | {len(rooms)} rooms | {r.get('views', 0)} views")
except Exception as e:
    print(f'Error: {e}')
