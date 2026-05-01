import json, os
from collections import Counter

with open('knowledge/RENDERING_DATABASE.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

seen = set()
unique = []
for r in data['records']:
    if r['id'] not in seen:
        seen.add(r['id'])
        unique.append(r)

print(f'Before: {len(data["records"])}, After: {len(unique)}')

data['records'] = unique
data['meta']['total_images'] = len(unique)

with open('knowledge/RENDERING_DATABASE.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'File size: {os.path.getsize("knowledge/RENDERING_DATABASE.json")/1024:.1f} KB')

cats = Counter(r['category'] for r in unique)
subs = Counter(r['subcategory'] for r in unique)
print('\n[Category]')
for c,n in cats.most_common(): print(f'  {c}: {n}')
print('\n[Subcategory]')
for s,n in subs.most_common(): print(f'  {s}: {n}')
