import json
with open('knowledge/RENDERING_DATABASE.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total: {len(data['records'])} records\n")

# Scene distribution
scenes = {}
for r in data['records']:
    s = r.get('scene', 'unknown')
    scenes[s] = scenes.get(s, 0) + 1

print("Scene distribution:")
for s, c in sorted(scenes.items(), key=lambda x: -x[1])[:10]:
    print(f"  {s}: {c}")

# Sample records
print("\nSample records:")
for r in data['records'][:3]:
    print(f"  - {r.get('scene_label')}: {r.get('subcategory')} / {r.get('filename')[:30]}")
