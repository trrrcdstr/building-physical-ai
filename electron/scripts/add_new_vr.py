# -*- coding: utf-8 -*-
"""
添加3个新VR链接到知识库
"""
import json
import os
from datetime import datetime

KB = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge"
PROJ = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed"

# 新URL列表（去重后）
new_urls = [
    "https://vr.justeasy.cn/view/d11757452g76z641-1758796744.html",
    "https://vr.justeasy.cn/view/176y49ex54254vl1-1750324726.html",
]

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def save_json(path, data):
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 加载现有知识库
vr_kb = load_json(os.path.join(KB, "VR_KNOWLEDGE.json"))
catalog = load_json(os.path.join(PROJ, "world_model_catalog.json"))

# 获取现有URL集合
existing_urls = set()
if vr_kb and "raw_vr" in vr_kb:
    for vr in vr_kb["raw_vr"]:
        if isinstance(vr, dict) and vr.get("url"):
            existing_urls.add(vr["url"])

print(f"现有VR数量: {len(vr_kb.get('raw_vr', []))}")
print(f"现有URL数量: {len(existing_urls)}")

# 添加新VR
added = 0
now = datetime.now().strftime("%Y-%m-%d %H:%M")

for url in new_urls:
    if url in existing_urls:
        print(f"跳过（已存在）: {url}")
        continue
    
    # 提取VR ID
    parts = url.rstrip('/').split('/')
    vr_id = parts[-1].replace('.html', '').replace('.asp', '')
    
    # 创建VR条目
    vr_entry = {
        "name": f"VR效果图 (手动添加 {now})",
        "url": url,
        "source": "手动添加",
        "category": "interior",
        "type": "vr_scene",
        "domain": "vr.justeasy.cn",
        "vr_id": vr_id,
        "platform": "Justeasy",
        "added_at": now,
    }
    
    # 添加到知识库
    vr_kb["raw_vr"].append(vr_entry)
    existing_urls.add(url)
    added += 1
    print(f"添加: {url}")

# 更新元数据
vr_kb["meta"]["total_vr"] = len(vr_kb["raw_vr"])
vr_kb["meta"]["last_updated"] = now

# 保存
save_json(os.path.join(KB, "VR_KNOWLEDGE.json"), vr_kb)
print(f"\nVR知识库已更新: {len(vr_kb['raw_vr'])} 个VR (+{added})")

# 更新世界模型目录
if catalog:
    start_id = len(catalog.get("scenes", []))
    for i, url in enumerate(new_urls):
        if url not in [s.get("url") for s in catalog.get("scenes", [])]:
            parts = url.rstrip('/').split('/')
            vr_id = parts[-1].replace('.html', '').replace('.asp', '')
            
            catalog["scenes"].append({
                "id": f"manual_{start_id+i+1:04d}",
                "type": "vr_scene",
                "category": "interior",
                "name": f"VR效果图 (手动添加)",
                "source": "手动添加",
                "url": url,
                "domain": "vr.justeasy.cn",
                "vr_id": vr_id,
                "added_at": now,
            })
            catalog["summary"]["total_scenes"] = catalog["summary"].get("total_scenes", 0) + 1
    
    save_json(os.path.join(PROJ, "world_model_catalog.json"), catalog)
    print(f"世界模型目录已更新: {catalog['summary']['total_scenes']} 个场景")

print("\n完成！")
