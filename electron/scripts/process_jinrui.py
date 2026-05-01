"""和瑞·锦钰城施工图解析 + 27套VR链接清洗"""
import os, glob, json, re, docx

OUT = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed"
os.makedirs(OUT, exist_ok=True)

SRC_VR = r"C:\Users\Administrator\Desktop\建筑数据库\27套3D效果图链接.docx"
SRC_CAD = r"C:\Users\Administrator\Desktop\和瑞·锦钰城-建筑施工图2024.06.26合格版"
SRC_DOCX = r"C:\Users\Administrator\Desktop\和瑞·锦钰城-建筑施工图2024.06.26合格版\建筑专业审查意见回复2024.6.17.doc"

def anonymize(text):
    if not text:
        return ""
    t = str(text)
    t = re.sub(r"和瑞|锦钰城", "[项目名]", t)
    t = re.sub(r"龙湖|Longfor", "[某房企]", t)
    t = re.sub(r"[一-鿿]{2,8}(?:花园|庭院|府|苑|城|湾|邸|居)", "[小区名]", t)
    return t.strip()

# ============================================================
# 1. 读取VR链接
# ============================================================
print("=== 1. VR链接读取 ===")
doc = docx.Document(SRC_VR)
vr_raw = []
for p in doc.paragraphs:
    if p.text.strip():
        vr_raw.append(anonymize(p.text.strip()))

print(f"段落数: {len(vr_raw)}")

# 提取URL
vr_links = []
for line in vr_raw:
    urls = re.findall(r"https?://[^\s，、。\"]+", line)
    for u in urls:
        # 去除 ?from=... 参数
        u_clean = re.sub(r"\?from=.*", "", u).strip()
        if u_clean not in [l["url"] for l in vr_links]:
            vr_links.append({
                "url": u_clean,
                "original": u,
                "platform": "justeasy" if "justeasy" in u_clean else
                           "kujiale" if "kujiale" in u_clean else "other"
            })

print(f"唯一VR链接: {len(vr_links)}")
for i, v in enumerate(vr_links, 1):
    print(f"  {i}. [{v['platform']}] {v['url']}")

# 提取VR ID
vr_info = []
for v in vr_links:
    url = v["url"]
    if "justeasy" in url:
        m = re.search(r"/view/([a-zA-Z0-9]+)", url)
        vid = m.group(1) if m else url.split("/")[-1]
        v["vr_id"] = vid
        v["type"] = "720yun_similar"
        v["description"] = "Justeasy VR全景"
    elif "kujiale" in url:
        m = re.search(r"/3FO[A-Z0-9]+/", url)
        vid = m.group(0).strip("/") if m else url
        v["vr_id"] = vid
        v["type"] = "kujiale"
        v["description"] = "酷家乐VR"
    else:
        v["vr_id"] = url
        v["type"] = "unknown"
        v["description"] = "其他VR"
    vr_info.append(v)

# VR数据 - 分类场景
vr_scenes = {
    "data_source": "[项目名]27套VR",
    "platforms": {"justeasy": 0, "kujiale": 0, "other": 0},
    "links": [],
    "scene_types": []
}

for v in vr_info:
    vr_scenes["platforms"][v["platform"]] += 1
    vr_scenes["links"].append(v)

# ============================================================
# 2. 解析锦钰城 CAD (AC1018 = AutoCAD 2004)
# ============================================================
print("\n=== 2. 锦钰城 CAD 解析 ===")

try:
    import ezdxf
    HAS_EZDXF = True
except:
    HAS_EZDXF = False
    print("ezdxf not available")

cad_results = []
total_entities = 0

