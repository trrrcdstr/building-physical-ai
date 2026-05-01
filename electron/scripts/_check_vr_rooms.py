import json
with open('knowledge/VR_KNOWLEDGE.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rooms = data.get('rooms', {})
print(f'Room types: {len(rooms)}')
print()
for room_type, count in rooms.items():
    print(f'  {room_type}: {count}')

# 检查raw_vr中的VR记录
raw_vr = data.get('raw_vr', [])
print(f'\nTotal raw_vr entries: {len(raw_vr) if isinstance(raw_vr, list) else "N/A"}')
if isinstance(raw_vr, list) and raw_vr:
    print(f'Sample VR keys: {list(raw_vr[0].keys())[:5]}')
