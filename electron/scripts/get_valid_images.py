import json, sys
sys.stdout.reconfigure(encoding='utf-8')
json_path = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\renderings\rendering_objects.json'
with open(json_path, encoding='utf-8') as f:
    data = json.load(f)
# 过滤室内类（category=室内），取前2张
indoor = [d for d in data if d.get('category') == '室内'][:2]
print('找到 %d 张室内图片，取前2张：' % len(indoor))
for i, item in enumerate(indoor):
    url = item.get('path', '')
    # 转换URL为本地路径（http://localhost:8888/ → C:/Users/Administrator/Desktop/设计数据库/效果图/）
    local_path = url.replace('http://localhost:8888/', r'C:/Users/Administrator/Desktop/设计数据库/效果图/')
    print('图%d:' % (i+1))
    print('  URL: %s' % url)
    print('  本地路径: %s' % local_path)
    print('  分辨率: %dx%d' % (item.get('width', 0), item.get('height', 0)))