"""
ArchDaily 中国站项目批量采集器
目标：采集 500+ 项目
"""
import requests
import re
import json
import time
from pathlib import Path
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# 已知项目ID范围（ArchDaily 中国站）
# 通过观察，中国项目ID大致在 600000-1030000 之间
PROJECT_ID_RANGES = [
    (980000, 983000),  # 最新项目
    (900000, 905000),
    (850000, 855000),
    (800000, 805000),
    (750000, 755000),
    (700000, 705000),
    (650000, 655000),
]

def parse_project_page(html: str, url: str) -> dict:
    """解析项目页面"""
    project = {
        'title': '',
        'source': 'archdaily_cn',
        'url': url,
        'category': 'Architecture',
        'description': '',
        'tags': [],
        'architects': [],
        'locations': [],
        'year': None,
        'scraped_at': datetime.now().isoformat(),
    }
    
    # 提取标题
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if title_match:
        project['title'] = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
    
    # 提取描述（meta description）
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', html)
    if desc_match:
        project['description'] = desc_match.group(1)
    
    # 提取标签
    tags = re.findall(r'/cn/tag/([^"\'>\s]+)', html)
    project['tags'] = list(set(tags))[:15]
    
    # 判断分类
    if any(t in ['ju-zhu-jian-zhu', 'zhu-zhai', 'bie-shu'] for t in project['tags']):
        project['category'] = 'Residential'
    elif any(t in ['wen-hua-jian-zhu', 'bo-wu-guan', 'ju-yuan'] for t in project['tags']):
        project['category'] = 'Cultural'
    elif any(t in ['shang-ye-jian-zhu', 'ban-gong', 'jiu-dian'] for t in project['tags']):
        project['category'] = 'Commercial'
    elif any(t in ['jing-guan', 'jing-guan-jian-zhu', 'gong-yuan'] for t in project['tags']):
        project['category'] = 'Landscape'
    elif any(t in ['shi-nei', 'shi-nei-she-ji'] for t in project['tags']):
        project['category'] = 'Interior'
    elif any(t in ['jiao-yu-jian-zhu', 'xue-xiao'] for t in project['tags']):
        project['category'] = 'Educational'
    
    # 提取建筑师（从标题或描述中）
    # 常见模式："项目名 / 事务所名"
    if ' / ' in project['title']:
        parts = project['title'].split(' / ')
        if len(parts) >= 2:
            project['architects'] = [parts[-1].strip()]
    
    # 提取地点（从标签中）
    location_tags = [t for t in project['tags'] if t in [
        'zhong-guo', 'bei-jing', 'shang-hai', 'guang-zhou', 'shen-zhen',
        'hang-zhou', 'cheng-du', 'nan-jing', 'wu-han', 'xi-an',
        'su-zhou', 'qing-dao', 'da-lian', 'xia-men', 'kun-ming'
    ]]
    if location_tags:
        project['locations'] = location_tags
    
    # 提取年份
    year_match = re.search(r'(20\d{2})', project['title'])
    if year_match:
        project['year'] = int(year_match.group(1))
    
    return project

def fetch_and_parse(project_id: int) -> dict:
    """获取并解析单个项目"""
    url = f'https://www.archdaily.cn/cn/{project_id}'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200 and 'archdaily' in resp.text.lower():
            project = parse_project_page(resp.text, url)
            if project['title'] and len(project['title']) > 5:
                return project
    except Exception as e:
        pass
    return None

def batch_collect(target_count: int = 500, output_dir: Path = None):
    """批量采集"""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'web_knowledge'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_projects = []
    
    # 加载已有数据
    existing_file = output_dir / 'archdaily_cn_projects.json'
    if existing_file.exists():
        with open(existing_file, 'r', encoding='utf-8') as f:
            all_projects = json.load(f)
        print(f'[INFO] 加载已有数据: {len(all_projects)} 条')
    
    # 开始采集
    for start, end in PROJECT_ID_RANGES:
        print(f'\n[INFO] 采集范围: {start} - {end}')
        for pid in range(start, end):
            if len(all_projects) >= target_count:
                break
            
            # 跳过已存在的
            if any(p.get('url', '').endswith(str(pid)) for p in all_projects):
                continue
            
            project = fetch_and_parse(pid)
            if project:
                all_projects.append(project)
                print(f'  [{len(all_projects)}] {project["title"][:50]}... ({project["category"]})')
            
            # 每50条保存一次
            if len(all_projects) % 50 == 0:
                with open(existing_file, 'w', encoding='utf-8') as f:
                    json.dump(all_projects, f, ensure_ascii=False, indent=2)
                print(f'  [SAVE] 已保存 {len(all_projects)} 条')
            
            time.sleep(0.3)  # 礼貌延迟
        
        if len(all_projects) >= target_count:
            break
    
    # 最终保存
    with open(existing_file, 'w', encoding='utf-8') as f:
        json.dump(all_projects, f, ensure_ascii=False, indent=2)
    
    print(f'\n[DONE] 共采集 {len(all_projects)} 条项目')
    return all_projects

if __name__ == '__main__':
    import sys
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    batch_collect(target_count=target)
