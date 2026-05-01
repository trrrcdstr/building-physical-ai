"""
设计数据库索引生成器 V2 - 按实际目录结构动态扫描
"""
import os, sys, io, json, hashlib
from pathlib import Path
from datetime import datetime
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("设计数据库索引器 V2")
print("=" * 60)

DESIGN_ROOT = Path(r"C:\Users\Administrator\Desktop\设计数据库")
OUT_FILE = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\RENDERING_DATABASE.json")

# 类别映射（按实际子目录名推断类别）
CATEGORY_MAP = {
    # 室内效果图 -> interior
    "李女士":     {"category": "interior", "scene": "residential", "label": "家庭室内-李女士"},
    "覃总":       {"category": "interior", "scene": "residential", "label": "家庭室内-覃总"},
    "王总":       {"category": "interior", "scene": "residential", "label": "家庭室内-王总"},
    "黄总":       {"category": "interior", "scene": "residential", "label": "家庭室内-黄总"},
    "山水庭院":   {"category": "interior", "scene": "residential", "label": "家庭室内-山水庭院"},
    "龙湖景观":   {"category": "landscape", "scene": "park", "label": "园林景观"},
    "近距离家具jpg": {"category": "interior", "scene": "furniture", "label": "家具特写"},
    "金螳螂工艺": {"category": "interior", "scene": "craftsmanship", "label": "工艺细节"},
    "山水庭院建筑项目": {"category": "architectural", "scene": "villa", "label": "别墅建筑"},
    # 建筑效果图 -> architectural
    "别墅建筑花园": {"category": "architectural", "scene": "villa", "label": "别墅建筑花园"},
    "市政公园":    {"category": "architectural", "scene": "park", "label": "市政公园"},
    "产业园写字楼街景外立面": {"category": "architectural", "scene": "office_building", "label": "产业园写字楼"},
    "商场综合体":  {"category": "architectural", "scene": "mall", "label": "商场综合体"},
    "地产小区":    {"category": "architectural", "scene": "residential_complex", "label": "地产小区"},
    "工厂建筑":    {"category": "architectural", "scene": "factory", "label": "工厂建筑"},
    "学校建筑园林": {"category": "architectural", "scene": "school", "label": "学校园林"},
    # 园林效果图 -> landscape
    "园林效果图":  {"category": "landscape", "scene": "landscape", "label": "园林景观"},
    # 越香格拉witz -> landscape
    "越香格拉witz": {"category": "landscape", "scene": "landscape", "label": "园林景观"},
}

# 风格推断
STYLE_KEYWORDS = {
    "新中式": "新中式", "欧式": "欧式", "现代": "现代简约",
    "中式": "中式", "古典": "古典", "轻奢": "轻奢",
    "简约": "简约", "复古": "复古", "极简": "极简",
    "西班牙": "西班牙", "东南亚": "东南亚",
}

def infer_style_tags(filename: str) -> list:
    tags = []
    fn = filename.replace('_', '').replace('-', '')
    for kw, tag in STYLE_KEYWORDS.items():
        if kw in fn:
            tags.append(tag)
    if not tags:
        tags.append("通用风格")
    return tags

def extract_features(img_path: Path) -> dict:
    try:
        with Image.open(img_path) as img:
            w, h = img.size
            aspect = round(w / h, 2) if h > 0 else 1.0
            mode = img.mode
    except Exception:
        w, h, aspect, mode = 0, 0, 1.0, "unknown"
    return {
        "width": w,
        "height": h,
        "aspect_ratio": aspect,
        "color_mode": mode,
        "file_size_kb": round(img_path.stat().st_size / 1024, 1),
    }

def compute_hash(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

def scan():
    records = []
    stats = {}

    for cat_dir in sorted(DESIGN_ROOT.iterdir()):
        if not cat_dir.is_dir():
            continue

        cat_name = cat_dir.name
        if cat_name not in stats:
            stats[cat_name] = {"total": 0, "subdirs": {}}

        print(f"\n扫描: {cat_name}")

        # 遍历所有子目录
        for sub_dir in sorted(cat_dir.iterdir()):
            if not sub_dir.is_dir():
                continue

            sub_name = sub_dir.name
            info = CATEGORY_MAP.get(sub_name, {
                "category": "unknown",
                "scene": "unknown",
                "label": sub_name
            })

            # 扫描所有图片
            jpg_files = []
            for ext in ["*.jpg", "*.JPG", "*.jpeg", "*.JPEG"]:
                jpg_files.extend(sub_dir.glob(ext))

            if sub_name not in stats[cat_name]["subdirs"]:
                stats[cat_name]["subdirs"][sub_name] = 0

            for img_path in sorted(jpg_files):
                features = extract_features(img_path)
                content_hash = compute_hash(img_path)
                style_tags = infer_style_tags(img_path.stem)

                record = {
                    "id": content_hash,
                    "category": info["category"],
                    "subcategory": sub_name,
                    "scene": info["scene"],
                    "scene_label": info["label"],
                    "filename": img_path.name,
                    "path": f"file:///{img_path.as_posix()}",  # unix style for JSON
                    "file_size_kb": features["file_size_kb"],
                    "width": features["width"],
                    "height": features["height"],
                    "aspect_ratio": features["aspect_ratio"],
                    "color_mode": features["color_mode"],
                    "style_tags": style_tags,
                    "embedding_hint": f"{info['category']}_{info['scene']}_{features['aspect_ratio']}",
                    "added_at": datetime.now().isoformat(),
                }
                records.append(record)
                stats[cat_name]["subdirs"][sub_name] += 1
                stats[cat_name]["total"] += 1

        print(f"  -> {stats[cat_name]['total']} 张")

    # 去重
    seen = set()
    unique = []
    for r in records:
        if r["id"] not in seen:
            seen.add(r["id"])
            unique.append(r)

    print(f"\n总计: {len(records)} 张, 去重后: {len(unique)} 张")

    # 保存
    output = {
        "meta": {
            "version": "2.0",
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

    print(f"[SAVED] {OUT_FILE} ({OUT_FILE.stat().st_size / 1024:.1f} KB)")

    # 统计
    from collections import Counter
    cats = Counter(r["category"] for r in unique)
    subs = Counter(r["subcategory"] for r in unique)
    styles = Counter(t for r in unique for t in r["style_tags"])

    print("\n[按类别]")
    for c, n in cats.most_common():
        print(f"  {c}: {n}")
    print("\n[按子目录]")
    for s, n in subs.most_common():
        print(f"  {s}: {n}")
    print("\n[按风格 TOP10]")
    for t, n in styles.most_common(10):
        print(f"  {t}: {n}")

    return unique

if __name__ == "__main__":
    scan()
