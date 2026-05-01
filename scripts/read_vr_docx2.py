# -*- coding: utf-8 -*-
"""
读取新3D效果图链接.docx，提取VR链接并去隐私
"""
import zipfile, re, json, os

docx_path = r"C:\Users\Administrator\Desktop\设计数据库\新3D效果图链接.docx"
BASE = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai"

# 读取docx XML内容
with zipfile.ZipFile(docx_path, 'r') as z:
    xml_content = z.read("word/document.xml").decode("utf-8", errors="ignore")

# 提取所有文本
import xml.etree.ElementTree as ET

ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
root = ET.fromstring(xml_content)

paragraphs = []
for para in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
    texts = []
    for t in para.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"):
        if t.text:
            texts.append(t.text)
    text = "".join(texts).strip()
    if text:
        paragraphs.append(text)

print(f"总段落数: {len(paragraphs)}")
print("="*60)
for i, p in enumerate(paragraphs):
    print(f"[{i}] {p}")
