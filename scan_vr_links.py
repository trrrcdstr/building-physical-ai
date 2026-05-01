"""
批量扫描VR链接，提取场景信息和截图
去掉公司名称和电话信息
"""
import json
import re
import time
from pathlib import Path
from datetime import datetime

# 加载链接数据
with open(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_links_new.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

links = data['links']
print(f"共 {len(links)} 个链接待扫描")

# 已知公司名和电话模式 - 需要从数据中去除
COMPANY_PATTERNS = [
    r'杭州鑫满天装饰\d*',
    r'建E网',
    r'技术支持[：:]?\s*建E网',
]

PHONE_PATTERN = r'1[3-9]\d{9}'  # 中国手机号

def clean_text(text):
    """去除公司名和电话"""
    if not text:
        return text
    result = text
    for pattern in COMPANY_PATTERNS:
        result = re.sub(pattern, '', result)
    result = re.sub(PHONE_PATTERN, '', result)
    # 清理多余空白
    result = re.sub(r'\s+', ' ', result).strip()
    return result

# 按平台分组
platform_groups = {}
for link in links:
    p = link['platform']
    if p not in platform_groups:
        platform_groups[p] = []
    platform_groups[p].append(link)

print(f"平台分布:")
for p, ls in platform_groups.items():
    print(f"  {p}: {len(ls)} 个")

# 输出结构化数据模板
output_template = []
for link in links:
    entry = {
        "id": f"vr-new-{link['index']:03d}",
        "original_index": link['index'],
        "url": link['url'],
        "platform": link['platform'],
        "platform_id": link['platform_id'],
        "title": None,          # 待填充
        "rooms": [],            # 待填充: 房间列表
        "designer_clean": None, # 去除公司电话后的设计师
        "screenshot_path": None,# 截图路径
        "mirrored": False,      # 是否已镜像
    }
    output_template.append(entry)

# 保存模板
template_path = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_links_structured.json')
with open(template_path, 'w', encoding='utf-8') as f:
    json.dump(output_template, f, ensure_ascii=False, indent=2)

print(f"\n模板已保存到: {template_path}")
print("接下来将逐个访问VR页面提取数据...")
