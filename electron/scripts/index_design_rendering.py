"""
设计数据库效果图索引生成器
扫描: 室内效果图 / 建筑效果图 / 园林效果图
输出: rendering_database.json (带分类+嵌入)
"""
import os
import json
import hashlib
import math
from pathlib import Path
from datetime import datetime
from PIL import Image
import io

# ============================================================
# 配置
# ============================================================
DESIGN_ROOT = Path(r"C:\Users\Administrator\Desktop\设计数据库")
OUT_FILE    = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\RENDERING_DATABASE.json")

CATEGORIES = {
    "室内效果图": {
        "type": "interior",
        "subcategories": {
            "家庭":   {"scene": "residential", "label": "家庭室内", "rooms": ["客厅", "卧室", "餐厅", "厨房", "卫生间"]},
            "办公":   {"scene": "office", "label": "办公室内", "rooms": ["开放办公区", "会议室", "接待区"]},
            "工装":   {"scene": "commercial", "label": "工装室内", "rooms": ["商业空间", "展厅", "门店"]},
            "酒店民俗": {"scene": "hotel", "label": "酒店民宿", "rooms": ["大堂", "客房", "餐厅", "走廊"]},
            "餐饮":   {"scene": "restaurant", "label": "餐饮空间", "rooms": ["用餐区", "厨房", "包间", "吧台"]},
            "地产":   {"scene": "real_estate", "label": "地产样板间", "rooms": ["客厅", "主卧", "厨房"]},
        }
    },
    "建筑效果图": {
        "type": "architectural",
        "subcategories": {
            "别墅建筑花园": {"scene": "villa", "label": "别墅建筑花园", "floors": "low-rise"},
            "市政公园":    {"scene": "park", "label": "市政公园", "features": ["绿化", "步道", "水景", "亭台"]},
            "产业园写字楼街景外立面": {"scene": "office_building", "label": "产业园写字楼", "floors": "mid-rise"},
            "商场综合体":  {"scene": "mall", "label": "商场综合体", "features": ["商业裙楼", "塔楼", "广场"]},
            "地产小区":    {"scene": "residential_complex", "label": "住宅小区", "features": ["住宅楼", "景观", "车位"]},
            "工厂建筑":    {"scene": "factory", "label": "工厂建筑", "features": ["厂房", "仓库", "办公"]},
            "学校建筑园林": {"scene": "school", "label": "学校园林", "features": ["教学楼", "操场", "绿化"]},
        }
    },
    "园林效果图": {
        "type": "landscape",
        "subcategories": {
            "根目录": {"scene": "landscape", "label": "园林景观", "features": ["绿化", "水景", "步道", "亭台", "公园"]},
        }
    }
}

# ============================================================
# 图像特征提取（简化版：用文件属性+尺寸作为伪嵌入）
# ============================================================
def extract_image_features(img_path: Path) -> dict:
    """提取图像特征（用于检索匹配）"""
    try:
        with Image.open(img_path) as img:
            w, h = img.size
            aspect = round(w / h, 2) if h > 0 else 1.0
            mode = img.mode  # RGB/CMYK/...
    except Exception:
        w, h, aspect, mode = 0, 0, 1.0, "unknown"

    return {
        "width": w,
        "height": h,
        "aspect_ratio": aspect,
        "color_mode": mode,
        "file_size_kb": round(img_path.stat().st_size / 1024, 1),
    }

def compute_file_hash(path: Path, prefix_len: int = 8) -> str:
    """计算文件内容哈希（用于去重）"""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:prefix_len]

