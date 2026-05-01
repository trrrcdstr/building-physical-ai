import json
with open('knowledge/VR_KNOWLEDGE.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rooms = {}
for vr in data.get('records', []):
    for r in vr.get('rooms', []):
        room_type = r.get('room_type', 'unknown')
        rooms[room_type] = rooms.get(room_type, 0) + 1

print(f'Total room records: {sum(rooms.values())}')
for r, c in sorted(rooms.items(), key=lambda x: -x[1])[:10]:
    print(f'{r}: {c}')