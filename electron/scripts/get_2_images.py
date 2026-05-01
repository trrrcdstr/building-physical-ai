import json, sys
sys.stdout.reconfigure(encoding='utf-8')
json_path = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\renderings\rendering_objects.json'
with open(json_path, encoding='utf-8') as f:
    data = json.load(f)
indoor = [d for d in data if d.get('category') == '室内' and d.get('scene') == '家庭']
print('找到 %d 张室内家庭图片' % len(indoor))
for i, item in enumerate(indoor[:2]):
    url = item.get('path', '')
    local = url.replace('http://localhost:8888/', r'C:\Users\Administrator\Desktop\设计数据库\效果图\\')
    print('图%d: %s' % (i+1, local))
    print('URL: %s' % url)