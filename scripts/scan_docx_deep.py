# -*- coding: utf-8 -*-
"""
深度扫描docx：文本+公司/电话关键词+文档属性
"""
import zipfile, re, json
from xml.etree import ElementTree as ET

docx_path = r"C:\Users\Administrator\Desktop\设计数据库\新3D效果图链接.docx"

with zipfile.ZipFile(docx_path, 'r') as z:
    # 列出所有文件
    print("=== DOCX内部文件 ===")
    for name in z.namelist():
        print(f"  {name}")

    # 文档主体
    xml_content = z.read("word/document.xml").decode("utf-8", errors="ignore")

    # 文档属性（core.xml）
    try:
        core = z.read("docProps/core.xml").decode("utf-8", errors="ignore")
        print("\n=== 文档属性 ===")
        print(core[:500])
    except:
        pass

    # app.xml
    try:
        app = z.read("docProps/app.xml").decode("utf-8", errors="ignore")
        print("\n=== APP属性 ===")
        print(app[:500])
    except:
        pass

# 扫描所有文本（包括批注、页眉页脚）
print("\n=== 扫描公司/电话关键词 ===")
keywords_company = ["公司", "科技", "装饰", "设计", "工作室", "工作室", "工作室", "有限公司", "集团", "设计院"]
keywords_phone = ["电话", "手机", "微信", "QQ", "邮箱", "@", "1[0-9]{10}", "[0-9]{3,4}-[0-9]{7,8}"]

root = ET.fromstring(xml_content)
all_text = "".join(t.text or "" for t in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))

print(f"总文本长度: {len(all_text)}")
print(f"前300字符: {all_text[:300]}")
print(f"后300字符: {all_text[-300:]}")

# 搜索关键词
found = []
for kw in keywords_company + ["有限公司", "设计", "装饰"]:
    if kw in all_text:
        # 找到上下文
        idx = all_text.find(kw)
        ctx = all_text[max(0,idx-20):idx+40]
        found.append(f"[{kw}] ...{ctx}...")
        if len(found) > 5:
            break

if found:
    print("\n发现公司关键词:")
    for f in found:
        print(f"  {f}")
else:
    print("\n未发现公司/电话关键词（文本干净）")

# URL统计
urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', all_text)
print(f"\n总URL数: {len(urls)}")
domains = {}
for url in urls:
    d = re.sub(r'https?://', '', url).split('/')[0]
    domains[d] = domains.get(d, 0) + 1
print("域名统计:")
for d, c in sorted(domains.items(), key=lambda x: -x[1]):
    print(f"  {d}: {c}")
