# -*- coding: utf-8 -*-
"""
数据全面盘点 + 世界模型数据整合
"""
import json, os

BASE = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai"
PROJ = os.path.join(BASE, "data", "processed")
KB = os.path.join(BASE, "knowledge")

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== 1. 盘点各数据源 ======
print("=== Data Inventory ===")

vr_data = load_json(os.path.join(KB, "VR_KNOWLEDGE.json"))
print(f"VR_KNOWLEDGE: {len(vr_data.get('raw_vr',[]))} VRs")

bb = load_json(os.path.join(KB, "BENBANG_PROJECTS.json"))
print(f"BENBANG_PROJECTS: {len(bb) if bb else 0} projects")

jr = load_json(os.path.join(KB, "JINRUI_ARCHITECTURE.json"))
print(f"JINRUI: {len(jr.get('buildings',[])) if jr else 0} buildings")

prj = load_json(os.path.join(PROJ, "projects.json"))
print(f"projects.json: {len(prj) if prj else 0} projects")

sg = load_json(os.path.join(PROJ, "cleaned", "scene_graph_real.json"))
print(f"scene_graph_real: {sg.get('num_nodes', 0) if sg else 0} nodes, {len(sg.get('all_relations',[])) if sg else 0} relations")

lt = load_json(os.path.join(KB, "LIGHTING_DATABASE.json"))
print(f"LIGHTING_DATABASE: {len(lt) if isinstance(lt, list) else 'dict'} items")

# ====== 2. 构建世界模型 ======
print("\n=== Building World Model ===")

world_model = {
    "version": "1.0",
    "generated": "2026-04-14",
    "summary": {
        "total_scenes": 0,
        "categories": {}
    },
    "scenes": [],
    "physical_objects": [],
    "relationships": []
}

def add_scene(category, name, scene_type, source, extra=None):
    sid = len(world_model["scenes"])
    scene = {"id": f"scene_{sid:04d}", "type": scene_type, "category": category,
             "name": name, "source": source}
    if extra:
        scene.update(extra)
    world_model["scenes"].append(scene)
    cat = scene["category"]
    world_model["summary"]["categories"][cat] = world_model["summary"]["categories"].get(cat, 0) + 1
    world_model["summary"]["total_scenes"] += 1
    return scene

# VR场景 (105个)
if isinstance(vr_data, dict):
    for vr in vr_data.get("raw_vr", []):
        if isinstance(vr, dict):
            add_scene(
                vr.get("category", "interior"), vr.get("name", ""),
                "vr_scene", "VR_KNOWLEDGE",
                {"url": vr.get("url",""), "style": vr.get("style",""),
                 "materials": vr.get("materials",[]), "room_type": vr.get("room_type","")}
            )

# 本邦项目 (33个)
if bb:
    for p in bb:
        add_scene(p.get("category","engineering"), p.get("name",""),
                  "engineering_project", "广州本邦工程顾问",
                  {"location": p.get("location",""), "tags": p.get("tags",[])})

# 锦钰城 (9个楼栋)
if jr:
    for b in jr.get("buildings", []):
        add_scene("residential", b.get("name",""),
                  "building", "锦钰城",
                  {"floors": b.get("floors",""), "units": b.get("units",""), "area": b.get("area","")})

# projects.json
if prj:
    for p in prj:
        add_scene(p.get("type","unknown"), p.get("name",""),
                  "project", "desktop_db",
                  {"location": p.get("location","")})

# scene_graph_real: 物理对象 (151个门/窗)
if sg and isinstance(sg, dict):
    node_names = sg.get("node_names", [])
    node_types = sg.get("node_types", [])
    node_features = sg.get("node_features", [])
    node_positions = sg.get("node_positions", [])

    for i in range(len(node_names)):
        obj = {
            "id": node_names[i] if i < len(node_names) else f"node_{i}",
            "type": node_types[i] if i < len(node_types) else "unknown",
            "features": node_features[i] if i < len(node_features) else [],
            "position": node_positions[i] if i < len(node_positions) else [],
            "source": "spatial_inference"
        }
        world_model["physical_objects"].append(obj)

    # 空间关系
    for rel in sg.get("all_relations", []):
        if isinstance(rel, dict):
            world_model["relationships"].append({
                "id": f"edge_{len(world_model['relationships'])}",
                "source": node_names[rel.get("node_i",0)] if rel.get("node_i",0) < len(node_names) else f"node_{rel.get('node_i',0)}",
                "target": node_names[rel.get("node_j",0)] if rel.get("node_j",0) < len(node_names) else f"node_{rel.get('node_j',0)}",
                "type": rel.get("relation","spatial"),
                "distance": rel.get("distance",0),
                "direction": rel.get("direction",""),
                "same_room": rel.get("relation","") == "same_room",
                "source": "spatial_inference"
            })

# ====== 3. 保存 ======
out_path = os.path.join(PROJ, "world_model_catalog.json")
save_json(out_path, world_model)

print(f"\nTotal scenes: {world_model['summary']['total_scenes']}")
print(f"Physical objects: {len(world_model['physical_objects'])}")
print(f"Spatial relations: {len(world_model['relationships'])}")
print(f"\nCategories:")
for cat, n in sorted(world_model["summary"]["categories"].items(), key=lambda x: -x[1]):
    print(f"  {cat}: {n}")
print(f"\nSaved: {out_path}")

# ====== 4. 场景类型映射 ======
scene_types = {}
for scene in world_model["scenes"]:
    cat = scene["category"]
    if cat not in scene_types:
        scene_types[cat] = []
    scene_types[cat].append({"id": scene["id"], "name": scene["name"], "type": scene["type"]})

type_map_path = os.path.join(PROJ, "scene_type_mapping.json")
save_json(type_map_path, scene_types)
print(f"Scene types: {type_map_path} ({len(scene_types)} categories)")
