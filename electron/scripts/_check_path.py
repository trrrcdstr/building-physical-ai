import json
with open('knowledge/RENDERING_DATABASE.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Print first 3 records' paths
for r in db['records'][:3]:
    print(repr(r['path']))
    print(f"  -> decoded: {r['path'].replace('file://', '').replace('/', '\\\\')}")
