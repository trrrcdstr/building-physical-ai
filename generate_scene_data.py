"""
建筑物理AI世界模型 - 场景数据生成器
从VR知识库自动生成分类场景数据
"""
import json
import os

with open('knowledge/VR_KNOWLEDGE.json', 'r', encoding='utf-8') as f:
    vr_kb = json.load(f)

with open('data/processed/world_model_input.json', 'r', encoding='utf-8') as f:
    vr_list = json.load(f)

# 场景分类规则
SCENE_TAGS = {
    'residence': ['客厅', '餐厅', '厨房', '主卧', '次卧', '书房', '影音室', '茶室', '棋牌室', '健身房', '衣帽间', '主卫', '次卫'],
    'mall': ['商铺', '餐饮', '中庭', '电梯厅', '卫生间', '走廊', '儿童区'],
    'office': ['办公区', '会议室', '茶水间', '卫生间', '走廊', '电梯厅', '前台'],
    'hotel': ['大堂', '餐厅', '客房', '健身房', '泳池', '会议室', '走廊', '卫生间'],
    'villa_garden': ['花园', '庭院', '泳池', '硬化铺装', '凉亭', '草坪'],
    'park': ['绿化', '步道', '广场', '游乐设施', '草坪', '水景'],
    'office_building': ['标准层', '地下车库', '设备层', '电梯厅', '卫生间', '走廊'],
    'residential': ['楼栋', '园林', '会所', '地下车库', '大堂', '电梯厅'],
    'commercial_complex': ['商铺', '餐饮', '办公', '酒店', '地下车库', '中庭', '大堂'],
}

# 房间颜色
ROOM_COLORS = {
    '客厅': '#E8D5B7', '餐厅': '#D4C4A8', '厨房': '#C8B89A',
    '主卧': '#B8C8D8', '次卧': '#C0C0C0', '儿童房': '#FFE4B5',
    '卫生间': '#B0D0D0', '玄关': '#D0C0B0', '阳台': '#A0B090',
    '书房': '#D8D0C0', '衣帽间': '#D8C8B8', '影音室': '#A0A0B8',
    '棋牌室': '#C8B8A0', '健身房': '#B8C0B0', '茶室': '#C8D0B8',
    '主卫': '#A8D8D8', '次卫': '#B0E0E0', '走廊': '#D0C8B8',
    '花园': '#90B870', '庭院': '#A0C080', '泳池': '#60A0D0',
    '地下车库': '#607D8B', '商铺': '#F0E8D8', '办公区': '#E0E8F0',
    '其他': '#CCCCCC',
}

def get_scene_type(room_category):
    """根据房间类别推断场景类型"""
    for scene, tags in SCENE_TAGS.items():
        if room_category in tags:
            return scene
    return 'residence'  # 默认家庭场景

def gen_objects(vr_entry):
    """为单个VR条目生成3D对象列表"""
    objects = []
    vr_id = vr_entry['vr_id']
    platform = vr_entry['platform']
    designer = vr_entry['designer']
    rooms = vr_entry.get('rooms', [])
    room_cats = vr_entry.get('room_categories', [])
    physics_tags = vr_entry.get('physics_tags', [])
    
    for i, (room, cat) in enumerate(zip(rooms, room_cats)):
        scene_type = get_scene_type(cat)
        color = ROOM_COLORS.get(cat, '#CCCCCC')
        
        # 生成随机但一致的位置
        import hashlib
        seed = hashlib.md5(f'{vr_id}-{i}'.encode()).hexdigest()
        x = (int(seed[:4], 16) % 40) - 20
        z = (int(seed[4:8], 16) % 40) - 20
        w = 3 + (int(seed[8:10], 16) % 3)
        d = 4 + (int(seed[10:12], 16) % 3)
        
        obj = {
            'id': f'vr{vr_id}-room{i}',
            'name': f'{room}-VR{vr_id}',
            'type': 'floor',
            'position': [float(x), 0, float(z)],
            'rotation': [0, 0, 0],
            'dimensions': {'width': float(w), 'height': 0.2, 'depth': float(d)},
            'physics': {
                'mass': 0,
                'material': cat,
                'friction': 0.5,
                'isStructural': True,
            },
            'robot': {
                'graspable': False,
                'openable': False,
                'pathObstacle': True,
                'pushable': False,
                'climbable': '楼梯' in cat or '台阶' in cat,
            },
            'vrData': {
                'vr_id': vr_id,
                'platform': platform,
                'designer': designer,
                'room_name': room,
                'room_category': cat,
                'physics_tags': [t for t in physics_tags if t in cat or i < len(physics_tags)],
            },
            'sceneCategory': 'interior' if scene_type in ['residence', 'mall', 'office', 'hotel'] else 'landscape' if scene_type in ['villa_garden', 'park'] else 'architecture',
            'sceneType': scene_type,
        }
        objects.append(obj)
    
    return objects

# 生成所有场景
all_objects = []
for vr in vr_list:
    all_objects.extend(gen_objects(vr))

print(f'Generated {len(all_objects)} objects from {len(vr_list)} VR entries')

# 按场景类型分组
scenes = {k: [] for k in SCENE_TAGS.keys()}
for obj in all_objects:
    st = obj['sceneType']
    if st in scenes:
        scenes[st].append(obj)

# 输出统计
for scene, objs in scenes.items():
    if objs:
        print(f'  {scene}: {len(objs)} rooms')

# 生成TypeScript文件
ts_output = f"""// Auto-generated scene data - 2026-04-10
// Total: {len(all_objects)} objects from {len(vr_list)} VR entries

export const worldObjects = {json.dumps(all_objects, ensure_ascii=False, indent=2)} as const

export const sceneData = {{
"""

for scene, objs in scenes.items():
    if objs:
        ts_output += f"  '{scene}': {json.dumps(objs, ensure_ascii=False, indent=4)},\n"

ts_output += """} as const

export const sceneStats = {
  totalVR: """ + str(len(vr_list)) + """,
  totalObjects: """ + str(len(all_objects)) + """,
  byScene: {"""
for scene, objs in scenes.items():
    if objs:
        ts_output += f"\n    '{scene}': {len(objs)},"
ts_output += """
  },
}
"""

with open('web-app/src/data/sceneData.ts', 'w', encoding='utf-8') as f:
    f.write(ts_output)

print('\nGenerated: web-app/src/data/sceneData.ts')

# 生成CAD底层数据库
cad_meta = {
    'project': '南沙星河东悦湾',
    'location': '广州南沙',
    'total_files': 17,
    'total_size_mb': 73,
    'disciplines': {
        '建筑': {'count': 5, 'files': ['地块三地下室建筑底图.dwg']},
        '电气': {'count': 5, 'files': ['电施_车库.dwg', '弱电.dwg', '照明.dwg']},
        '给排水': {'count': 4, 'files': ['地块三地下室水图.dwg']},
        '暖通': {'count': 3, 'files': ['地块三地下室通风图.dwg']},
    },
    'floor': '地块三地下室',
    'note': 'DWG文件为R2004二进制格式，需要AutoCAD或LibreCAD导出为DXF后解析',
    'parsed_entities': 0,  # 待解析
    'room_count': 50,  # 停车位
}

with open('knowledge/CAD_DATABASE.json', 'w', encoding='utf-8') as f:
    json.dump(cad_meta, f, ensure_ascii=False, indent=2)

print('Generated: knowledge/CAD_DATABASE.json')
print('\nDone!')
