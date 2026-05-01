# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path

base_dir = r"C:\Users\Administrator\Desktop\设计数据库\效果图"

# 分类映射：实际文件夹名 -> 类别
category_map = {
    "室内效果图": "室内",
    "园林效果图": "园林",
    "建筑效果图": "建筑",
}

# 子类别映射：实际子文件夹名 -> 场景类型
scene_map = {
    # 室内
    "家庭": "家庭",
    "别墅": "家庭",
    "客厅": "家庭",
    "卧室": "家庭",
    "餐厅": "家庭",
    "厨房": "家庭",
    "卫生间": "家庭",
    "书房": "家庭",
    "工装": "工装",
    "商业": "商业",
    "商场": "商场",
    "餐饮": "餐饮",
    "酒店": "酒店",
    "民宿": "酒店民俗",
    "办公": "办公",
    "地产": "地产",
    # 园林
    "公园": "市政公园",
    "别墅园林": "别墅园林",
    "景观": "园林",
    "绿化": "园林",
    # 建筑
    "别墅建筑": "别墅建筑花园",
    "写字楼": "产业园写字楼",
    "产业园": "产业园写字楼",
    "小区": "地产小区",
    "商业综合体": "商场综合体",
    "工厂": "工厂建筑",
    "学校": "学校建筑园林",
}

renderings = []
image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

# 遍历分类目录
for cat_dir, category in category_map.items():
    cat_path = os.path.join(base_dir, cat_dir)
    if not os.path.exists(cat_path):
        print(f"跳过不存在: {cat_path}")
        continue
    
    print(f"扫描: {cat_dir}")
    
    # 遍历场景子目录
    for scene_dir in os.listdir(cat_path):
        scene_path = os.path.join(cat_path, scene_dir)
        if not os.path.isdir(scene_path):
            continue
        
        # 映射场景类型
        scene_type = scene_map.get(scene_dir, scene_dir)
        
        # 遍历图片文件
        for f in os.listdir(scene_path):
            ext = os.path.splitext(f)[1].lower()
            if ext not in image_exts:
                continue
            
            full_path = os.path.join(scene_path, f)
            rel_path = os.path.join("设计数据库", "效果图", cat_dir, scene_dir, f)
            
            renderings.append({
                "id": len(renderings) + 1,
                "name": f,
                "path": full_path,
                "category": category,
                "scene_type": scene_type,
                "subdir": f"{cat_dir}/{scene_dir}"
            })

# 统计
stats = {"室内": {}, "园林": {}, "建筑": {}}
for r in renderings:
    cat = r["category"]
    scene = r["scene_type"]
    if scene not in stats[cat]:
        stats[cat][scene] = 0
    stats[cat][scene] += 1

print(f"\n总渲染图: {len(renderings)}")
print("\n分类统计:")
for cat, scenes in stats.items():
    print(f"  {cat}:")
    for scene, count in scenes.items():
        print(f"    {scene}: {count}")

# 保存JSON
output_file = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\renderings\rendering_objects.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(renderings, f, ensure_ascii=False, indent=2)

print(f"\n已保存到: {output_file}")