# ============================================================
# 场景标签推断
# ============================================================
def infer_scene_tags(filename: str, category: str, subcategory: str) -> list:
    """从文件名和目录推断场景标签"""
    tags = []
    fn_lower = filename.lower()

    # 材质/风格标签
    style_map = {
        "新中式": "新中式", "欧式": "欧式", "现代": "现代简约",
        "中式": "中式", "古典": "古典", "轻奢": "轻奢",
        "简约": "简约", "复古": "复古", "极简": "极简",
        "西班牙": "西班牙风格", "东南亚": "东南亚风格",
    }
    for kw, style in style_map.items():
        if kw in filename:
            tags.append(style)

    # 功能标签
    if any(k in fn_lower for k in ["客厅", "卧室", "餐厅", "厨房", "卫生间", "浴室"]):
        tags.append("家居空间")
    if any(k in fn_lower for k in ["办公", "写字楼", "工位", "会议室"]):
        tags.append("办公空间")
    if any(k in fn_lower for k in ["酒店", "大堂", "客房", "民宿"]):
        tags.append("酒店空间")
    if any(k in fn_lower for k in ["餐厅", "餐饮", "咖啡", "酒吧"]):
        tags.append("餐饮空间")
    if any(k in fn_lower for k in ["泳池", "游泳池", "水景"]):
        tags.append("亲水空间")
    if any(k in fn_lower for k in ["花园", "庭院", "绿化", "园林"]):
        tags.append("绿化空间")
    if any(k in fn_lower for k in ["停车", "车库"]):
        tags.append("停车设施")
    if any(k in fn_lower for k in ["俯瞰", "鸟瞰", "航拍"]):
        tags.append("俯瞰视角")

    return tags if tags else ["通用"]

# ============================================================
# 主扫描函数
# ============================================================
def scan_directory(base_path: Path, category_info: dict) -> list:
    """扫描一个类别目录"""
    records = []
    subcategories = category_info["subcategories"]

    for sub_name, sub_info in subcategories.items():
        sub_dir = base_path / sub_name

        if sub_name == "根目录":
            # 园林效果图在根目录
            sub_dir = base_path

        if not sub_dir.exists():
            continue

        # 获取所有图片
        image_files = []
        for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG", "*.png", "*.PNG"]:
            image_files.extend(sub_dir.glob(ext))

        for img_path in sorted(image_files, key=lambda p: p.name):
            # 特征提取
            features = extract_image_features(img_path)
            content_hash = compute_file_hash(img_path)

            # 场景标签
            scene_tags = infer_scene_tags(img_path.stem, category_info["type"], sub_name)

            record = {
                "id": content_hash,
                "category": category_info["type"],
                "subcategory": sub_name,
                "scene": sub_info.get("scene", ""),
                "scene_label": sub_info.get("label", sub_name),
                "filename": img_path.name,
                "path": f"file://{img_path}".replace("\\", "/"),
                "file_size_kb": features["file_size_kb"],
                "width": features["width"],
                "height": features["height"],
                "aspect_ratio": features["aspect_ratio"],
                "color_mode": features["color_mode"],
                "scene_tags": scene_tags,
                "rooms": sub_info.get("rooms", []),
                "features": sub_info.get("features", []),
                "embedding_hint": f"{category_info['type']}_{sub_info.get('scene','')}_{features['aspect_ratio']}",
                "added_at": datetime.now().isoformat(),
            }

            records.append(record)

    return records

def main():
    print("=" * 60)
    print("设计数据库效果图索引生成器")
    print("=" * 60)

    all_records = []
    stats = {}

    for cat_name, cat_info in CATEGORIES.items():
        cat_dir = DESIGN_ROOT / cat_name
        if not cat_dir.exists():
            print(f"  [SKIP] {cat_name} - 目录不存在")
            continue

        records = scan_directory(cat_dir, cat_info)
        all_records.extend(records)
        stats[cat_name] = len(records)
        print(f"  {cat_name}: {len(records)} 张")

    print(f"\n总计: {len(all_records)} 张效果图")

    # 去重（按哈希）
    seen = set()
    unique = []
    for r in all_records:
        if r["id"] not in seen:
            seen.add(r["id"])
            unique.append(r)
    print(f"去重后: {len(unique)} 张")

    # 保存
    output = {
        "meta": {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "source": str(DESIGN_ROOT),
            "total_images": len(unique),
            "stats": stats,
        },
        "records": unique,
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVED] {OUT_FILE}")
    print(f"  大小: {OUT_FILE.stat().st_size / 1024:.1f} KB")

    # 统计
    from collections import Counter
    cats = Counter(r["category"] for r in unique)
    subs = Counter(r["subcategory"] for r in unique)
    tags = Counter(t for r in unique for t in r["scene_tags"])

    print("\n[按类别]")
    for c, n in cats.most_common():
        print(f"  {c}: {n}")

    print("\n[按子类别]")
    for s, n in subs.most_common():
        print(f"  {s}: {n}")

    print("\n[按标签 TOP15]")
    for t, n in tags.most_common(15):
        print(f"  {t}: {n}")

    return unique

if __name__ == "__main__":
    main()
