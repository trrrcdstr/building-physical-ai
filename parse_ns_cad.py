# -*- coding: utf-8 -*-
"""
南沙星河东悦湾 CAD 图纸解析
解析DWG文件，提取建筑元素，生成世界模型数据
"""
import os
import sys
import json
import re
sys.stdout.reconfigure(encoding='utf-8')

try:
    import ezdxf
except ImportError:
    print("需要安装: pip install ezdxf")
    sys.exit(1)

BASE_NS = r'C:\Users\Administrator\Desktop\南沙星河东悦湾'
PROJ = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai'
OUT_DIR = os.path.join(PROJ, 'data', 'processed', 'ns_cad')
os.makedirs(OUT_DIR, exist_ok=True)

def find_dwg_files(base):
    """递归找所有DWG文件"""
    dwgs = []
    for root, dirs, files in os.walk(base):
        for f in sorted(files):
            if f.lower().endswith('.dwg'):
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, base)
                size = os.path.getsize(fp) / 1024
                dwgs.append((fp, rel, size))
    return sorted(dwgs, key=lambda x: -x[2])

def parse_dwg(fp):
    """解析单个DWG文件，返回关键信息"""
    try:
        doc = ezdxf.readfile(fp)
    except Exception as e:
        return {"error": str(e)}

    ms = doc.modelspace()
    
    # 提取所有图层
    layers = list(doc.layers)
    layer_info = []
    for layer in layers:
        if layer not in ('0', 'Defpoints'):
            color = doc.layers.get(layer).color if doc.layers.has_entry(layer) else 0
            layer_info.append({"name": layer, "color": color})
    
    # 统计实体类型
    entity_types = {}
    for e in ms:
        etype = e.dxftype()
        entity_types[etype] = entity_types.get(etype, 0) + 1
    
    # 提取文本（标题、尺寸标注）
    texts = []
    for e in ms:
        if e.dxftype() == 'TEXT':
            txt = e.dxf.text.strip() if hasattr(e.dxf, 'text') else ''
            if txt and len(txt) < 200:
                texts.append(txt)
        elif e.dxftype() == 'MTEXT':
            txt = e.text.strip() if hasattr(e, 'text') else ''
            if txt and len(txt) < 300:
                texts.append(txt[:200])
    
    # 提取房间/空间标注
    rooms = []
    for e in ms:
        if e.dxftype() == 'TEXT':
            txt = e.dxf.text if hasattr(e.dxf, 'text') else ''
            if txt and any(kw in txt for kw in ['室', '厅', '房', '卫', '厨', '间', '梯', '厅', '台']):
                if len(txt) < 50:
                    rooms.append(txt.strip())
    
    # 提取门、窗
    doors = []
    windows = []
    for e in ms:
        if e.dxftype() == 'INSERT':
            name = e.get_dxf_attrib('name', '')
            if '门' in str(name) or 'door' in str(name).lower():
                doors.append(str(name))
            if '窗' in str(name) or 'window' in str(name).lower():
                windows.append(str(name))
    
    # 提取主要尺寸
    dimensions = []
    for e in ms:
        if e.dxftype() == 'DIMENSION':
            try:
                dim_text = e.dxf.text if hasattr(e.dxf, 'text') else ''
                if dim_text:
                    dimensions.append(str(dim_text))
            except:
                pass
    
    return {
        "layers": layer_info,
        "entity_types": entity_types,
        "texts": texts[:30],  # 限制数量
        "rooms": list(set(rooms))[:20],
        "doors": list(set(doors))[:10],
        "windows": list(set(windows))[:10],
        "dimensions": dimensions[:10],
        "total_entities": sum(entity_types.values()),
    }

def extract_layer_entities(doc, layer_name):
    """提取某图层所有实体"""
    ms = doc.modelspace()
    entities = []
    for e in ms:
        if e.dxf.layer == layer_name:
            etype = e.dxftype()
            data = {"type": etype}
            if etype == 'LINE':
                data["start"] = (e.dxf.start.x, e.dxf.start.y)
                data["end"] = (e.dxf.end.x, e.dxf.end.y)
            elif etype == 'LWPOLYLINE' or etype == 'POLYLINE':
                pts = list(e.get_points())
                if pts:
                    data["points"] = [(p[0], p[1]) for p in pts[:20]]
            elif etype == 'TEXT':
                data["text"] = e.dxf.text if hasattr(e.dxf, 'text') else ''
                data["insert"] = (e.dxf.insert.x, e.dxf.insert.y)
            entities.append(data)
    return entities

# ─────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────
print("扫描南沙星河东悦湾 DWG 文件...")
dwg_files = find_dwg_files(BASE_NS)
print(f"共找到 {len(dwg_files)} 个DWG文件\n")

# 按专业分类
categories = {
    "建筑": [],
    "电气": [],
    "给排水": [],
    "暖通": [],
    "结构": [],
    "其他": []
}

cat_keywords = {
    "建筑": ["建筑", "底图", "平面图", "户型", "标准层", "配套"],
    "电气": ["电施", "消电", "弱电", "防雷", "照明", "充电桩", "电气"],
    "给排水": ["水图", "给排", "消火栓", "水施", "喷淋", "水专业"],
    "暖通": ["通风", "暖通", "防烟", "排烟", "空调"],
    "结构": ["结构", "梁配", "板配", "柱配", "钢筋", "混凝土"],
}

