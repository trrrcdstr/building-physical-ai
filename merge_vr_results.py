"""
整合VR扫描结果到数据模型
"""
import json
from pathlib import Path

# 读取扫描结果
scanned = []
scanned_path = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_scanned_results.json')
if scanned_path.exists():
    with open(scanned_path, 'r', encoding='utf-8') as f:
        scanned = json.load(f)

# 读取原始链接
links_path = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_links_new.json')
with open(links_path, 'r', encoding='utf-8') as f:
    links_data = json.load(f)
original_links = {l['url']: l for l in links_data['links']}

print(f"原始链接: {len(original_links)}")
print(f"已扫描: {len(scanned)}")

# 创建扫描结果字典
scanned_by_url = {r['url']: r for r in scanned}

# 构建完整结构
def clean_value(val):
    """清洗公司名和电话"""
    import re
    if not val or not isinstance(val, str):
        return val
    # 电话号码
    val = re.sub(r'1[3-9]\d{9}', '', val)
    # 公司名
    val = re.sub(r'杭州鑫满天装饰', '', val)
    val = re.sub(r'DESIGN by \w+', '', val)
    val = re.sub(r'技术支持[：:]\s*建E网', '', val)
    val = re.sub(r'建E网', '', val)
    val = re.sub(r'效果图小凯', '', val)
    val = re.sub(r'\s+', ' ', val).strip()
    return val if val else None

# 合并数据
all_vr_data = []
for url, orig in original_links.items():
    scanned_entry = scanned_by_url.get(url, {})
    
    title_raw = scanned_entry.get('title') or orig.get('title')
    title_clean = clean_value(title_raw) if title_raw else None
    
    designer_raw = scanned_entry.get('designer_raw')
    designer_clean = clean_value(designer_raw) if designer_raw else None
    
    rooms = scanned_entry.get('rooms', [])
    
    all_vr_data.append({
        "id": f"vr-new-{orig['index']:03d}",
        "original_index": orig['index'],
        "url": url,
        "platform": orig['platform'],
        "platform_id": orig['platform_id'],
        "title_raw": title_raw,
        "title_clean": title_clean,
        "designer_raw": designer_raw,
        "designer_clean": designer_clean,
        "rooms": rooms,
        "room_types": [normalize_room(r) for r in rooms],
        "views": scanned_entry.get('views'),
        "has_rooms": len(rooms) > 0,
    })

# 房间标准化映射
ROOM_MAP = {
    '客厅': 'living_room',
    '餐厅': 'dining_room',
    '主卧': 'master_bedroom',
    '次卧': 'secondary_bedroom',
    '书房': 'study',
    '厨房': 'kitchen',
    '卫生间': 'bathroom',
    '主卫': 'master_bath',
    '次卫': 'secondary_bath',
    '阳台': 'balcony',
    '玄关': 'entrance',
    '儿童房': 'kids_room',
    '衣帽间': 'cloakroom',
    '地下室客厅': 'basement_living',
    '地下室茶室': 'basement_tea_room',
    '地下室乒乓球室': 'basement_pingpong',
    '地下室棋牌室': 'basement_game_room',
    '地下室影音室': 'basement_cinema',
    '地下室瑜伽室': 'basement_yoga',
    '一楼餐厅': 'first_floor_dining',
    '一楼岛台': 'island_counter',
    '二楼主卧': 'second_floor_master',
    '二楼次卧': 'second_floor_secondary',
    '负一茶室': 'b1_tea_room',
    '负一休闲区': 'b1_leisure',
    '棋牌区': 'game_area',
    '沙发床': 'sofa_bed',
    '电视背景': 'tv_wall',
    '餐边柜': 'sideboard',
    '鞋柜静帧': 'shoe_cabinet',
    '客厅看阳台': 'living_to_balcony',
    '客厅': 'living_room',
}

def normalize_room(room):
    return ROOM_MAP.get(room, room)

# 保存完整数据
output_path = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_complete_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_vr_data, f, ensure_ascii=False, indent=2)

print(f"\n完整数据已保存: {output_path}")
print(f"总VR数: {len(all_vr_data)}")

# 统计
from collections import Counter
platforms = Counter(v['platform'] for v in all_vr_data)
has_rooms = sum(1 for v in all_vr_data if v['has_rooms'])
total_rooms = sum(len(v['rooms']) for v in all_vr_data)
total_views = sum(v['views'] or 0 for v in all_vr_data)

print(f"\n统计:")
print(f"  平台分布: {dict(platforms)}")
print(f"  有房间信息: {has_rooms}/{len(all_vr_data)}")
print(f"  总房间数: {total_rooms}")
print(f"  总浏览量: {total_views}")

# 房间类型统计
all_room_types = []
for v in all_vr_data:
    all_room_types.extend(v['rooms'])
room_counts = Counter(all_room_types)
print(f"\n房间类型 Top10:")
for room, count in room_counts.most_common(10):
    print(f"  {room}: {count}")
