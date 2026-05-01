import re
from pathlib import Path

# 搜索多个数据文件
keywords = ['恒大', '云东海', '云涧', '佛山', '恒安', '元田', '里水', '三水', '丰发']

files_to_search = [
    'C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/web-app/src/data/sceneData.ts',
    'C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/web-app/src/data/sceneData_renderings.ts',
    'C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/web-app/src/data/room_scene_data.js',
    'C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/web-app/src/data/sceneConfig.ts',
]

results = {}

for file_path in files_to_search:
    p = Path(file_path)
    if not p.exists():
        continue
    
    content = p.read_text(encoding='utf-8')
    file_name = p.name
    
    found_keywords = []
    for kw in keywords:
        if kw in content:
            found_keywords.append(kw)
            idx = content.find(kw)
            context = content[max(0, idx-80):idx+120]
            results[f'{file_name}-{kw}'] = context
    
    if found_keywords:
        print(f'\n=== {file_name} ===')
        print(f'Keywords: {found_keywords}')
        for kw in found_keywords:
            ctx = results.get(f'{file_name}-{kw}', '')[:200]
            print(f'\nContext for "{kw}":\n{ctx}\n')

# 搜索 data 目录下的其他文件
data_dir = Path('C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/data')
if data_dir.exists():
    print('\n=== Searching data directory ===')
    for json_file in data_dir.glob('*.json'):
        content = json_file.read_text(encoding='utf-8')
        for kw in keywords:
            if kw in content:
                print(f'Found "{kw}" in {json_file.name}')
                idx = content.find(kw)
                print(f'  Context: {content[max(0, idx-50):idx+100]}')
                break
