import json
from pathlib import Path

# 读取VR知识库
vr_file = Path('C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/knowledge/VR_KNOWLEDGE.json')
with open(vr_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 搜索关键词
keywords = ['恒大', '云东海', '云涧花园', '佛山', '别墅', '小区']
matches = []

# 在 raw_vr 中搜索
for vr in data.get('raw_vr', []):
    title = vr.get('title') or ''
    url = vr.get('url') or ''
    designer = vr.get('designer') or ''
    rooms_str = ' '.join(vr.get('rooms', []))
    
    # 检查每个关键词
    matched_kw = None
    for kw in keywords:
        if kw.lower() in title.lower() or kw.lower() in url.lower() or kw.lower() in designer.lower() or kw.lower() in rooms_str.lower():
            matched_kw = kw
            break
    
    if matched_kw:
        matches.append({
            'keyword': matched_kw,
            'index': vr.get('index'),
            'title': title,
            'url': url,
            'platform': vr.get('platform'),
            'designer': designer,
            'rooms': vr.get('rooms', []),
            'views': vr.get('views', 0)
        })

# 去重
seen = set()
unique_matches = []
for m in matches:
    key = m['index']
    if key not in seen:
        seen.add(key)
        unique_matches.append(m)

print(f"Total matches: {len(unique_matches)}")
for m in unique_matches:
    print(f"Keyword: {m['keyword']} | Index: {m['index']} | Title: {m['title']} | Platform: {m['platform']}")
    print(f"  URL: {m['url'][:100]}...")
    print(f"  Designer: {m['designer']} | Rooms: {m['rooms']} | Views: {m['views']}")
    print()

# Also search in rooms section
print("=== Rooms section search ===")
for room_name, room_data in data.get('rooms', {}).items():
    for sample in room_data.get('samples', []):
        orig_name = sample.get('original_name', '')
        title = sample.get('title') or ''
        designer = sample.get('designer') or ''
        for kw in keywords:
            if kw.lower() in orig_name.lower() or kw.lower() in title.lower() or kw.lower() in designer.lower():
                print(f"Room: {room_name} | Keyword: {kw} | Name: {orig_name} | Title: {title} | Platform: {sample.get('platform')}")
                break

# Also search in meta section
print("\n=== Meta section search ===")
meta = data.get('meta', {})
for kw in keywords:
    meta_str = json.dumps(meta, ensure_ascii=False).lower()
    if kw.lower() in meta_str:
        print(f"Keyword '{kw}' found in meta section")

# Search for villa/别墅 type projects
print("\n=== Villa-like projects (别墅/叠排/跃层/大宅) ===")
villa_keywords = ['别墅', '叠排', '跃层', '大宅', '洋房']
for vr in data.get('raw_vr', []):
    title = vr.get('title') or ''
    for vk in villa_keywords:
        if vk.lower() in title.lower():
            print(f"Index: {vr['index']} | Title: {title} | Platform: {vr['platform']} | Views: {vr['views']}")
            break
