"""
从VR页面批量提取元数据
使用web_fetch获取页面标题等信息
"""
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

# 加载链接数据
with open(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_links_new.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

links = data['links']

# 清理函数
def clean_company_info(text):
    if not text:
        return ""
    result = text
    result = re.sub(r'1[3-9]\d{9}', '', result)
    result = re.sub(r'杭州鑫满天装饰', '', result)
    result = re.sub(r'DESIGN\s*by\s*\w+', '', result)
    result = re.sub(r'技术支持[：:]?\s*建E网', '', result)
    result = re.sub(r'效果图小凯', '', result)
    result = re.sub(r'建E网', '', result)
    result = re.sub(r'\s+', ' ', result).strip()
    return result

# 从3d66 URL推断项目信息
def parse_3d66_url(url):
    """尝试从3d66页面获取信息"""
    # 3d66 VR链接通常包含项目ID
    id_match = re.search(r'index_detail_(\d+)', url)
    vr_id = id_match.group(1) if id_match else None
    return vr_id

# 建筑类型推断关键词
RESIDENTIAL_KEYWORDS = ['庐', '府', '苑', '园', '居', '庭', '寓', '舍', '邸', '阁', '轩', '院', '家', '城', '湾', '畔', '郡']
COMMERCIAL_KEYWORDS = ['办公', '酒店', '会所', '展厅', '商业']
VILLA_KEYWORDS = ['别墅', '山庄', '庄园']

def guess_building_type(title):
    """从标题推断建筑类型"""
    if not title:
        return 'unknown'
    for kw in VILLA_KEYWORDS:
        if kw in title:
            return 'villa'
    for kw in COMMERCIAL_KEYWORDS:
        if kw in title:
            return 'commercial'
    for kw in RESIDENTIAL_KEYWORDS:
        if kw in title:
            return 'residential'
    # 含数字+楼层号的通常是住宅
    if re.search(r'\d+-\d+', title):
        return 'residential'
    return 'unknown'

# 房间类型
ROOM_TYPES = {
    '客厅': 'living_room',
    '餐厅': 'dining_room',
    '主卧': 'master_bedroom',
    '次卧': 'secondary_bedroom',
    '书房': 'study',
    '厨房': 'kitchen',
    '卫生间': 'bathroom',
    '阳台': 'balcony',
    '玄关': 'entrance',
    '儿童房': 'kids_room',
    '衣帽间': 'cloakroom',
    '储物间': 'storage',
    '电视背景': 'tv_wall',
    '沙发床': 'sofa_bed',
    '餐边柜': 'sideboard',
    '鞋柜': 'shoe_cabinet',
    '过道': 'hallway',
    '楼梯': 'staircase',
    '茶室': 'tea_room',
    '影音室': 'media_room',
    '健身房': 'gym',
    '车库': 'garage',
    '花园': 'garden',
    '露台': 'terrace',
    '门厅': 'lobby',
    '休闲区': 'leisure_area',
}

# 构建结构化数据
structured_data = []
for link in links:
    entry = {
        "id": f"vr-new-{link['index']:03d}",
        "original_index": link['index'],
        "url": link['url'],
        "platform": link['platform'],
        "platform_id": link['platform_id'],
        "title": None,
        "title_clean": None,
        "building_type": "unknown",
        "rooms": [],
        "designer_raw": None,
        "designer_clean": None,
        "views": None,
        "screenshot_path": None,
        "mirrored": False,
    }
    structured_data.append(entry)

# 统计
print(f"总链接数: {len(structured_data)}")
platforms = Counter(l['platform'] for l in links)
print(f"平台分布: {dict(platforms)}")

# 保存结构化数据
output_path = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_links_structured.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(structured_data, f, ensure_ascii=False, indent=2)

print(f"结构化模板已保存: {output_path}")
print("等待浏览器扫描填充详细信息...")
