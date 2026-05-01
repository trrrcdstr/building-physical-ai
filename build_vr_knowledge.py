# -*- coding: utf-8 -*-
"""
VR数据 → 知识库
目标：清洗、去重、分层组织，构建可搜索的建筑空间知识库
"""
import json
import re
import os
from collections import defaultdict

BASE = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai'
IN_FILE = os.path.join(BASE, 'data', 'processed', 'vr_scanned_results.json')
OUT_DIR = os.path.join(BASE, 'knowledge')
os.makedirs(OUT_DIR, exist_ok=True)

with open(IN_FILE, 'r', encoding='utf-8') as f:
    vr_list = json.load(f)

print(f"加载 {len(vr_list)} 条VR记录")

# ─────────────────────────────────────────
# 1. 数据清洗
# ─────────────────────────────────────────
PHONE_RE = re.compile(r'1[3-9]\d{9}')
COMPANY_RE = re.compile(r'(设计|装饰|建筑|工程|装修|家居|软装|全屋|定制|整装)\s*公司')

def clean_designer(raw):
    """去除手机号和公司名，保留设计师/品牌名"""
    if not raw:
        return None
    # 去除手机号
    cleaned = PHONE_RE.sub('', raw)
    # 去除公司名
    cleaned = COMPANY_RE.sub('', cleaned)
    # 去除多余符号
    cleaned = re.sub(r'[\[\]（）\(\)【】""'']', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    # 去除末尾的逗号、连字符
    cleaned = cleaned.strip(' ,，-–—.')
    return cleaned if cleaned else None

def clean_title(raw):
    """清洗标题"""
    if not raw:
        return None
    # 去除异常后缀（0、数字序列）
    cleaned = re.sub(r'[0-9]+$', '', raw)
    cleaned = re.sub(r'0异常$', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else None

# 清洗所有记录
for v in vr_list:
    v['designer_clean'] = clean_designer(v.get('designer_raw', ''))
    v['title_clean'] = clean_title(v.get('title', ''))
    v['rooms_clean'] = [r.replace('0异常', '').replace('异常', '').strip()
                         for r in v.get('rooms', []) if r.strip()]

# ─────────────────────────────────────────
# 2. 统计分析
# ─────────────────────────────────────────
print("\n=== 数据统计 ===")

# 房间类型统计
room_counter = defaultdict(int)
for v in vr_list:
    for r in v.get('rooms_clean', []):
        room_counter[r] += 1

print(f"\n房间类型分布 (Top 20):")
for rm, cnt in sorted(room_counter.items(), key=lambda x: -x[1])[:20]:
    print(f"  {rm}: {cnt}")

# 设计师统计
designer_counter = defaultdict(int)
for v in vr_list:
    d = v.get('designer_clean')
    if d:
        designer_counter[d] += 1

print(f"\n设计师/品牌分布 (Top 10):")
for d, cnt in sorted(designer_counter.items(), key=lambda x: -x[1])[:10]:
    print(f"  {d}: {cnt}")

# 平台统计
platform_counter = defaultdict(int)
for v in vr_list:
    platform_counter[v['platform']] += 1
print(f"\n平台分布:")
for p, cnt in sorted(platform_counter.items(), key=lambda x: -x[1]):
    print(f"  {p}: {cnt}")

# ─────────────────────────────────────────
# 3. 构建知识库文件
# ─────────────────────────────────────────

# 3a. 房间类型知识库
ROOM_CATEGORIES = {
    "客厅": ["客厅", "横厅", "竖厅", "大客厅", "挑高客厅", "阳光客厅"],
    "餐厅": ["餐厅", "中西厨", "开放式厨房", "岛台", "餐厨一体"],
    "厨房": ["厨房", "中厨", "西厨", "开放式厨房", "岛台", "餐厨一体"],
    "主卧": ["主卧", "主人房", "主卧室", "套房主卧"],
    "次卧": ["次卧", "次卧2", "卧室2", "客卧", "客房", "书房"],
    "儿童房": ["儿童房", "小孩房", "儿童房2"],
    "卫生间": ["卫生间", "公卫", "主卫", "马桶间", "浴室", "洗手间", "卫浴"],
    "玄关": ["玄关", "入户", "门厅", "鞋柜"],
    "阳台": ["阳台", "景观阳台", "生活阳台", "观景阳台", "露台"],
    "书房": ["书房", "多功能房", "茶室", "棋牌室"],
    "储藏": ["储藏室", "杂物间", "衣帽间", "家政间"],
    "设备": ["设备间", "洗衣间", "家政间"],
    "楼梯": ["楼梯", "电梯", "步梯"],
}

def categorize_room(room):
    for cat, keywords in ROOM_CATEGORIES.items():
        for kw in keywords:
            if kw in room:
                return cat
    return "其他"

room_kb = {}
for v in vr_list:
    for r in v.get('rooms_clean', []):
        cat = categorize_room(r)
        if cat not in room_kb:
            room_kb[cat] = []
        room_kb[cat].append({
            "original_name": r,
            "index": v['index'],
            "platform": v['platform'],
            "designer": v.get('designer_clean'),
            "title": v.get('title_clean'),
        })

# 去重（同index同房间只保留一条）
for cat in room_kb:
    seen = set()
    unique = []
    for item in room_kb[cat]:
        key = (item['index'], item['original_name'])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    room_kb[cat] = unique

print(f"\n房间分类:")
for cat, items in sorted(room_kb.items(), key=lambda x: -len(x[1])):
    print(f"  {cat}: {len(items)}个VR场景")

# ─────────────────────────────────────────
# 4. 输出知识库文件
# ─────────────────────────────────────────

# 4a. 主知识库 JSON
knowledge_base = {
    "meta": {
        "source": "VR效果图扫描",
        "total_vr": len(vr_list),
        "total_with_rooms": sum(1 for v in vr_list if v.get('rooms_clean')),
        "platforms": dict(platform_counter),
        "generated": "2026-04-10",
        "note": "房间浏览量因平台JS限制无法抓取，数据完整度约70%"
    },
    "rooms": {cat: {"count": len(items), "samples": items[:10]}
              for cat, items in room_kb.items()},
    "designers": [{"name": d, "vr_count": c}
                  for d, c in sorted(designer_counter.items(), key=lambda x: -x[1])],
    "raw_vr": vr_list  # 清洗后的原始数据
}

out_path = os.path.join(OUT_DIR, 'VR_KNOWLEDGE.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
print(f"\n知识库已保存: {out_path}")

# 4b. 机器人家居交互场景（从VR数据提取）
SCENE_TEMPLATES = {
    "玄关": {
        "robot_task": "入户识别+鞋柜操作",
        "typical_objects": ["玄关柜", "鞋柜", "穿衣镜", "入户门", "开关"],
        "physics_notes": ["鞋柜门铰链力矩<3Nm", "穿衣镜高度1.4-1.8m适合机器人视觉定位"],
        "common_vr_names": list(set([r for v in vr_list for r in v.get('rooms_clean', [])
                                      if '玄关' in r or '入户' in r][:50]))
    },
    "客厅": {
        "robot_task": "导航+物品操作+开关控制",
        "typical_objects": ["沙发", "茶几", "电视柜", "窗帘", "主灯开关", "插座"],
        "physics_notes": ["沙发柔软抓取难度高", "茶几高度0.4-0.5m", "开关高度1.3m"],
        "common_vr_names": list(set([r for v in vr_list for r in v.get('rooms_clean', [])
                                      if '客厅' in r or '横厅' in r or '竖厅' in r][:50]))
    },
    "厨房": {
        "robot_task": "炊具操作+水槽清洁+碗碟抓取",
        "typical_objects": ["灶台", "油烟机", "水槽", "橱柜", "冰箱", "调料架"],
        "physics_notes": ["水槽深度200mm", "灶台高度0.8-0.85m", "碗碟质量100-500g", "水压0.3MPa"],
        "common_vr_names": list(set([r for v in vr_list for r in v.get('rooms_clean', [])
                                      if '厨房' in r or '岛台' in r or '餐厨' in r][:50]))
    },
    "主卧": {
        "robot_task": "床品整理+衣柜操作+窗帘控制",
        "typical_objects": ["床", "衣柜", "床头柜", "窗帘", "主卫门"],
        "physics_notes": ["床品柔软变形", "衣柜门铰链力矩<2Nm", "被子折叠难度高"],
        "common_vr_names": list(set([r for v in vr_list for r in v.get('rooms_clean', [])
                                      if '主卧' in r or '卧室1' in r][:50]))
    },
    "卫生间": {
        "robot_task": "洗漱+马桶操作+镜柜开启",
        "typical_objects": ["马桶", "洗手台", "浴室柜", "淋浴房", "毛巾架", "镜柜"],
        "physics_notes": ["马桶盖重量3-5kg", "洗手台高度0.8m", "镜柜铰链<2Nm"],
        "common_vr_names": list(set([r for v in vr_list for r in v.get('rooms_clean', [])
                                      if '卫生间' in r or '洗手间' in r or '浴室' in r][:50]))
    },
}

scene_out = os.path.join(OUT_DIR, 'ROBOT_SCENES.md')
with open(scene_out, 'w', encoding='utf-8') as f:
    f.write("# 机器人家居交互场景知识库\n\n")
    f.write(f"_从 {len(vr_list)} 个VR全景场景自动提取 · 生成时间: 2026-04-10_\n\n")
    
    for cat, info in SCENE_TEMPLATES.items():
        f.write(f"## {cat}\n\n")
        f.write(f"**典型任务**: {info['robot_task']}\n\n")
        f.write(f"**常见物体**:\n")
        for obj in info['typical_objects']:
            f.write(f"- {obj}\n")
        f.write(f"\n**物理特性笔记**:\n")
        for note in info['physics_notes']:
            f.write(f"- {note}\n")
        f.write(f"\n**VR场景样本** ({len(info['common_vr_names'])}个):\n")
        for name in info['common_vr_names'][:8]:
            f.write(f"- {name}\n")
        f.write(f"\n---\n\n")

print(f"场景知识库已保存: {scene_out}")

# 4c. 世界模型输入数据
world_model_input = []
for v in vr_list:
    rooms = v.get('rooms_clean', [])
    if not rooms:
        continue
    world_model_input.append({
        "vr_id": v['index'],
        "platform": v['platform'],
        "title": v.get('title_clean') or v.get('title'),
        "designer": v.get('designer_clean'),
        "rooms": rooms,
        "room_count": len(rooms),
        "physics_tags": []
    })

# 自动打物理标签
PHYSICS_TAGS = {
    "玄关": ["入户", "地面高差", "狭窄通道"],
    "厨房": ["水槽", "燃气灶", "高温", "刀具"],
    "卫生间": ["防水", "潮湿", "水渍", "滑倒风险"],
    "阳台": ["户外", "风雨", "晾晒"],
    "楼梯": ["高差", "踏步", "坠落风险"],
}

for entry in world_model_input:
    tags = set()
    for r in entry['rooms']:
        cat = categorize_room(r)
        tags.add(cat)
        if cat in PHYSICS_TAGS:
            tags.update(PHYSICS_TAGS[cat])
    entry['physics_tags'] = list(tags)
    entry['room_categories'] = [categorize_room(r) for r in entry['rooms']]

wm_out = os.path.join(BASE, 'data', 'processed', 'world_model_input.json')
with open(wm_out, 'w', encoding='utf-8') as f:
    json.dump(world_model_input, f, ensure_ascii=False, indent=2)
print(f"\n世界模型输入数据: {wm_out}")
print(f"共 {len(world_model_input)} 条带房间的世界模型条目")

print("\n✅ VR知识库构建完成！")