for fp, rel, size in dwg_files:
    cat = "其他"
    rel_lower = rel.lower()
    for c, kws in cat_keywords.items():
        if any(kw in rel for kw in kws):
            cat = c
            break
    categories[cat].append((fp, rel, size))

print("专业分类:")
for cat, files in categories.items():
    if files:
        print(f"  {cat}: {len(files)}个文件")
        for _, rel, size in files:
            print(f"    {size:.0f}KB {rel}")

# ─────────────────────────────────────────
# 解析关键文件
# ─────────────────────────────────────────
print("\n\n开始解析关键图纸...")

# 优先解析建筑底图和最大的几个文件
priority_files = []
for cat, files in categories.items():
    for fp, rel, size in files:
        if any(kw in rel for kw in ["建筑底图", "平面图", "通风图", "水图", "电施", "消电"]):
            priority_files.append((fp, rel, size, cat))

# 取最大的几个
priority_files = sorted(priority_files, key=lambda x: -x[2])[:6]

parsing_results = []
for fp, rel, size, cat in priority_files:
    print(f"\n解析 [{cat}] {rel} ({size:.0f}KB)...")
    try:
        result = parse_dwg(fp)
        result["category"] = cat
        result["file"] = rel
        result["size_kb"] = size
        parsing_results.append(result)
        
        print(f"  实体总数: {result.get('total_entities', 'N/A')}")
        print(f"  图层数: {len(result.get('layers', []))}")
        if result.get('rooms'):
            print(f"  房间标注: {result['rooms'][:5]}")
        if result.get('texts'):
            print(f"  文本样本: {result['texts'][:3]}")
    except Exception as e:
        print(f"  解析失败: {e}")

# ─────────────────────────────────────────
# 生成世界模型输入
# ─────────────────────────────────────────
print("\n\n生成世界模型数据...")

# 从解析结果提取建筑空间
world_rooms = []
for res in parsing_results:
    for room_name in res.get('rooms', []):
        if room_name and len(room_name) < 30:
            world_rooms.append({
                "source_file": res.get('file', ''),
                "category": res.get('category', ''),
                "room_name": room_name,
                "floor": "地下室",
                "building": "地块三",
                "project": "南沙星河东悦湾",
            })

# 去重
seen = set()
unique_rooms = []
for r in world_rooms:
    key = r['room_name']
    if key not in seen:
        seen.add(key)
        unique_rooms.append(r)

print(f"提取到 {len(unique_rooms)} 个房间/空间标注")

# 保存世界模型数据
wm_out = os.path.join(OUT_DIR, 'ns_world_model_input.json')
with open(wm_out, 'w', encoding='utf-8') as f:
    json.dump({
        "project": "南沙星河东悦湾",
        "source": "CAD施工图",
        "cad_files_parsed": len(parsing_results),
        "rooms": unique_rooms,
        "parsing_results": [{
            "file": r['file'],
            "category": r['category'],
            "size_kb": r['size_kb'],
            "total_entities": r.get('total_entities', 0),
            "layers_count": len(r.get('layers', [])),
            "rooms": r.get('rooms', []),
            "doors": r.get('doors', []),
            "windows": r.get('windows', []),
            "dimensions_sample": r.get('dimensions', [])[:5],
        } for r in parsing_results if 'error' not in r]
    }, f, ensure_ascii=False, indent=2)

print(f"数据已保存: {wm_out}")

# ─────────────────────────────────────────
# 导出为3D世界模型可用的格式
# ─────────────────────────────────────────
print("\n生成3D场景配置...")

# 创建简化的建筑场景数据（供Three.js使用）
scene_config = {
    "project": "南沙星河东悦湾",
    "type": "basement_parking",
    "floor": "地块三地下室",
    "area_sqm": "约20000",  # 估算
    "rooms": [r['room_name'] for r in unique_rooms],
    "disciplines": list(categories.keys()),
    "cad_layers": {}
}

for res in parsing_results:
    if 'error' in res:
        continue
    scene_config["cad_layers"][res['file']] = {
        "layers": [l['name'] for l in res.get('layers', []) if l['name']],
        "entity_count": res.get('total_entities', 0),
    }

scene_out = os.path.join(OUT_DIR, 'ns_scene_config.json')
with open(scene_out, 'w', encoding='utf-8') as f:
    json.dump(scene_config, f, ensure_ascii=False, indent=2)
print(f"场景配置已保存: {scene_out}")

# 生成合并报告
print("\n\n" + "="*50)
print("南沙星河东悦湾 CAD 解析报告")
print("="*50)
print(f"DWG文件总数: {len(dwg_files)}")
print(f"总大小: {sum(s for _, _, s in dwg_files):.0f} KB")
print(f"\n已解析关键文件: {len(parsing_results)}")
for res in parsing_results:
    if 'error' not in res:
        print(f"\n[{res['category']}] {res['file']}")
        print(f"  实体: {res.get('total_entities', 0)}, 图层: {len(res.get('layers', []))}")
        rooms = res.get('rooms', [])
        if rooms:
            print(f"  房间: {rooms[:8]}")
print(f"\n数据输出: {OUT_DIR}")