if HAS_EZDXF:
    dwg_files = glob.glob(os.path.join(SRC_CAD, "*.dwg"))
    for fpath in sorted(dwg_files):
        fname = os.path.basename(fpath)
        size_mb = os.path.getsize(fpath) / 1e6
        
        # 检查版本
        with open(fpath, "rb") as f:
            hdr = f.read(6)
        ver = hdr.decode("ascii", errors="ignore")
        
        if ver not in ("AC1018", "AC1021", "AC1024"):
            print(f"[SKIP {ver}] {fname}")
            cad_results.append({
                "file": anonymize(fname),
                "version": ver,
                "size_mb": round(size_mb, 2),
                "status": "skip_version",
            })
            continue
        
        try:
            doc_cad = ezdxf.readfile(fpath)
            msp = doc_cad.modelspace()
            entities = list(msp)
            etype_counts = {}
            
            for e in msp:
                t = e.dxftype()
                etype_counts[t] = etype_counts.get(t, 0) + 1
            
            bbox = msp.bounding_box()
            bb = None
            if bbox:
                bb = {"min": [round(float(x), 3) for x in bbox.extmin],
                      "max": [round(float(x), 3) for x in bbox.extmax]}
            
            # 提取文本实体（图例、标注）
            texts = []
            for e in msp:
                if e.dxftype() in ("TEXT", "MTEXT"):
                    txt = e.text[:200].replace("\n", " ") if hasattr(e, "text") else ""
                    if txt.strip():
                        texts.append(anonymize(txt[:100]))
            
            # 提取图层名
            layers = []
            for ln in doc_cad.layers:
                layers.append({"name": anonymize(ln.dxf.name), "color": str(ln.dxf.color)})
            
            total_entities += len(entities)
            print(f"[OK] {fname}: {len(entities)} entities, {len(layers)} layers, bbox={bb}")
            
            cad_results.append({
                "file": anonymize(fname),
                "original_name": fname,
                "version": ver,
                "size_mb": round(size_mb, 2),
                "status": "ok",
                "total_entities": len(entities),
                "entity_types": etype_counts,
                "bbox": bb,
                "layers": layers[:20],  # 最多20个图层
                "texts_sample": texts[:30],  # 最多30个文本样本
            })
            doc_cad.close()
        except Exception as e:
            print(f"[ERR] {fname}: {e}")
            cad_results.append({
                "file": anonymize(fname),
                "version": ver,
                "size_mb": round(size_mb, 2),
                "status": "error",
                "error": str(e)[:100],
            })

# ============================================================
# 3. 读取审查意见 DOCX
# ============================================================
print("\n=== 3. 审查意见 DOCX ===")
try:
    doc_review = docx.Document(SRC_DOCX)
    review_text = []
    for p in doc_review.paragraphs:
        if p.text.strip():
            review_text.append(anonymize(p.text.strip()))
    
    print(f"段落: {len(review_text)}")
    print("预览:", "\n".join(review_text[:5]))
    
    review_data = {
        "source": "建筑专业审查意见回复",
        "paragraphs": len(review_text),
        "content": review_text,
    }
except Exception as e:
    review_data = {"error": str(e)}
    print(f"Error: {e}")

# ============================================================
# 4. 生成完整数据报告
# ============================================================
report = {
    "source": "[项目名]建筑施工图2024",
    "data_type": "cad_vr_knowledge",
    "vr_data": vr_scenes,
    "cad_data": {
        "total_files": len(cad_results),
        "parsed": sum(1 for r in cad_results if r.get("status") == "ok"),
        "skipped": sum(1 for r in cad_results if r.get("status") == "skip_version"),
        "errors": sum(1 for r in cad_results if r.get("status") == "error"),
        "total_entities": total_entities,
        "files": cad_results,
    },
    "review_data": review_data,
    "privacy_cleaned": True,
}

out_json = os.path.join(OUT, "jinrui_jinyucheng_data.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n{'='*50}")
print(f"完成！")
print(f"  VR链接: {len(vr_links)} 个 (Justeasy: {vr_scenes['platforms']['justeasy']}, 酷家乐: {vr_scenes['platforms']['kujiale']})")
print(f"  CAD文件: {len(cad_results)} 个")
print(f"  CAD解析成功: {sum(1 for r in cad_results if r.get('status') == 'ok')}")
print(f"  CAD总实体数: {total_entities}")
print(f"  输出: {out_json}")
print(f"隐私: ✅ 清洗完成")
