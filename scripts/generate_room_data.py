"""
房间数据生成器
从VR知识库和建筑对象中提取房间信息，构建拓扑关系
"""
import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
DATA_DIR = BASE_DIR / "data" / "processed"

print("=" * 60)
print("房间数据生成器")
print("=" * 60)

# 1. 加载VR知识库
with open(KNOWLEDGE_DIR / "VR_KNOWLEDGE.json", 'r', encoding='utf-8') as f:
    vr_data = json.load(f)

rooms_info = vr_data.get('rooms', {})
raw_vr = vr_data.get('raw_vr', [])

print(f"\n[VR知识库]")
print(f"  房间类型: {len(rooms_info)}")
print(f"  VR条目: {len(raw_vr)}")

# 2. 提取房间类型统计
room_stats = {}
for room_type, info in rooms_info.items():
    if isinstance(info, dict):
        room_stats[room_type] = info.get('count', 0)
    else:
        room_stats[room_type] = 0

print(f"\n[房间类型统计]")
for rt, cnt in sorted(room_stats.items(), key=lambda x: -x[1]):
    print(f"  {rt}: {cnt}")

# 3. 加载建筑对象
with open(DATA_DIR / "building_objects.json", 'r', encoding='utf-8') as f:
    obj_data = json.load(f)

# 处理数据格式
if isinstance(obj_data, dict) and 'nodes' in obj_data:
    objects = obj_data['nodes']
    if isinstance(objects, dict):
        objects = list(objects.values())
else:
    objects = obj_data if isinstance(obj_data, list) else []

print(f"\n[建筑对象]")
print(f"  对象数量: {len(objects)}")

# 统计类型
type_stats = defaultdict(int)
for obj in objects:
    t = obj.get('type', 'unknown')
    type_stats[t] += 1

for t, cnt in sorted(type_stats.items(), key=lambda x: -x[1]):
    print(f"  {t}: {cnt}")

# 4. 生成虚拟房间划分
# 基于门窗位置，按X坐标分组创建虚拟房间
print(f"\n[生成虚拟房间]")

# 按X坐标分组
x_positions = defaultdict(list)
for obj in objects:
    pos = obj.get('position', [0, 0, 0])
    if isinstance(pos, list) and len(pos) >= 1:
        x = pos[0]
    elif isinstance(pos, dict):
        x = pos.get('x', 0)
    else:
        x = 0
    x_positions[int(x // 50)].append(obj)  # 每50m一个房间

virtual_rooms = []
for group_id, objs in sorted(x_positions.items()):
    x_coords = []
    for o in objs:
        pos = o.get('position', [0, 0, 0])
        if isinstance(pos, list) and len(pos) >= 1:
            x_coords.append(pos[0])
        elif isinstance(pos, dict):
            x_coords.append(pos.get('x', 0))
    x_min = min(x_coords) if x_coords else 0
    x_max = max(x_coords) if x_coords else 0

    doors = [o for o in objs if o.get('type') == 'door']
    windows = [o for o in objs if o.get('type') == 'window']

    room = {
        'id': f"room_{group_id:02d}",
        'name': f"区域{group_id + 1}",
        'type': 'residential',  # 默认类型
        'bounds': {
            'x_min': x_min,
            'x_max': x_max,
            'y_min': -1.0,
            'y_max': 5.0,
            'z_min': -3.0,
            'z_max': 0.0
        },
        'doors': [o['id'] for o in doors],
        'windows': [o['id'] for o in windows],
        'door_count': len(doors),
        'window_count': len(windows),
        'area_estimate': (x_max - x_min) * 6.0,  # 假设宽度6m
    }
    virtual_rooms.append(room)

print(f"  生成虚拟房间: {len(virtual_rooms)}")
for room in virtual_rooms[:5]:
    print(f"    {room['id']}: {room['door_count']}门 + {room['window_count']}窗, 面积约{room['area_estimate']:.0f}m2")

# 5. 生成拓扑关系（邻接）
print(f"\n[生成拓扑关系]")

edges = []
for i in range(len(virtual_rooms) - 1):
    room1 = virtual_rooms[i]
    room2 = virtual_rooms[i + 1]

    # 相邻房间通过门连接
    edge = {
        'source': room1['id'],
        'target': room2['id'],
        'relation': 'adjacent',
        'connection_type': 'door',
        'distance': room2['bounds']['x_min'] - room1['bounds']['x_max'],
    }
    edges.append(edge)

print(f"  邻接边: {len(edges)}")

# 6. 保存结果
output = {
    'meta': {
        'generated_at': '2026-04-21',
        'source': 'VR_KNOWLEDGE + building_objects',
        'room_count': len(virtual_rooms),
        'edge_count': len(edges),
    },
    'rooms': virtual_rooms,
    'edges': edges,
    'room_stats': room_stats,
}

out_file = DATA_DIR / "spatial_rooms.json"
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n[保存]")
print(f"  {out_file} ({out_file.stat().st_size / 1024:.1f} KB)")

# 7. 生成技能可用的房间索引
room_index = {}
for room in virtual_rooms:
    room_index[room['id']] = {
        'name': room['name'],
        'type': room['type'],
        'area': room['area_estimate'],
        'doors': room['door_count'],
        'windows': room['window_count'],
    }

index_file = DATA_DIR / "room_index.json"
with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(room_index, f, ensure_ascii=False, indent=2)

print(f"  {index_file} ({index_file.stat().st_size / 1024:.1f} KB)")

print("\n[完成]")
