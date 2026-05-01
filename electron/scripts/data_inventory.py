# -*- coding: utf-8 -*-
"""
数据全面盘点 + 分类整理
"""
import json, os, glob

BASE = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai"
PROJ = os.path.join(BASE, "data", "processed")

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except:
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                return json.load(f)
        except Exception as e:
            return None

# === 1. desktop_db_index ===
db = load_json(os.path.join(PROJ, "desktop_db_index.json"))
print(f"=== desktop_db_index ({len(db) if db else 0} 项) ===")
for i, p in enumerate(db or []):
    print(f"  {i+1}. [{p.get('type','?')}] {p.get('name','?')}")

# === 2. projects.json ===
prj = load_json(os.path.join(PROJ, "projects.json"))
print(f"\n=== projects.json ({len(prj) if prj else 0} 项) ===")
for i, p in enumerate(prj or []):
    print(f"  {i+1}. [{p.get('type','?')}] {p.get('name','?')}")

# === 3. VR知识库 ===
vr = load_json(os.path.join(BASE, "knowledge", "VR_KNOWLEDGE.json"))
print(f"\n=== VR知识库 ({len(vr) if vr else 0} 项) ===")
if vr:
    # 按source统计
    srcs = {}
    for v in vr:
        src = v.get('source', 'unknown')
        srcs[src] = srcs.get(src, 0) + 1
    for s, c in sorted(srcs.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c} VRs")
    # 按type统计
    types = {}
    for v in vr:
        t = v.get('type', '?')
        types[t] = types.get(t, 0) + 1
    for t, c in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  类型={t}: {c} VRs")

# === 4. 本邦项目 ===
bb = load_json(os.path.join(BASE, "knowledge", "BENBANG_PROJECTS.json"))
print(f"\n=== 广州本邦项目 ({len(bb) if bb else 0} 项) ===")
for i, p in enumerate(bb or []):
    print(f"  {i+1}. [{p.get('category','?')}] {p.get('name','?')}")

# === 5. 锦钰城 ===
jr = load_json(os.path.join(BASE, "knowledge", "JINRUI_ARCHITECTURE.json"))
print(f"\n=== 锦钰城建筑数据 ({len(jr.get('buildings',[])) if jr else 0} 栋楼) ===")
if jr:
    print(f"  项目: {jr.get('project_name','?')}")
    print(f"  楼栋: {[b.get('name','?') for b in jr.get('buildings',[])]}")

# === 6. 灯具库 ===
lt = load_json(os.path.join(BASE, "knowledge", "LIGHTING_DATABASE.json"))
print(f"\n=== 灯具数据库 ({len(lt) if lt else 0} 款) ===")

# === 7. raw目录 ===
print(f"\n=== data/raw 目录 ===")
for d in os.listdir(os.path.join(BASE, "data", "raw")):
    full = os.path.join(BASE, "data", "raw", d)
    if os.path.isdir(full):
        files = os.listdir(full)
        print(f"  {d}/ ({len(files)} files)")
        for f in files[:5]:
            print(f"    - {f}")

# === 8. 其他JSON文件 ===
print(f"\n=== world_model_input ===")
wmi = load_json(os.path.join(PROJ, "world_model_input.json"))
if wmi:
    print(f"  scenes: {len(wmi.get('scenes', []))}")
    print(f"  types: {list(wmi.keys())}")
