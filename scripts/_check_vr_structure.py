import json
with open('knowledge/VR_KNOWLEDGE.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'Top keys: {list(data.keys())[:10]}')
for k, v in list(data.items())[:3]:
    t = type(v).__name__
    sz = len(v) if isinstance(v, (list, dict)) else str(v)[:30]
    print(f'  {k}: {t} ({sz})')
