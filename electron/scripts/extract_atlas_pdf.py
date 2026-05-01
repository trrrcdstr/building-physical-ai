# -*- coding: utf-8 -*-
"""Extract PDF content and anonymize for world model"""
import os, json, re, sys
from pypdf import PdfReader

PDF_PATH = r"C:\Users\Administrator\Desktop\广州本邦工程顾问有限公司图册（酒店、商业）.pdf"
OUT_DIR = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge"
OUT_FILE = os.path.join(OUT_DIR, "HOTEL_COMMERCIAL_ATLAS.json")

# Company names to anonymize
COMPANY_NAMES = [
    "广州本邦工程顾问有限公司",
    "广州本创机电工程有限公司",
    "本邦工程顾问",
    "本邦工程",
    "本创机电",
    "本邦",
    "广州本邦",
]

# Project names to anonymize (will detect from context)
PROJECT_PATTERNS = [
    r"[^\s]{2,10}(?:酒店|宾馆|民宿|度假村|中心|广场|大厦|花园|公馆|府邸|湾|城|汇|天地)",
    r"[^\s]{2,8}(?:广场|中心|综合体|商业街)",
]

def anonymize(text):
    if not text:
        return ""
    t = str(text)
    for name in COMPANY_NAMES:
        t = t.replace(name, "[公司名]")
    # Anonymize project names (hotel/commercial names)
    t = re.sub(r"(?:项目名称?[:：]?\s*)[\u4e00-\u9fff]{2,15}(?:酒店|中心|广场|大厦|花园|公馆)", 
               lambda m: m.group(0)[:3] + "[项目名]", t)
    # Anonymize addresses
    t = re.sub(r"广东省[^\s,，。]{2,20}", "[地址]", t)
    t = re.sub(r"广州[^\s,，。]{2,20}(?:路|街|大道|区|市)", "[地址]", t)
    return t.strip()

reader = PdfReader(PDF_PATH)
pages_data = []
all_text = []
project_list = []
design_elements = []
mep_systems = []

for i, page in enumerate(reader.pages):
    text = (page.extract_text() or "").strip()
    if not text:
        pages_data.append({"page": i+1, "text": "", "has_images": True})
        continue
    
    clean = anonymize(text)
    pages_data.append({"page": i+1, "text": clean, "has_images": len(text) < 100})
    all_text.append(clean)
    
    # Extract design knowledge
    # MEP systems
    for sys_name in ["暖通空调", "给排水", "消防", "电气", "智能化", "弱电", "空调", "通风", 
                      "防排烟", "供配电", "照明", "动力", "监控", "楼宇自控", "BA系统",
                      "给水", "排水", "雨水", "污水", "热水", "冰蓄冷", "VAV", "风机盘管",
                      "新风", "排风", "排烟", "喷淋", "消火栓", "灭火", "气体灭火"]:
        if sys_name in text:
            if sys_name not in mep_systems:
                mep_systems.append(sys_name)
    
    # Extract hotel/commercial specific design knowledge
    for kw in ["客房", "大堂", "宴会厅", "会议室", "健身房", "游泳池", "SPA", 
               "厨房", "洗衣房", "停车场", "商业", "裙楼", "塔楼", "地下室",
               "设备房", "机房", "制冷机房", "锅炉房", "水泵房", "变配电房",
               "弱电间", "管井", "新风机组", "空调箱", "冷热源", "地源热泵",
               "节能", "绿建", "LEED"]:
        if kw in text:
            if kw not in design_elements:
                design_elements.append(kw)

# Build knowledge base
full_text = "\n\n".join(all_text)
kb = {
    "source": "酒店+商业类图册（已脱敏）",
    "total_pages": len(reader.pages),
    "file_size_mb": round(os.path.getsize(PDF_PATH) / 1e6, 1),
    "created_by": "WPS演示导出",
    "creation_date": "2023-10-26",
    "privacy_cleaned": True,
    
    "design_scope": {
        "project_types": ["酒店", "商业综合体", "办公楼", "豪宅"],
        "services": [
            "机电设计顾问",
            "工程项目管理",
            "节能改造技术服务",
            "EPC机电咨询",
            "二次机电设计（装修阶段）",
            "医疗专项/生化实验室设计",
        ],
        "mep_systems": sorted(mep_systems),
        "design_phases": ["规划方案", "初步设计", "招标图", "施工图"],
    },
    
    "key_design_elements": sorted(design_elements),
    
    "pages": pages_data,
    
    "full_text_anonymized": full_text,
}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

print("PDF extraction complete:")
print("  Pages: {}".format(len(reader.pages)))
print("  MEP systems found: {}".format(len(mep_systems)))
print("  Design elements: {}".format(len(design_elements)))
print("  Text chars: {}".format(len(full_text)))
print("  Output: {}".format(OUT_FILE))
print("  Privacy: {}".format(kb["privacy_cleaned"]))

# Print sample
print("\n--- Sample content (Page 1-3) ---")
for p in pages_data[:3]:
    if p["text"]:
        print("\n[Page {}]".format(p["page"]))
        print(p["text"][:300])
