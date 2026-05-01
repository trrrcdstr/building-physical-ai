# -*- coding: utf-8 -*-
"""
建筑物理AI世界模型 - 效果图数据导入管道
将桌面效果图导入世界模型，统一分类 + 生成场景数据
"""
import os
import json
import re
from pathlib import Path
from datetime import datetime

# ========== 配置 ==========
DESKTOP = Path(os.path.expanduser("~")) / "Desktop"

SCAN_DIRS = {
    "室内效果图":  DESKTOP / "室内效果图",
    "建筑效果图":  DESKTOP / "建筑效果图",
    "园林效果图":  DESKTOP / "园林效果图",
}

# ========== 导图分类映射 ==========
# 思维导图四大分类 -> 内部类型标签
MINDMAP_CATEGORIES = {
    "室内": {
        "家庭空间": {
            "description": "家庭居住空间",
            "folders": ["家庭"],
            "scene_types": ["residence", "living_room", "bedroom", "kitchen", "bathroom", "dining_room"],
            "tags": ["家庭", "别墅", "住宅", "客厅", "主卧", "次卧", "厨房", "卫生间", "书房", "餐厅"],
        },
        "商业空间": {
            "description": "商业经营空间",
            "folders": ["餐饮", "地产"],  # 地产属于楼盘展示商业空间
            "scene_types": ["commercial", "retail", "restaurant", "showroom"],
            "tags": ["商场", "超市", "餐厅", "咖啡厅", "样板间", "展厅"],
        },
        "办公空间": {
            "description": "办公商务空间",
            "folders": ["办公", "工装"],
            "scene_types": ["office", "commercial_space"],
            "tags": ["办公室", "会议室", "总裁办", "开放办公", "工装"],
        },
        "酒店空间": {
            "description": "酒店民宿空间",
            "folders": ["酒店民俗"],
            "scene_types": ["hotel", "homestay"],
            "tags": ["酒店", "民宿", "大堂", "客房"],
        },
    },
    "室外": {
        "园林庭院": {
            "description": "私家庭院和园林景观",
            "folders": [],  # 从子目录名匹配
            "scene_types": ["garden", "courtyard"],
            "tags": ["别墅花园", "中式庭院", "现代庭院", "园林"],
            "subdir_keywords": ["花园", "庭院", "园林"],
        },
        "市政景观": {
            "description": "市政公共景观",
            "folders": [],
            "scene_types": ["municipal", "park"],
            "tags": ["市政公园", "道路绿化", "广场", "市政"],
            "subdir_keywords": ["市政", "公园", "道路"],
        },
        "社区空间": {
            "description": "社区住宅小区空间",
            "folders": [],
            "scene_types": ["community", "residential_area"],
            "tags": ["小区", "社区", "广场", "地产小区"],
            "subdir_keywords": ["小区", "社区", "地产"],
        },
    },
    "建筑": {
        "商业建筑": {
            "description": "商业地产建筑",
            "folders": [],
            "scene_types": ["commercial_building", "mall", "office_building"],
            "tags": ["商场", "写字楼", "产业园", "综合体", "商业"],
            "subdir_keywords": ["商场", "写字楼", "产业园", "商业"],
        },
        "居住建筑": {
            "description": "居住住宅建筑",
            "folders": [],
            "scene_types": ["residential_building", "villa", "apartment"],
            "tags": ["别墅", "住宅", "高层", "小区"],
            "subdir_keywords": ["别墅", "住宅", "地产小区"],
        },
        "工业建筑": {
            "description": "工业生产建筑",
            "folders": [],
            "scene_types": ["industrial_building", "factory"],
            "tags": ["工厂", "工业", "厂房", "仓库"],
            "subdir_keywords": ["工厂", "工业"],
        },
        "公共建筑": {
            "description": "公共事业建筑",
            "folders": [],
            "scene_types": ["public_building", "school", "hospital"],
            "tags": ["学校", "医院", "体育馆", "公共", "市政"],
            "subdir_keywords": ["学校", "医院", "体育馆", "公共"],
        },
        "景观建筑": {
            "description": "景观与室外建筑",
            "folders": [],
            "scene_types": ["landscape", "park"],
            "tags": ["市政公园", "景观", "外立面", "街景"],
            "subdir_keywords": ["公园", "街景", "外立面", "景观"],
        },
    },
}

