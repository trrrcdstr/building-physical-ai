# -*- coding: utf-8 -*-
import json

json_file = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\renderings\rendering_objects.json"
with open(json_file, encoding='utf-8') as f:
    data = json.load(f)

count = 0
for item in data:
    local_path = item.get('path', '')
    if '效果图' in local_path:
        idx = local_path.find('效果图') + 3
        rest = local_path[idx:].replace('\\', '/').lstrip('/')
        item['url'] = f'http://localhost:8888/{rest}'
        count += 1

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'转换完成: {count}条')
print(f'示例: {data[0].get("url", "NO")}')