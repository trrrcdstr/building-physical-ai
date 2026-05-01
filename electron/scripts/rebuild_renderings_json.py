#!/usr/bin/env python3
"""
重建 rendering_objects.json - 使用正确的文件路径
自动扫描 桌面/设计数据库 下的效果图目录
"""
import os, json

BASE = r"C:\Users\Administrator\Desktop\设计数据库"

# 场景分类映射（子目录名 → category + scene_type）
CATEGORY_MAP = {
    # 室内
    "家庭":     {"category": "室内", "scene_type": "residence"},
    "办公":     {"category": "室内", "scene_type": "office"},
    "工装":     {"category": "室内", "scene_type": "office"},
    "酒店民俗":  {"category": "室内", "scene_type": "hotel"},
    "地产":     {"category": "室内", "scene_type": "residential"},
    "餐饮":     {"category": "室内", "scene_type": "mall"},
    # 室外/园林
    "市政公园":  {"category": "园林", "scene_type": "park"},
    # 建筑
    "产业园写字楼街景外立面": {"category": "建筑", "scene_type": "office_building"},
    "别墅建筑花园":           {"category": "建筑", "scene_type": "residential"},
    "商场综合体":             {"category": "建筑", "scene_type": "commercial_complex"},
    "地产小区":               {"category": "建筑", "scene_type": "residential"},
    "学校建筑园林":           {"category": "建筑", "scene_type": "residential"},
    "工厂建筑":               {"category": "建筑", "scene_type": "office_building"},
}

# 颜色主题
CAT_COLORS = {
    "室内": "#E8D5B7",
    "园林": "#A8D0A0",
    "建筑": "#B8C8D8",
}

def scan_directory(root_dir, category, scene_type):
    """扫描目录，收集所有图片"""
    objects = []
    idx = 1
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in sorted(filenames):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                full_path = os.path.join(dirpath, fname)
                size_kb = os.path.getsize(full_path) // 1024
                # 取子目录名作为 scene 标识
                subdir = os.path.basename(dirpath)
                # 生成 ID
                id_prefix = f"{category}_{scene_type}"
                obj_id = f"{id_prefix}_{idx:04d}"
                # file:// URL for frontend
                file_url = "file:///" + full_path.replace("\\", "/").replace(" ", "%20")
                # 3D position: spread across scene
                spread_x = (idx % 20) * 15
                spread_z = (idx // 20) * 10
                obj = {
                    "id": obj_id,
                    "name": fname,
                    "type": "rendering",
                    "scene_type": scene_type,
                    "category": category,
                    "scene": subdir,
                    "path": file_url,
                    "original_path": full_path,
                    "size_kb": size_kb,
                    "position": {"x": spread_x, "y": 0, "z": spread_z},
                    "tags": [category, scene_type, subdir],
                }
                objects.append(obj)
                idx += 1
    return objects

def main():
    all_objects = []
    
    # 扫描室内效果图
    indoor_dir = os.path.join(BASE, "室内效果图")
    if os.path.exists(indoor_dir):
        for subdir in os.listdir(indoor_dir):
            sub_path = os.path.join(indoor_dir, subdir)
            if os.path.isdir(sub_path):
                info = CATEGORY_MAP.get(subdir, {"category": "室内", "scene_type": "residence"})
                objs = scan_directory(sub_path, info["category"], info["scene_type"])
                all_objects.extend(objs)
                print(f"  室内/{subdir}: {len(objs)} 张")

    # 扫描园林效果图
    garden_dir = os.path.join(BASE, "园林效果图")
    if os.path.exists(garden_dir):
        for subdir in os.listdir(garden_dir):
            sub_path = os.path.join(garden_dir, subdir)
            if os.path.isdir(sub_path):
                info = CATEGORY_MAP.get(subdir, {"category": "园林", "scene_type": "park"})
                objs = scan_directory(sub_path, info["category"], info["scene_type"])
                all_objects.extend(objs)
                print(f"  园林/{subdir}: {len(objs)} 张")

    # 扫描建筑效果图
    building_dir = os.path.join(BASE, "建筑效果图")
    if os.path.exists(building_dir):
        for subdir in os.listdir(building_dir):
            sub_path = os.path.join(building_dir, subdir)
            if os.path.isdir(sub_path):
                info = CATEGORY_MAP.get(subdir, {"category": "建筑", "scene_type": "office_building"})
                objs = scan_directory(sub_path, info["category"], info["scene_type"])
                all_objects.extend(objs)
                print(f"  建筑/{subdir}: {len(objs)} 张")

    # 写 JSON
    out_path = os.path.join(
        r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai",
        "web-app", "public", "data", "rendering_objects.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_objects, f, ensure_ascii=False, indent=2)
    
    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\nWritten: {out_path}")
    print(f"Total: {len(all_objects)} objects")
    print(f"File size: {size_mb:.1f} MB")

    # 统计
    cats = {}
    for obj in all_objects:
        cats[obj["category"]] = cats.get(obj["category"], 0) + 1
    print("\nBy category:")
    for cat, cnt in sorted(cats.items()):
        print(f"  {cat}: {cnt}")

    # 验证前3个路径可读
    print("\nSample paths (first 3):")
    for obj in all_objects[:3]:
        print(f"  {obj['id']}: {obj['path'][:80]}")

main()
