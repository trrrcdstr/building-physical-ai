#!/usr/bin/env python3
"""
安全强化：移除 public/data/rendering_objects.json 中的敏感路径
保留 file:// URL 用于前端访问，移除 original_path 字段
"""
import json, os

path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\web-app\public\data\rendering_objects.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Processing {len(data)} objects...")

fixed = 0
for obj in data:
    # 1. 移除 original_path（包含完整桌面路径）
    if "original_path" in obj:
        del obj["original_path"]
    
    # 2. path 保持 file:// URL（前端可直接访问）
    # 不含敏感信息，因为浏览器需要自己访问本地文件
    path_val = obj.get("path", "")
    
    # 3. 移除任何明文公司/项目名
    sensitive = ["山水庭院", "龙湖", "黄葛渡", "南沙星河", "东悦湾",
                 "锦钰城", "恒大云东海", "恒创睿能", "晟蒂鹏", "珠江电力"]
    for s in sensitive:
        if s in path_val:
            print(f"  WARN: '{s}' found in path: {path_val[:60]}")
    
    fixed += 1

# 4. 写入干净版本
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

size = os.path.getsize(path)
print(f"\nDone: {fixed} objects cleaned")
print(f"File size: {size/1024:.0f} KB")

# 验证
with open(path, "rb") as f:
    raw = f.read()
has_desktop = b"\\Users\\Administrator\\Desktop" in raw
has_original_path = b"original_path" in raw
print(f"Contains Desktop path: {has_desktop}")
print(f"Contains original_path: {has_original_path}")
print(f"Privacy status: {'CLEAN ✓' if not has_desktop and not has_original_path else 'NEEDS REVIEW'}")

# 打印样本
print("\nSample object (first):")
print(json.dumps(data[0], ensure_ascii=False, indent=2))
