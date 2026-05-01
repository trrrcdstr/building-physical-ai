#!/usr/bin/env python3
"""验证 rendering_objects.json 的路径编码"""
import json, os

path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\web-app\public\data\rendering_objects.json"
with open(path, 'rb') as f:
    raw = f.read()

data = json.loads(raw)
print(f"Total objects: {len(data)}")
first = data[0]

# 检查 UTF-8 字节中是否包含中文
# "室内效果图" UTF-8: \xe5\xae\xbd\xe5\xae\xa4\xe6\x95\x88\xe6\x9e\x9c\xe5\x9b\xbe
idx = raw.find(b'\xe5\xae\xbd')  # '宽' (开头的第一个字)
if idx >= 0:
    print(f"UTF-8 Chinese found at byte {idx}")
    print(f"Context: {raw[idx-5:idx+20]}")
else:
    print("No UTF-8 Chinese found in raw bytes")

# 检查路径是否正确
print(f"\nFirst path: {first['path']}")
print(f"First category: {first['category']}")
print(f"First scene_type: {first['scene_type']}")
print(f"First scene: {first['scene']}")

# 验证路径实际可读
p = first['original_path']
if os.path.exists(p):
    print(f"\nOK: original_path EXISTS: {p[:80]}")
else:
    print(f"\nWARN: original_path NOT FOUND: {p[:80]}")
    # 尝试用设计数据库路径
    alt = p.replace("室内效果图", "室内效果图".encode('utf-8').decode('utf-8'))
    print(f"  Trying direct path check...")

# 统计
cats = {}
for obj in data:
    cats[obj['category']] = cats.get(obj['category'], 0) + 1
print("\nBy category:")
for k, v in sorted(cats.items()):
    print(f"  {k}: {v}")

# 检查是否有空path
bad = sum(1 for obj in data if not obj.get('path'))
print(f"\nEntries with no path: {bad}")
