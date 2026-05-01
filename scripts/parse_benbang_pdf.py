# -*- coding: utf-8 -*-
import fitz
import json
import re
import os

pdf_path = r'C:\Users\Administrator\Desktop\广州本邦工程顾问有限公司图册（酒店、商业）.pdf'
doc = fitz.open(pdf_path)

print(f'总页数: {len(doc)}')
print(f'图片数: 145')
print()

results = {
    'file': '广州本邦工程顾问有限公司图册（酒店、商业）.pdf',
    'pages': len(doc),
    'total_images': 0,
    'company_name': '广州本邦工程顾问有限公司',
    'projects': []
}

# 各页内容摘要
page_summaries = []

for i in range(len(doc)):
    page = doc[i]
    text = page.get_text().strip()
    imgs = page.get_images()
    results['total_images'] += len(imgs)
    text_len = len(text.replace(' ', '').replace('\n', ''))

    summary = {
        'page': i + 1,
        'text_chars': text_len,
        'images': len(imgs),
        'preview': text[:200] if text else '[图片/空白]'
    }
    page_summaries.append(summary)

    if i < 15:
        print(f"第{i+1:02d}页: 文字{text_len}字 图片{len(imgs)}张 | {text[:80] if text else '[图片/空白]'}")

doc.close()

results['page_summaries'] = page_summaries

# 保存结果
out_path = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\benbang_survey.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n已保存: {out_path}")