def classify_file(file_path, category, subdir="", filename=""):
    """根据文件路径和目录分类"""
    name_lower = filename.lower()
    name_cn = filename
    
    # 1. 室内效果图 - 直接按子目录分类
    if category == "室内效果图":
        for subcat, info in MINDMAP_CATEGORIES["室内"].items():
            if subdir in info["folders"]:
                return ("室内", subcat, info["scene_types"][0], info["tags"])
    
    # 2. 建筑效果图 - 按子目录关键词匹配
    if category == "建筑效果图":
        for subcat, info in MINDMAP_CATEGORIES["室外"].items():
            for kw in info.get("subdir_keywords", []):
                if kw in subdir:
                    return ("室外", subcat, info["scene_types"][0], info["tags"])
        for subcat, info in MINDMAP_CATEGORIES["建筑"].items():
            for kw in info.get("subdir_keywords", []):
                if kw in subdir:
                    return ("建筑", subcat, info["scene_types"][0], info["tags"])
        # 园林效果图（扁平目录）
        if category == "园林效果图":
            return ("室外", "园林庭院", "garden", ["园林", "景观"])
    
    # 3. 园林效果图
    if category == "园林效果图":
        return ("室外", "园林庭院", "garden", ["园林", "景观"])
    
    return None

def scan_directory(root_path):
    """扫描目录，返回文件列表"""
    files = []
    if not root_path.exists():
        return files
    
    # 直接在根目录的文件
    for f in root_path.glob("*"):
        if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            files.append({
                "path": str(f),
                "name": f.name,
                "category": root_path.name,
                "subdir": "",
                "size_kb": f.stat().st_size // 1024,
            })
    
    # 子目录文件
    for subdir in root_path.iterdir():
        if not subdir.is_dir():
            continue
        for f in subdir.glob("*"):
            if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                files.append({
                    "path": str(f),
                    "name": f.name,
                    "category": root_path.name,
                    "subdir": subdir.name,
                    "size_kb": f.stat().st_size // 1024,
                })
    
    return files

def determine_tags(filename, subdir, top_category, scene):
    """根据文件名和目录推断更多标签"""
    tags = []
    name = filename.lower()
    
    # 风格关键词
    style_kws = {
        "现代": ["现代", "简约", "极简", "北欧"],
        "中式": ["中式", "古典", "传统", "新中式"],
        "欧式": ["欧式", "法式", "美式", "英式"],
        "豪华": ["豪华", "轻奢", "高档", "品质"],
        "日式": ["日式", "和风", "榻榻米"],
        "工业": ["工业", "loft", "复古"],
    }
    
    for style, kws in style_kws.items():
        for kw in kws:
            if kw in name:
                tags.append(style)
                break
    
    # 空间类型关键词
    room_kws = ["客厅", "餐厅", "卧室", "主卧", "次卧", "书房", "厨房", "卫生间", 
                 "洗手间", "阳台", "玄关", "衣帽间", "影音", "茶室", "健身"]
    for room in room_kws:
        if room in name or room in subdir:
            tags.append(room)
    
    return list(set(tags))[:5]  # 最多5个标签

