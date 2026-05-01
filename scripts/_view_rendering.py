import json
with open('knowledge/RENDERING_DATABASE.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total: {len(data['records'])} records")

rec = data['records'][0]
print("\nFields:", list(rec.keys()))
print("\nSample record:")
for k, v in rec.items():
    print(f"  {k}: {v}")

print("\n\nLast record:")
last = data['records'][-1]
for k, v in last.items():
    print(f"  {k}: {v}")
