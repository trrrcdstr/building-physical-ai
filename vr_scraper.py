"""
批量VR链接扫描器 - 提取页面信息并截图
使用Playwright自动化浏览器
"""
import json
import re
import os
import time
from pathlib import Path
from datetime import datetime

# 输出目录
SCREENSHOT_DIR = Path(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\vr_screenshots')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# 加载链接数据
with open(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\vr_links_new.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

links = data['links']
print(f"共 {len(links)} 个链接")

# 清理函数 - 去除公司名和电话
def clean_company_info(text):
    """去除公司名和电话号码"""
    if not text:
        return ""
    result = text
    # 去除电话号码
    result = re.sub(r'1[3-9]\d{9}', '', result)
    # 去除常见公司名
    result = re.sub(r'杭州鑫满天装饰', '', result)
    result = re.sub(r'DESIGN by \w+', '', result)
    result = re.sub(r'技术支持[：:]?\s*建E网', '', result)
    result = re.sub(r'效果图小凯', '', result)
    result = re.sub(r'建E网', '', result)
    # 清理多余空白
    result = re.sub(r'\s+', ' ', result).strip()
    return result

# 3d66平台 - 从snapshot中提取信息
def extract_3d66_info(snapshot_text):
    """从3d66页面的snapshot中提取标题和设计师"""
    title = None
    designer = None
    views = None
    
    # 查找标题 - 通常是一个link
    title_match = re.search(r'link\s+"([^"]+)"', snapshot_text)
    if title_match:
        potential_title = title_match.group(1)
        # 跳过公司名
        if '装饰' not in potential_title and 'DESIGN' not in potential_title:
            title = potential_title
    
    # 查找设计师
    designer_match = re.search(r'(?:杭州鑫满天装饰|DESIGN by \w+)', snapshot_text)
    if designer_match:
        designer = designer_match.group(0)
    
    # 查找浏览量
    views_match = re.search(r'"(\d+)"', snapshot_text)
    if views_match:
        views = int(views_match.group(1))
    
    return {
        "title": title,
        "designer_raw": designer,
        "designer_clean": clean_company_info(designer) if designer else None,
        "views": views,
    }

# Justeasy平台 - 从snapshot中提取信息
def extract_justeasy_info(snapshot_text):
    """从Justeasy页面的snapshot中提取"""
    title = None
    rooms = []
    
    # 提取公司信息
    company_match = re.search(r'([\u4e00-\u9fa5]+装饰\d+)', snapshot_text)
    company_raw = company_match.group(0) if company_match else None
    
    # 提取房间名
    room_keywords = ['客厅', '卧室', '主卧', '次卧', '书房', '厨房', '卫生间', 
                     '餐厅', '阳台', '玄关', '儿童房', '衣帽间', '储物间',
                     '沙发床', '电视背景', '餐边柜', '鞋柜']
    for kw in room_keywords:
        if kw in snapshot_text:
            rooms.append(kw)
    
    # 去重
    rooms = list(dict.fromkeys(rooms))
    
    return {
        "company_raw": company_raw,
        "company_clean": clean_company_info(company_raw) if company_raw else None,
        "rooms": rooms,
    }

# 720yun平台
def extract_720yun_info(snapshot_text):
    """从720yun页面的snapshot中提取"""
    title = None
    creator = None
    
    title_match = re.search(r'([\u4e00-\u9fa5]+\d+-\d+)', snapshot_text)
    if title_match:
        title = title_match.group(1)
    
    creator_match = re.search(r'创作者[：:]([^\s"]+)', snapshot_text)
    if creator_match:
        creator = creator_match.group(1)
    
    return {
        "title": title,
        "creator_raw": creator,
        "creator_clean": clean_company_info(creator) if creator else None,
    }

print("脚本已准备就绪")
print("将通过浏览器工具逐个访问VR页面提取数据")
print("每次访问约需5-10秒，81个链接约需7-14分钟")
