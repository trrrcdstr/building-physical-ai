"""
DXF解析测试
验证ezdxf能否正确读取生成的DXF文件
"""

import ezdxf
import json
from pathlib import Path
from typing import Dict, List, Any

def parse_dxf(dxf_path: str) -> Dict[str, Any]:
    """解析DXF文件"""
    
    print(f"[DXF解析器] 正在解析: {dxf_path}")
    
    # 读取DXF文件
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    
    # 解析结果
    result = {
        "file": dxf_path,
        "version": doc.dxfversion,
        "layers": [],
        "entities": {
            "lines": [],
            "arcs": [],
            "texts": [],
            "dimensions": []
        },
        "statistics": {
            "total_entities": 0,
            "by_layer": {}
        }
    }
    
    # 获取图层
    for layer in doc.layers:
        result["layers"].append({
            "name": layer.dxf.name,
            "color": layer.dxf.color,
            "locked": layer.is_locked()
        })
    
    # 遍历实体
    for entity in msp:
        result["statistics"]["total_entities"] += 1
        
        # 按图层统计
        layer_name = entity.dxf.layer
        result["statistics"]["by_layer"][layer_name] = \
            result["statistics"]["by_layer"].get(layer_name, 0) + 1
        
        # 按类型解析
        if entity.dxftype() == 'LINE':
            result["entities"]["lines"].append({
                "start": (entity.dxf.start.x, entity.dxf.start.y),
                "end": (entity.dxf.end.x, entity.dxf.end.y),
                "layer": entity.dxf.layer
            })
        
        elif entity.dxftype() == 'ARC':
            result["entities"]["arcs"].append({
                "center": (entity.dxf.center.x, entity.dxf.center.y),
                "radius": entity.dxf.radius,
                "start_angle": entity.dxf.start_angle,
                "end_angle": entity.dxf.end_angle,
                "layer": entity.dxf.layer
            })
        
        elif entity.dxftype() == 'TEXT':
            result["entities"]["texts"].append({
                "content": entity.dxf.text,
                "position": (entity.dxf.insert.x, entity.dxf.insert.y),
                "height": entity.dxf.height,
                "layer": entity.dxf.layer
            })
        
        elif entity.dxftype() == 'DIMENSION':
            result["entities"]["dimensions"].append({
                "layer": entity.dxf.layer
            })
    
    print(f"[DXF解析器] 解析完成")
    print(f"  图层: {len(result['layers'])} 个")
    print(f"  实体: {result['statistics']['total_entities']} 个")
    print(f"  直线: {len(result['entities']['lines'])} 条")
    print(f"  圆弧: {len(result['entities']['arcs'])} 条")
    print(f"  文字: {len(result['entities']['texts'])} 个")
    
    return result

def extract_building_elements(parse_result: Dict) -> Dict[str, Any]:
    """从解析结果中提取建筑构件"""
    
    elements = {
        "walls": [],
        "doors": [],
        "windows": [],
        "pipes": []
    }
    
    # 从WALLS图层提取墙体
    wall_lines = [l for l in parse_result["entities"]["lines"] 
                  if l["layer"] == "WALLS"]
    
    # 简化：将相邻的线段组合成墙体
    # 这里只是示例，实际需要更复杂的几何处理
    
    # 从DOORS图层提取门
    door_texts = [t for t in parse_result["entities"]["texts"] 
                  if t["layer"] == "DOORS"]
    for text in door_texts:
        if text["content"].startswith("M"):
            elements["doors"].append({
                "id": text["content"].split()[0],
                "spec": text["content"]
            })
    
    # 从WINDOWS图层提取窗
    window_texts = [t for t in parse_result["entities"]["texts"] 
                    if t["layer"] == "WINDOWS"]
    for text in window_texts:
        if text["content"].startswith("C"):
            elements["windows"].append({
                "id": text["content"].split()[0],
                "spec": text["content"]
            })
    
    # 从PIPES图层提取管线
    pipe_texts = [t for t in parse_result["entities"]["texts"] 
                  if t["layer"] == "PIPES"]
    for text in pipe_texts:
        elements["pipes"].append({
            "type": text["content"]
        })
    
    return elements

if __name__ == "__main__":
    dxf_path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\cad_samples\test_building.dxf"
    
    # 解析DXF
    parse_result = parse_dxf(dxf_path)
    
    # 提取建筑构件
    elements = extract_building_elements(parse_result)
    
    # 保存解析结果
    output_dir = Path(dxf_path).parent
    output_path = output_dir / "parsed_result.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "parse_result": parse_result,
            "building_elements": elements
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n[解析结果] 已保存到: {output_path}")
    
    # 打印建筑构件
    print("\n提取的建筑构件:")
    print(f"  门: {len(elements['doors'])} 个")
    for d in elements["doors"]:
        print(f"    - {d}")
    
    print(f"  窗: {len(elements['windows'])} 个")
    for w in elements["windows"]:
        print(f"    - {w}")
    
    print(f"  管线: {len(elements['pipes'])} 条")
    for p in elements["pipes"]:
        print(f"    - {p}")
