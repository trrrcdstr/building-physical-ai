# -*- coding: utf-8 -*-
import json, os, glob, sys
from collections import Counter

project_dir = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai"
catalog_path = os.path.join(project_dir, "data", "processed", "world_model_catalog.json")

print("="*60)
print("世界模型状态检查")
print("="*60)

# 1. 数据统计
if os.path.exists(catalog_path):
    with open(catalog_path, encoding="utf-8") as f:
        catalog = json.load(f)
    
    scenes = catalog.get("scenes", [])
    print(f"\n【场景总数】{len(scenes)}")
    
    # 按类型统计
    types = Counter(s.get("scene_type", "unknown") for s in scenes)
    print("\n【按类型】")
    for t, c in types.most_common():
        print(f"  {t}: {c}")
    
    # 按平台统计
    platforms = Counter()
    for s in scenes:
        url = s.get("vr_url", "")
        if "3d66" in url: p = "3d66"
        elif "justeasy" in url: p = "Justeasy"
        elif "720yun" in url: p = "720yun"
        elif "kujiale" in url: p = "酷家乐"
        elif url.endswith((".jpg", ".png", ".jpeg")): p = "图片"
        else: p = "其他"
        platforms[p] += 1
    
    print("\n【按平台】")
    for p, c in platforms.most_common():
        print(f"  {p}: {c}")
else:
    print(f"\n[错误] catalog 不存在: {catalog_path}")

# 2. 知识库统计
print("\n" + "="*60)
print("【知识库文件】")
knowledge_dir = os.path.join(project_dir, "knowledge")
if os.path.exists(knowledge_dir):
    for f in sorted(glob.glob(os.path.join(knowledge_dir, "*.json"))):
        size = os.path.getsize(f) / 1024
        print(f"  {os.path.basename(f)}: {size:.1f}KB")

# 3. 服务状态
print("\n" + "="*60)
print("【服务状态】")

# 检查端口
import subprocess
result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
lines = result.stdout.split("\n")
ports = {"3000": None, "5000": None}
for line in lines:
    for port in ports:
        if f":{port}" in line and "LISTENING" in line:
            parts = line.split()
            if parts:
                ports[port] = parts[-1]  # PID

print(f"  前端 (3000): {'PID ' + ports['3000'] if ports['3000'] else '未运行'}")
print(f"  推理 (5000): {'PID ' + ports['5000'] if ports['5000'] else '未运行'}")

# 4. 3D场景数据
print("\n" + "="*60)
print("【3D场景数据】")
data_dir = os.path.join(project_dir, "data", "processed")
files = {
    "scene_graph_real.json": os.path.join(data_dir, "scene_graph_real.json"),
    "link_data_real.json": os.path.join(data_dir, "cleaned", "link_data_real.json"),
    "scene_graph_training_clean.json": os.path.join(data_dir, "scene_graph_training_clean.json"),
}

for name, path in files.items():
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            print(f"  {name}: ✅ 存在, {len(data)}条记录")
        else:
            print(f"  {name}: ✅ 存在, {len(data)}个场景")
    else:
        print(f"  {name}: ❌ 不存在")

# 5. 前端代码
print("\n" + "="*60)
print("【前端关键文件】")
frontend_dir = os.path.join(project_dir, "web-app")
key_files = [
    "src/App.tsx",
    "src/scenes/RelationScene.tsx",
    "src/data/sceneData.ts",
]
for f in key_files:
    path = os.path.join(frontend_dir, f)
    if os.path.exists(path):
        size = os.path.getsize(path) / 1024
        print(f"  {f}: {size:.1f}KB")
    else:
        print(f"  {f}: ❌ 不存在")

print("\n" + "="*60)
