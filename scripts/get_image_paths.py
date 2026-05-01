import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('C:/Users/Administrator/.qclaw/workspace/projects/building-physical-ai/data/processed/rendering_objects.json', encoding='utf-8') as f:
    data = json.load(f)
indoor_family = [d for d in data if d.get('category') == '室内' and d.get('scene') == '家庭']
for i, item in enumerate(indoor_family[:2]):
    url = item.get('path', '')
    local_path = url.replace('http://localhost:8888/', 'C:/Users/Administrator/Desktop/设计数据库/效果图/')
    print('Image %d: %s' % (i+1, local_path))
    print('URL: %s' % url)
