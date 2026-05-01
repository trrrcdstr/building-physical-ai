# -*- coding: utf-8 -*-
"""
解析广州本邦工程顾问PDF - 改进版项目提取
"""
import fitz
import json
import re

pdf_path = r'C:\Users\Administrator\Desktop\广州本邦工程顾问有限公司图册（酒店、商业）.pdf'
doc = fitz.open(pdf_path)

# 读取全部页面文本
all_pages_text = []
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text()
    imgs = page.get_images()
    all_pages_text.append({
        'page': i + 1,
        'text': text,
        'images': len(imgs),
        'text_len': len(text.strip().replace(' ','').replace('\n',''))
    })

doc.close()

# 打印全部文本内容，找项目名
print("=== 全部页面内容 ===")
for p in all_pages_text:
    if p['text_len'] > 20:
        print(f"\n--- 第{p['page']}页 ({p['text_len']}字, {p['images']}图) ---")
        print(p['text'][:500])