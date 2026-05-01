# -*- coding: utf-8 -*-
"""
提取新3D效果图链接.docx中的VR链接，去重+分类，纳入世界模型
"""
import zipfile, re, json, os
from xml.etree import ElementTree as ET

docx_path = r"C:\Users\Administrator\Desktop\设计数据库\新3D效果图链接.docx"
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

def extract_urls_v2(text):
    """
    智能URL提取：处理"1.https://xxx 2.https://xxx"无分隔符格式
    通过定位每个https://的位置，计算前一个URL的结束点
    """
    positions = [m.start() for m in re.finditer(r'https://', text)]
    urls = []
    for i, start in enumerate(positions):
        if i + 1 < len(positions):
            end = positions[i + 1]
            url_text = text[start:end]
        else:
            url_text = text[start:]
        
        # 去掉结尾的"数字.https://"（下一个URL的前缀）
        m = re.search(r'\d+\.https?://$', url_text)
        if m:
            url_text = url_text[:m.start()]
        
        # 清理末尾标点
        url = url_text.rstrip('.,;: \t\n')
        if url:
            urls.append(url)
    return urls

# ========== 1. 提取所有URL ==========
with zipfile.ZipFile(docx_path, 'r') as z:
    xml = z.read("word/document.xml").decode("utf-8", errors="ignore")

root = ET.fromstring(xml)
all_text = "".join(t.text or "" for t in root.iter(
    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))

raw_urls = extract_urls_v2(all_text)

# 去重（保持顺序）
seen = set()
unique_urls = []
for u in raw_urls:
    if u not in seen:
        seen.add(u)
        unique_urls.append(u)

print(f"原始URL数: {len(raw_urls)} -> 去重后: {len(unique_urls)}")

# 按域名分类
domains = {}
for url in unique_urls:
    d = re.sub(r'https?://', '', url).split('/')[0].split(':')[0]
    domains[d] = domains.get(d, 0) + 1

print("Domain distribution:")
for d, c in sorted(domains.items(), key=lambda x: -x[1]):
    print(f"  {d}: {c}")

# ========== 2. 生成场景条目 ==========
scenes = []
for i, url in enumerate(unique_urls):
    d = re.sub(r'https?://', '', url).split('/')[0].split(':')[0]
    
    # 从URL提取VR ID
    parts = url.rstrip('/').split('/')
    vr_id = parts[-1].replace('.html', '').replace('.asp', '')
    
    scene = {
        "id": f"docx_{i+1:04d}",
        "name": f"VR效果图 #{i+1}",
        "type": "vr_scene",
        "category": "interior",
        "url": url,
        "source": "新3D效果图链接.docx",
        "domain": d,
        "vr_id": vr_id,
        "index": i + 1,
        "description": "",
        "style": "",
        "room_type": "",
        "tags": [],
    }
    scenes.append(scene)

# ========== 3. 检查现有VR知识库中的URL（避免重复） ==========
existing_urls = set()
existing_vr = load_json(os.path.join(KB, "VR_KNOWLEDGE.json"))
if existing_vr and isinstance(existing_vr, dict):
    for vr in existing_vr.get("raw_vr", []):
        if isinstance(vr, dict) and vr.get("url"):
            existing_urls.add(vr["url"])

new_count = 0
existing_count = 0
for s in scenes:
    if s["url"] in existing_urls:
        s["status"] = "duplicate"
        existing_count += 1
    else:
        s["status"] = "new"
        new_count += 1

print(f"\nNew: {new_count}, existing: {existing_count}")

# ========== 4. 保存干净链接（无隐私信息） ==========
clean_md = f"# 新3D效果图链接（共{len(unique_urls)}个，已去重）\n\n"
for i, s in enumerate(scenes):
    clean_md += f"{i+1}. {s['url']}\n"

with open(os.path.join(PROJ, "vr_docx_clean.md"), 'w', encoding="utf-8") as f:
    f.write(clean_md)
print(f"\nClean links: vr_docx_clean.md")

# ========== 5. 保存场景数据 ==========
output = {
    "source": "新3D效果图链接.docx",
    "total": len(scenes),
    "new": new_count,
    "duplicate": existing_count,
    "domains": domains,
    "scenes": scenes
}
save_json(os.path.join(PROJ, "vr_docx_scenes.json"), output)
print(f"Scene data: vr_docx_scenes.json")

# ========== 6. 追加到世界模型目录 ==========
catalog = load_json(os.path.join(PROJ, "world_model_catalog.json"))
if catalog is None:
    catalog = {"version": "1.0", "scenes": [], "summary": {"total_scenes": 0, "categories": {}}, "physical_objects": [], "relationships": []}

start_id = len(catalog["scenes"])
added = 0
for i, s in enumerate(scenes):
    if s["status"] == "new":
        catalog["scenes"].append({
            "id": f"docx_{start_id+i:04d}",
            "type": "vr_scene",
            "category": s["category"],
            "name": s["name"],
            "source": "新3D效果图链接.docx",
            "url": s["url"],
            "domain": s["domain"],
            "vr_id": s["vr_id"],
            "index": s["index"],
        })
        cat = s["category"]
        catalog["summary"]["categories"][cat] = catalog["summary"]["categories"].get(cat, 0) + 1
        catalog["summary"]["total_scenes"] += 1
        added += 1

save_json(os.path.join(PROJ, "world_model_catalog.json"), catalog)
print(f"World model catalog updated: {catalog['summary']['total_scenes']} scenes total, +{added} new")

# ========== 7. 追加到VR知识库 ==========
if existing_vr and isinstance(existing_vr, dict):
    existing_vr["meta"]["docx_count"] = existing_vr["meta"].get("docx_count", 0) + added
    existing_vr["raw_vr"] = existing_vr.get("raw_vr", [])
    for s in scenes:
        if s["status"] == "new":
            existing_vr["raw_vr"].append({
                "name": s["name"],
                "url": s["url"],
                "source": "新3D效果图链接.docx",
                "category": s["category"],
                "type": "vr_scene",
                "domain": s["domain"],
                "vr_id": s["vr_id"],
                "index": s["index"],
            })
    save_json(os.path.join(KB, "VR_KNOWLEDGE.json"), existing_vr)
    total_vr = len(existing_vr["raw_vr"])
    print(f"VR knowledge base updated: {total_vr} total VRs (+{added} new)")
else:
    new_vr_kb = {
        "meta": {"source": "新3D效果图链接.docx", "count": len(scenes)},
        "raw_vr": [{"name": s["name"], "url": s["url"], "source": "新3D效果图链接.docx",
                    "category": s["category"], "domain": s["domain"], "vr_id": s["vr_id"]} for s in scenes]
    }
    save_json(os.path.join(KB, "VR_KNOWLEDGE_DOCX.json"), new_vr_kb)
    print(f"New VR KB: VR_KNOWLEDGE_DOCX.json ({len(scenes)} VRs)")

print("\nDone.")