def build_world_objects(files):
    """构建 worldObjects 格式"""
    objects = []
    
    # 映射 top_category -> type
    type_map = {
        "室内": "indoor",
        "室外": "outdoor", 
        "建筑": "building",
    }
    
    # 颜色映射
    color_map = {
        "室内": "#3b82f6",
        "室外": "#22c55e",
        "建筑": "#f59e0b",
    }
    
    for i, f in enumerate(files):
        result = classify_file(f["path"], f["category"], f["subdir"], f["name"])
        if not result:
            continue
        
        top_cat, scene, scene_type, base_tags = result
        extra_tags = determine_tags(f["name"], f["subdir"], top_cat, scene)
        all_tags = list(set(base_tags + extra_tags))
        
        # 生成唯一ID
        obj_id = f"{top_cat.lower()}_{scene.lower().replace('空间','').replace('庭院','').replace('建筑','').replace('景观','').replace('社区','')}_{i+1:04d}"
        obj_id = obj_id.replace(" ", "_").replace("/", "_")
        
        # 计算3D坐标（虚拟空间分布）
        # 按类别分组排列
        x = (i % 50) * 10 + (hash(f["name"]) % 20)
        y = 0
        z = (i // 50) * 10
        
        obj = {
            "id": obj_id,
            "name": f["name"].rsplit(".", 1)[0],  # 去掉扩展名
            "type": type_map.get(top_cat, "unknown"),
            "scene_type": scene_type,
            "category": top_cat,
            "scene": scene,
            "path": f["path"],
            "subdir": f["subdir"],
            "size_kb": f["size_kb"],
            "position": {"x": float(x), "y": float(y), "z": float(z)},
            "dimensions": {"w": 0, "h": 0, "d": 0},
            "tags": all_tags,
            "vrData": None,
        }
        objects.append(obj)
    
    return objects

def main():
    print("🏗️  建筑物理AI世界模型 - 效果图数据导入")
    print("=" * 50)
    
    all_files = []
    
    # 1. 扫描所有目录
    for name, path in SCAN_DIRS.items():
        print(f"\n📂 扫描: {name}")
        files = scan_directory(path)
        print(f"   发现: {len(files)} 张图片")
        all_files.extend(files)
    
    print(f"\n📊 总计: {len(all_files)} 张图片")
    
    # 2. 分类统计
    category_stats = {}
    for f in all_files:
        r = classify_file(f["path"], f["category"], f["subdir"], f["name"])
        if r:
            top_cat, scene, _, _ = r
            key = f"{top_cat} / {scene}"
            category_stats[key] = category_stats.get(key, 0) + 1
    
    print("\n📋 分类统计:")
    for k, v in sorted(category_stats.items()):
        print(f"   {k}: {v}张")
    
    # 3. 构建 worldObjects
    print("\n🔧 构建世界模型数据...")
    world_objects = build_world_objects(all_files)
    print(f"   生成: {len(world_objects)} 个对象")
    
    # 4. 生成 sceneData（按类别分组）
    scene_data = {
        "indoor": [],
        "outdoor": [],
        "building": [],
    }
    for obj in world_objects:
        cat = obj["category"].lower()
        if cat in scene_data:
            scene_data[cat].append({
                "id": obj["id"],
                "name": obj["name"],
                "type": obj["type"],
                "scene_type": obj["scene_type"],
                "scene": obj["scene"],
                "tags": obj["tags"],
            })
    
    # 5. 保存数据
    output_dir = Path("C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/data/processed/renderings")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 世界对象数据
    objects_out = output_dir / "rendering_objects.json"
    with open(objects_out, "w", encoding="utf-8") as f:
        json.dump(world_objects, f, ensure_ascii=False, indent=2)
    print(f"\n💾 保存: {objects_out} ({len(world_objects)} 个对象)")
    
    # 场景统计
    stats_out = output_dir / "rendering_stats.json"
    with open(stats_out, "w", encoding="utf-8") as f:
        json.dump({
            "total_files": len(all_files),
            "total_objects": len(world_objects),
            "category_stats": category_stats,
            "source_dirs": {str(k): str(v) for k, v in SCAN_DIRS.items()},
            "imported_at": datetime.now().isoformat(),
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 保存: {stats_out}")
    
    # 场景数据
    scene_out = output_dir / "rendering_scenes.json"
    with open(scene_out, "w", encoding="utf-8") as f:
        json.dump(scene_data, f, ensure_ascii=False, indent=2)
    print(f"💾 保存: {scene_out}")
    
    # 6. 复制到前端数据目录
    print("\n🌐 同步到前端...")
    try:
        web_src = Path("C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/web-app/src/data")
        web_backup = web_src / "sceneData_render_backup.json"
        web_main = web_src / "sceneData_renderings.ts"
        
        # 生成 TypeScript 格式
        ts_content = f"""// 自动生成 - 效果图世界模型数据
// 导入时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 总对象数: {len(world_objects)}

export const renderingWorldObjects = {json.dumps(world_objects, ensure_ascii=False)} as const;

export const renderingSceneData = {json.dumps(scene_data, ensure_ascii=False)} as const;

export const renderingStats = {{
  total: {len(world_objects)},
  indoor: {len(scene_data.get('indoor', []))},
  outdoor: {len(scene_data.get('outdoor', []))},
  building: {len(scene_data.get('building', []))},
}} as const;
"""
        with open(web_main, "w", encoding="utf-8") as f:
            f.write(ts_content)
        print(f"   ✅ 前端数据: {web_main}")
    except Exception as e:
        print(f"   ⚠️ 前端同步失败: {e}")
    
    print("\n✅ 导入完成!")
    return world_objects, category_stats

if __name__ == "__main__":
    main()
