# -*- coding: utf-8 -*-
"""
解析广州本邦工程顾问PDF，提取所有项目信息，去掉公司名称，存入世界模型
"""
import fitz
import json
import re
import os

pdf_path = r'C:\Users\Administrator\Desktop\广州本邦工程顾问有限公司图册（酒店、商业）.pdf'
doc = fitz.open(pdf_path)

all_pages = []

for i in range(len(doc)):
    page = doc[i]
    text = page.get_text().strip()
    imgs = page.get_images()
    all_pages.append({
        'page': i + 1,
        'text_chars': len(text.replace(' ', '').replace('\n', '')),
        'images': len(imgs),
        'text': text
    })

doc.close()

# 提取项目信息（从有项目数据的页面）
projects = []
building_area_pattern = re.compile(r'建筑面积[：:]\s*([^\n\r]{1,30})')
status_pattern = re.compile(r'项目状况[：:]\s*([^\n\r]{1,20})')
service_pattern = re.compile(r'服务内容[：:]\s*([^\n\r]{1,40})')

# 搜索所有包含项目信息的页面
current_project = {}
for p in all_pages:
    if p['images'] == 0 or p['text_chars'] < 30:
        continue
    
    text = p['text']
    
    # 跳过公司介绍页
    if any(kw in text[:50] for kw in ['公司团队', '机电设计顾问服务', '我们的服务', '项目类型', '服务内容', '核心竞争力', '公司宗旨', '项目业绩']):
        continue
    
    # 提取项目名称（第一行通常是项目名，超过2个字）
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    project_name = None
    for line in lines:
        # 过滤掉标题类文字
        if any(kw in line for kw in ['机电设计', '酒店', '商业', '医院', '办公楼', '豪宅', '服务', '项目']):
            if len(line) < 10:
                continue
        if len(line) >= 4 and not line.startswith('n'):
            project_name = line
            break
    
    if not project_name:
        continue
    
    area = None
    for line in lines:
        am = building_area_pattern.search(line)
        if am:
            area = am.group(1).strip()
            break
    
    status = None
    for line in lines:
        sm = status_pattern.search(line)
        if sm:
            status = sm.group(1).strip()
            break
    
    service = None
    for line in lines:
        sv = service_pattern.search(line)
        if sv:
            service = sv.group(1).strip()
            break
    
    # 构造项目数据（去掉公司名）
    project = {
        'name': project_name,
        'building_area': area,
        'status': status,
        'service': service,
        'images': p['images'],
        'page': p['page']
    }
    projects.append(project)

# 去重（根据名称）
seen = set()
unique = []
for p in projects:
    key = p['name'].strip()
    if key and key not in seen:
        seen.add(key)
        unique.append(p)

print(f"共提取 {len(unique)} 个项目")
for p in unique:
    print(f"  [{p['page']}] {p['name']} | 面积:{p['building_area']} | 状态:{p['status']} | 服务:{p['service']}")

# 构建世界模型数据
world_model_projects = []
category_map = {
    '度假': '酒店', '酒店': '酒店', '民宿': '酒店', '温德姆': '酒店',
    '香格里拉': '酒店', '白天鹅': '酒店', '山庄': '酒店', '温泉': '酒店',
    '商业': '商业', '商业街': '商业', '综合体': '商业', '广场': '商业'
}

for p in unique:
    name = p['name']
    cat = '未知'
    for kw, c in category_map.items():
        if kw in name:
            cat = c
            break
    
    world_model_projects.append({
        'name': name,
        'category': cat,
        'building_area': p['building_area'],
        'status': p['status'],
        'service': p['service'],
        'source': '广州本邦工程顾问有限公司图册（酒店、商业）',
        'page': p['page'],
        'type': '机电设计顾问'
    })

# 保存
out_path = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\BENBANG_PROJECTS.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(world_model_projects, f, ensure_ascii=False, indent=2)

print(f"\n已保存 {len(world_model_projects)} 个项目到:")
print(out_path)