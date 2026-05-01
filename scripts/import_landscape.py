# -*- coding: utf-8 -*-
"""
扫描园林效果图目录 → 复制到项目 → 纳入世界模型
"""
import os, json, hashlib, shutil
from datetime import datetime
from PIL import Image

SRC = r"C:\Users\Administrator\Desktop\园林效果图"
DST = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\raw\landscape_renderings"
KB = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge"
PROJ = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed"

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def save_json(path, data):
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 创建目标目录
os.makedirs(DST, exist_ok=True)

# 扫描图片
images = []
for f in os.listdir(SRC):
    if f.lower().endswith(('.jpg', '.jpeg')):
        src_path = os.path.join(SRC, f)
        size = os.path.getsize(src_path)
        try:
            img = Image.open(src_path)
            w, h = img.size
            img.close()
        except:
            w, h = 0, 0
        file_hash = hashlib.md5(f.encode()).hexdigest()[:8]
        images.append({
            "original_name": f,
            "src": src_path,
            "size_bytes": size,
            "width": w,
            "height": h,
            "file_hash": file_hash,
        })

images.sort(key=lambda x: -x["size_bytes"])
print(f"扫描完成: {len(images)} 张图片")

# 复制
copied = []
for i, img in enumerate(images):
    ext = os.path.splitext(img["original_name"])[1].lower()
    new_name = f"landscape_{i+1:03d}_{img['file_hash']}{ext}"
    dst_path = os.path.join(DST, new_name)
    shutil.copy2(img["src"], dst_path)
    img["new_name"] = new_name
    img["dst_path"] = dst_path
    copied.append(img)
    print(f"  [{i+1}] {img['original_name']} -> {new_name} ({img['width']}x{img['height']})")

print(f"\n已复制: {len(copied)} 张")

# 保存元数据
now = datetime.now().strftime("%Y-%m-%d %H:%M")
metadata = {
    "source": "园林效果图",
    "count": len(copied),
    "imported_at": now,
    "images": [
        {
            "original_name": img["original_name"],
            "new_name": img["new_name"],
            "relative_path": f"data/raw/landscape_renderings/{img['new_name']}",
            "width": img["width"],
            "height": img["height"],
            "size_bytes": img["size_bytes"],
        }
        for img in copied
    ]
}
save_json(os.path.join(PROJ, "landscape_renderings_meta.json"), metadata)

# 纳入世界模型目录
catalog = load_json(os.path.join(PROJ, "world_model_catalog.json"))
start_id = len(catalog.get("scenes", []))

for i, img in enumerate(copied):
    # 判断场景类型
    w, h = img["width"], img["height"]
    if w >= 3000:
        scene_type = "panorama"
    elif w >= 1600:
        scene_type = "wide_view"
    elif h > w:
        scene_type = "vertical"
    else:
        scene_type = "standard"

    catalog["scenes"].append({
        "id": f"landscape_{start_id+i+1:04d}",
        "type": "landscape_image",
        "category": "landscape",
        "name": f"园林效果图 #{i+1}",
        "original_name": img["original_name"],
        "relative_path": f"data/raw/landscape_renderings/{img['new_name']}",
        "width": w,
        "height": h,
        "scene_type": scene_type,
        "source": "园林效果图目录",
        "imported_at": now,
    })

# 更新分类统计
cat_key = "landscape"
catalog["summary"]["categories"][cat_key] = catalog["summary"].get("categories", {}).get(cat_key, 0) + len(copied)
catalog["summary"]["total_scenes"] = len(catalog["scenes"])

save_json(os.path.join(PROJ, "world_model_catalog.json"), catalog)
print(f"世界模型目录: {catalog['summary']['total_scenes']} 个场景（+{len(copied)}园林）")

# 更新VR知识库
vr_kb = load_json(os.path.join(KB, "VR_KNOWLEDGE.json"))
vr_kb["meta"]["total_vr"] = len(vr_kb["raw_vr"])
vr_kb["meta"]["last_updated"] = now
save_json(os.path.join(KB, "VR_KNOWLEDGE.json"), vr_kb)

print("\n完成!")
