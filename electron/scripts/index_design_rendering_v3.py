"""
设计数据库索引生成器 V3 - 递归扫描所有子目录
"""
import os, sys, io, json, hashlib
from pathlib import Path
from datetime import datetime
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("设计数据库索引器 V3 (递归)")
print("=" * 60)

DESIGN_ROOT = Path(r"C:\Users\Administrator\Desktop\设计数据库")
OUT_FILE = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\RENDERING_DATABASE.json")

# 从路径推断类别
def infer_category(full_path: Path) -> dict:
    """从完整路径推断类别信息"""
    parts = full_path.parts  # e.g. [..., '设计数据库', '效果图', '室内效果图', '家庭']
    path_str = str(full_path).replace('\\', '/')

    # 室内效果图 family
    if '室内效果图' in path_str or '室内家居场景' in path_str:
        if '家庭' in path_str or '家居场景' in path_str:
            return {"category": "interior", "scene": "residential", "label": "家庭室内"}
        elif '工装' in path_str:
            return {"category": "interior", "scene": "commercial", "label": "工装室内"}
        elif '酒店' in path_str or '民俗' in path_str:
            return {"category": "interior", "scene": "hotel", "label": "酒店民宿"}
        elif '餐饮' in path_str:
            return {"category": "interior", "scene": "restaurant", "label": "餐饮空间"}
        elif '地产' in path_str:
            return {"category": "interior", "scene": "real_estate", "label": "地产样板间"}
        elif '办公' in path_str:
            return {"category": "interior", "scene": "office", "label": "办公室内"}
        else:
            return {"category": "interior", "scene": "interior", "label": "室内空间"}

    # 建筑效果图 family
    elif '建筑效果图' in path_str:
        if '别墅' in path_str:
            return {"category": "architectural", "scene": "villa", "label": "别墅建筑花园"}
        elif '市政公园' in path_str or '公园' in path_str:
            return {"category": "architectural", "scene": "park", "label": "市政公园"}
        elif '产业园' in path_str or '写字楼' in path_str or '街景' in path_str:
            return {"category": "architectural", "scene": "office_building", "label": "产业园写字楼"}
        elif '商场' in path_str or '综合体' in path_str:
            return {"category": "architectural", "scene": "mall", "label": "商场综合体"}
        elif '地产小区' in path_str or '小区' in path_str:
            return {"category": "architectural", "scene": "residential_complex", "label": "地产小区"}
        elif '工厂' in path_str or '厂房' in path_str:
            return {"category": "architectural", "scene": "factory", "label": "工厂建筑"}
        elif '学校' in path_str:
            return {"category": "architectural", "scene": "school", "label": "学校园林"}
        else:
            return {"category": "architectural", "scene": "building", "label": "建筑景观"}

    # 园林效果图
    elif '园林效果图' in path_str or '景观' in path_str:
        return {"category": "landscape", "scene": "landscape", "label": "园林景观"}

    # 家庭别墅 subdirs
    elif '家庭别墅' in path_str:
        if '李女士' in path_str:
            return {"category": "interior", "scene": "residential", "label": "家庭室内-李女士"}
        elif '覃总' in path_str:
            return {"category": "interior", "scene": "residential", "label": "家庭室内-覃总"}
        elif '王总' in path_str:
            return {"category": "interior", "scene": "residential", "label": "家庭室内-王总"}
        elif '黄总' in path_str:
            return {"category": "interior", "scene": "residential", "label": "家庭室内-黄总"}
        elif '山水庭院' in path_str:
            return {"category": "interior", "scene": "residential", "label": "家庭室内-山水庭院"}
        elif '从化别墅' in path_str:
            return {"category": "interior", "scene": "residential", "label": "家庭室内-从化别墅"}
        elif '室内家居场景' in path_str:
            return {"category": "interior", "scene": "residential", "label": "家庭室内场景"}
        else:
            return {"category": "interior", "scene": "residential", "label": "家庭别墅"}

    # 酒店场景
    elif '酒店' in path_str:
        return {"category": "interior", "scene": "hotel", "label": "酒店场景"}

    else:
        return {"category": "unknown", "scene": "unknown", "label": "未分类"}

STYLE_KEYWORDS = {
    "新中式": "新中式", "欧式": "欧式", "现代": "现代简约",
    "中式": "中式", "古典": "古典", "轻奢": "轻奢",
    "简约": "简约", "复古": "复古", "极简": "极简",
    "西班牙": "西班牙", "东南亚": "东南亚",
}

def infer_style_tags(filename: str) -> list:
    tags = []
    fn = filename.replace('_', '').replace('-', '').replace(' ', '')
    for kw, tag in STYLE_KEYWORDS.items():
        if kw in fn:
            tags.append(tag)
    return tags if tags else ["通用风格"]

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

def scan_recursive(base_path: Path) -> list:
    """递归扫描所有子目录中的jpg文件"""
    records = []
    seen_hashes = set()

    for img_path in base_path.rglob("*"):  # recursive glob
        if not img_path.is_file():
            continue
        if img_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
            continue

        # 跳过CAD图纸目录（只要效果图）
        path_str = str(img_path).replace('\\', '/')
        if any(k in path_str for k in ['CAD施工图', '电气CAD', '6#', '7#', '9#', '.dwg', '.pdf', '.doc', '.bak']):
            continue

        # 提取特征
        features = extract_features(img_path)
        content_hash = compute_hash(img_path)

        # 去重
        if content_hash in seen_hashes:
            continue
        seen_hashes.add(content_hash)

        # 推断类别
        info = infer_category(img_path)
        style_tags = infer_style_tags(img_path.name)

        # 子目录名（取最近的一级子目录）
        rel_parts = img_path.relative_to(base_path).parts
        subcategory = rel_parts[1] if len(rel_parts) > 1 else rel_parts[0] if len(rel_parts) == 1 else "root"

        record = {
            "id": content_hash,
            "category": info["category"],
            "subcategory": subcategory,
            "scene": info["scene"],
            "scene_label": info["label"],
            "filename": img_path.name,
            "path": f"file:///{img_path.as_posix()}",  # unix-style for JSON
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

    return records

# 主程序
records = scan_recursive(DESIGN_ROOT)

print(f"扫描完成: {len(records)} 张效果图")

# 统计
from collections import Counter
cats = Counter(r["category"] for r in records)
subs = Counter(r["subcategory"] for r in records)
styles = Counter(t for r in records for t in r["style_tags"])

print("\n[按类别]")
for c, n in cats.most_common():
    print(f"  {c}: {n}")
print("\n[按子目录]")
for s, n in subs.most_common():
    print(f"  {s}: {n}")
print("\n[按风格 TOP10]")
for t, n in styles.most_common(10):
    print(f"  {t}: {n}")

# 保存
output = {
    "meta": {
        "version": "3.0",
        "created_at": datetime.now().isoformat(),
        "source": str(DESIGN_ROOT),
        "total_images": len(records),
    },
    "records": records,
}

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n[SAVED] {OUT_FILE} ({OUT_FILE.stat().st_size / 1024:.1f} KB)")

# 验证前3条路径
print("\n[路径验证]")
for r in records[:3]:
    p = r["path"].replace("file:///", "")
    exists = os.path.exists(p)
    print(f"  [{'OK' if exists else 'MISS'}] {p[:80]}")
