import json
from pathlib import Path

# 读取VR知识库
vr_file = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\VR_KNOWLEDGE.json")
with open(vr_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total VRs: {len(data.get('records', []))}")

# 分析结构
if data.get('records'):
    sample = data['records'][0]
    print(f"\nSample VR keys: {list(sample.keys())}")

    # 检查rooms字段
    if 'rooms' in sample:
        print(f"\nRooms in sample: {sample['rooms']}")

    # 统计有房间信息的VR数量
    with_rooms = sum(1 for vr in data['records'] if vr.get('rooms'))
    print(f"\nVRs with room info: {with_rooms}")

    # 统计房间类型
    all_rooms = {}
    for vr in data['records']:
        for r in vr.get('rooms', []):
            if isinstance(r, dict):
                rt = r.get('room_type', 'unknown')
            else:
                rt = str(r)
            all_rooms[rt] = all_rooms.get(rt, 0) + 1

    print(f"\nRoom types found: {len(all_rooms)}")
    for rt, cnt in sorted(all_rooms.items(), key=lambda x: -x[1])[:10]:
        print(f"  {rt}: {cnt}")
