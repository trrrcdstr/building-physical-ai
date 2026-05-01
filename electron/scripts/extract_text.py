# -*- coding: utf-8 -*-
"""
提取本邦PDF所有文字（分页）
"""
import fitz
import json

pdf_path = r'C:\Users\Administrator\Desktop\广州本邦工程顾问有限公司图册（酒店、商业）.pdf'
doc = fitz.open(pdf_path)

all_pages = []
for i in range(len(doc)):
    page = doc[i]
    # 尝试原始文本
    blocks = page.get_text("dict")["blocks"]
    texts = []
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    texts.append(span["text"])
    full_text = "\n".join(texts)
    all_pages.append({
        'page': i + 1,
        'text': full_text
    })

doc.close()

# 保存为JSON
out = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\benbang_text.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(all_pages, f, ensure_ascii=False, indent=2)

print(f"Saved {len(all_pages)} pages")

# 打印全部文本以便分析
for p in all_pages:
    if p['text'].strip():
        print(f"\n=== PAGE {p['page']} ===")
        print(p['text'][:400])