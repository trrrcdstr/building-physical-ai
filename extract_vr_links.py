"""
提取新3D效果图链接数据
整合到物理AI世界模型数据体系
"""
import json
import re
import docx
from pathlib import Path
from collections import Counter
from datetime import datetime

# 读取docx文件
doc = docx.Document(r'C:\Users\Administrator\Desktop\新3D效果图链接.docx')

# 提取所有链接
all_links = []
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if t and ('http' in t or 'https' in t):
        urls = re.findall(r'https?://[^\s]+', t)
        for url in urls:
            # 提取序号
            num_match = re.match(r'(\d+)\.', t)
            num = int(num_match.group(1)) if num_match else i
            
            # 判断平台
            if '3d66' in url:
                platform = '3d66'
                # 提取ID
                id_match = re.search(r'index_detail_(\d+)', url)
                platform_id = id_match.group(1) if id_match else 'unknown'
            elif 'justeasy' in url:
                platform = 'Justeasy'
                # 提取ID
                id_match = re.search(r'view/([a-z0-9x]+)-', url)
                platform_id = id_match.group(1) if id_match else 'unknown'
            elif '720yun' in url:
                platform = '720yun'
                platform_id = url.split('/')[-1] if '/' in url else 'unknown'
            else:
                platform = 'other'
                platform_id = 'unknown'
            
            all_links.append({
                "index": num,
                "url": url,
                "platform": platform,
                "platform_id": platform_id,
            })

# 去重
seen_urls = set()
unique_links = []
for link in all_links:
    if link['url'] not in seen_urls:
        seen_urls.add(link['url'])
        unique_links.append(link)

print(f"总链接数: {len(all_links)}")
print(f"去重后: {len(unique_links)}")

# 统计
platforms = Counter(l['platform'] for l in unique_links)
print(f"平台分布: {dict(platforms)}")

# 保存为JSON
output = {
    "source": "新3D效果图链接.docx",
    "extracted_at": datetime.now().isoformat(),
    "total_links": len(all_links),
    "unique_links": len(unique_links),
    "platform_distribution": dict(platforms),
    "links": unique_links
}

output_path = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_links_new.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n已保存到: {output_path}")
print(f"文件大小: {output_path.stat().st_size} bytes")
