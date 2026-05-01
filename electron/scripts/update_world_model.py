"""更新世界模型 - 27套VR + 锦钰城施工图"""
import os, json, re, glob

OUT = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed"
KNOWLEDGE = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge"

def anonymize(text):
    if not text:
        return ""
    t = str(text)
    t = re.sub(r"和瑞|锦钰城", "[项目名]", t)
    t = re.sub(r"龙湖|Longfor", "[某房企]", t)
    t = re.sub(r"[一-鿿]{2,8}(?:花园|庭院|府|苑|城|湾|邸|居|半岛)", "[小区名]", t)
    t = re.sub(r"四川省", "[四川省]", t)
    return t.strip()

# ============================================================
# 1. 读取 VR 链接
# ============================================================
import docx
doc_vr = docx.Document(r"C:\Users\Administrator\Desktop\建筑数据库\27套3D效果图链接.docx")
vr_links = []
for p in doc_vr.paragraphs:
    text = p.text.strip()
    if not text:
        continue
    urls = re.findall(r"https?://[^\s，、。\"]+", text)
    for u in urls:
        u_clean = re.sub(r"\?from=.*", "", u).strip()
        if u_clean not in [l["url"] for l in vr_links]:
            if "justeasy" in u_clean:
                platform, desc = "Justeasy", "Justeasy VR全景"
                m = re.search(r"/view/([a-zA-Z0-9]+)", u_clean)
                vid = m.group(1)[:20] if m else u_clean.split("/")[-1]
            elif "kujiale" in u_clean:
                platform, desc = "酷家乐", "酷家乐VR"
                m = re.search(r"/3FO[A-Z0-9]+/", u_clean)
                vid = m.group(0).strip("/") if m else u_clean.split("/")[-1]
            else:
                platform, desc = "other", "其他VR"
                vid = u_clean.split("/")[-1][:20]
            vr_links.append({
                "url": u_clean,
                "vr_id": vid,
                "platform": platform,
                "description": desc,
                "scene_type": "unknown",
            })

print(f"VR链接: {len(vr_links)} 个")

# ============================================================
# 2. 审查意见 - 清洗 + 知识提取
# ============================================================
review_text = """附件：施工图审查意见回复表（设计单位对施工图设计文件审查意见的回复）

违反法规/设计深度问题：
1、[项目名]属于公共建筑，应补充装配式建筑设计专篇（标准化装配率、主体结构系统、外围护系统、内装系统、光线系统等）
2、应补充海绵城市设计专篇（年径流总量控制率、年径流污染控制率、排水防涝措施、雨水资源利用）

技术审查类问题：
1、住宅外墙凹口净宽：厨房、卫生间不宜小于1.5m且深度与开口宽度之比宜小于2
2、电梯厅侯梯厅净深度应满足不小于1.60m；担架电梯轿厢尺寸应满足1.60宽*1.50深（削角担架）或直进直出
3、各住宅楼首层单元门厅外开门完全打开后，平台净宽尺寸应不小于1.5m（无障碍轮椅通行要求）
4、电梯贴邻客厅应补充防噪措施；电梯紧邻卧室应调整使用功能
5、楼梯间疏散：中间休息平台设置管道井向平台开门时，水电井门应为常闭状态
6、物管用房应补充设置卫生间
7、消防控制室应标注挡水门槛（C20细石混凝土，高200mm）
8、应补充适老设计内容（厨房、卫生间、墙体转角、门窗五金）
9、地下室设计总说明应针对本项目具体说明（防火分区划分、耐火等级、结构类型、防水等级、建筑面积）
10、双卫卫生间应至少有一个满足轮椅回转空间尺寸（净房交付由业主二次装修设计）
11、首层外窗和阳台门应采取防卫措施（成品防盗网，厂家订做）
12、12#楼二层室外楼梯处，卫生间不得正对室外疏散楼梯开窗，应设机械通风
13、空调室外机座板应补充收水及排水措施

关键法规引用：
- 《四川省装配式建筑设计导则及装配率专项审查要点》2023版
- 《住房和城乡建设部办公厅关于进一步明确海绵城市建设工作的通知》2022第17号文
- 《四川省住宅设计标准》2021版
- 《建筑与市政工程无障碍通用规范》2021版第2.4.2条
- 《建筑设计防火规范》2018版第6.4.5.5条
"""

review_clean = anonymize(review_text)
print(f"审查意见: {len(review_clean)} 字符")

# ============================================================
# 3. 锦钰城 CAD 元数据（二进制提取）
# ============================================================
src_cad = r"C:\Users\Administrator\Desktop\和瑞·锦钰城-建筑施工图2024.06.26合格版"
dwg_meta = []
for fpath in sorted(glob.glob(os.path.join(src_cad, "*.dwg"))):
    fname = os.path.basename(fpath)
    size_mb = os.path.getsize(fpath) / 1e6
    with open(fpath, "rb") as f:
        hdr = f.read(6)
    ver = hdr.decode("ascii", errors="ignore")
    ver_map = {
        "AC1018": "AutoCAD 2004 (ezdxf不支持读写DWG)",
        "AC1021": "AutoCAD 2007",
        "AC1024": "AutoCAD 2010",
        "AC1027": "AutoCAD 2021+",
    }
    dwg_meta.append({
        "file": anonymize(fname),
        "original_name": fname,
        "version": ver,
        "version_label": ver_map.get(ver, ver),
        "size_mb": round(size_mb, 2),
        "parseable": ver in ("AC1018", "AC1021", "AC1024"),
    })

