#!/usr/bin/env python3
"""验证 JSON 中文存储和文件可读性"""
import json, os

path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\web-app\public\data\rendering_objects.json"
with open(path, "rb") as f:
    raw = f.read()

print(f"File size: {len(raw)} bytes")
print(f"Objects: {len(json.loads(raw))}")

# 找中文 UTF-8 字节
chinese_terms = [b"\xe8\xae\xbe", b"\xe8\xae\xa1", b"\xe5\xae\xbd"]
found = sum(1 for t in chinese_terms if t in raw)
print(f"UTF-8 Chinese bytes found: {found}/{len(chinese_terms)}")

# 找 file:// 和 C:
idx1 = raw.find(b"file:///")
idx2 = raw.find(b"C:", idx1)
print(f"file:// at: {idx1}, C: at: {idx2}")
url_chunk = raw[idx1:idx2]
print(f"Between: {url_chunk}")

# 检查 json 解析后的数据
data = json.loads(raw)
first = data[0]
p = first["original_path"]
print(f"\nFirst original_path: {p}")
print(f"Path exists: {os.path.exists(p)}")

# 用 Windows API 直接读目录
import subprocess
r = subprocess.run(["cmd", "/c", "dir", "/b", r"C:\Users\Administrator\Desktop\设计数据库\室内效果图\办公"],
    capture_output=True)
print(f"\n真实目录内容 (cmd /c dir):\n{r.stdout[:200]}")