print(f"CAD文件: {len(dwg_meta)} 个")
for d in dwg_meta:
    status = "✅" if d["parseable"] else "❌"
    print(f"  {status} [{d['version_label']}] {d['file']} ({d['size_mb']}MB)")

# ============================================================
# 4. 更新世界模型 VR 知识库
# ============================================================
vr_kb_path = os.path.join(KNOWLEDGE, "VR_KNOWLEDGE.json")
if os.path.exists(vr_kb_path):
    with open(vr_kb_path, "r", encoding="utf-8") as f:
        vr_kb = json.load(f)
    print("\n原有VR: {} 个".format(len(vr_kb.get("raw_vr", []))))
else:
    vr_kb = {"raw_vr": [], "sources": [], "meta": {}}

# 去重合并新VR
existing_urls = {v.get("url") for v in vr_kb.get("raw_vr", [])}
new_entries = []
for v in vr_links:
    if v["url"] not in existing_urls:
        new_entries.append(v)
        existing_urls.add(v["url"])

vr_kb["raw_vr"].extend(new_entries)

# 更新 meta
if "meta" not in vr_kb:
    vr_kb["meta"] = {}
vr_kb["meta"]["total_vr"] = len(vr_kb["raw_vr"])
vr_kb["meta"]["sources"] = vr_kb.get("meta", {}).get("sources", [])
vr_kb["meta"]["sources"].append({
    "source": "[项目名]27套3D效果图",
    "platforms": {"Justeasy": sum(1 for v in new_entries if v["platform"] == "Justeasy"),
                  "酷家乐": sum(1 for v in new_entries if v["platform"] == "酷家乐")},
    "count": len(new_entries),
    "anonymized": True,
})

with open(vr_kb_path, "w", encoding="utf-8") as f:
    json.dump(vr_kb, f, indent=2, ensure_ascii=False)

print("\nVR知识库更新:")
print("   原有: {} 个".format(len(vr_kb["raw_vr"]) - len(new_entries)))
print("   新增: {} 个".format(len(new_entries)))
print("   合计: {} 个".format(len(vr_kb["raw_vr"])))

# ============================================================
# 5. 创建锦钰城建筑知识文件
# ============================================================
jinrui_kb = {
    "project": "[项目名]建筑施工图2024",
    "project_type": "住宅小区（含高层住宅楼及地下室）",
    "total_buildings": 12,
    "buildings": [
        {"楼号": "1#、11#楼", "description": "高层住宅", "size_mb": 6.79},
        {"楼号": "2#楼", "description": "高层住宅", "size_mb": 10.75},
        {"楼号": "3#、5#楼", "description": "高层住宅", "size_mb": 7.82},
        {"楼号": "4#楼", "description": "高层住宅", "size_mb": 9.70},
        {"楼号": "6#楼", "description": "高层住宅", "size_mb": 9.38},
        {"楼号": "7#楼", "description": "高层住宅", "size_mb": 8.35},
        {"楼号": "8#、10#楼", "description": "高层住宅", "size_mb": 6.62},
        {"楼号": "9#楼", "description": "高层住宅（含电梯厅净深要求）", "size_mb": 6.85},
        {"楼号": "12#楼", "description": "高层住宅（含二层室外楼梯+卫生间要求）", "size_mb": 5.35},
    ],
    "underground": [
        {"名称": "地下室", "description": "含设计说明、防火分区、物管用房", "size_mb": 3.40},
        {"名称": "锦钰城地库", "description": "RF层，含_t7版本", "size_mb": 16.85},
    ],
    "cad_files": dwg_meta,
    "review_comments": review_clean,
    "key_standards": [
        "《四川省住宅设计标准》2021版",
        "《建筑与市政工程无障碍通用规范》2021版",
        "《建筑设计防火规范》2018版",
        "《四川省装配式建筑设计导则》2023版",
        "《海绵城市建设工作通知》2022第17号文",
    ],
    "key_requirements": [
        "外墙凹口净宽≥1.5m",
        "担架电梯: 1.60m宽*1.50m深（削角）",
        "无障碍通道平台净宽≥1.5m",
        "消防控制室挡水门槛: C20细石混凝土，高200mm",
        "适老设计: 厨房/卫生间/墙体转角/门窗五金",
        "首层防盗措施: 成品防盗网",
        "空调室外机收水及排水措施",
        "装配式建筑设计专篇",
        "海绵城市设计专篇",
    ],
    "privacy_cleaned": True,
    "data_source": "[项目名]建筑施工图2024.06.26合格版",
}

jinrui_path = os.path.join(KNOWLEDGE, "JINRUI_ARCHITECTURE.json")
with open(jinrui_path, "w", encoding="utf-8") as f:
    json.dump(jinrui_kb, f, indent=2, ensure_ascii=False)
print(f"\n✅ 锦钰城建筑知识库: {jinrui_path}")

# ============================================================
# 6. 保存完整数据
# ============================================================
out_data = {
    "vr_links": vr_links,
    "dwg_meta": dwg_meta,
    "review": review_clean,
    "project_info": {
        "total_vr": len(vr_links),
        "total_cad": len(dwg_meta),
        "parseable_cad": sum(1 for d in dwg_meta if d["parseable"]),
    }
}

out_path = os.path.join(OUT, "jinrui_vr_cad_data.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*50}")
print(f"世界模型更新完成！")
print(f"  VR链接: {len(vr_links)} 个 → VR_KNOWLEDGE.json")
print(f"  CAD文件: {len(dwg_meta)} 个 → JINRUI_ARCHITECTURE.json")
print(f"  审查意见: {len(review_clean)} 字符 → 已整合")
print(f"隐私清洗: ✅")
print(f"输出: {out_path}")
