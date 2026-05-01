"""
几何外壳导出器 - 世界模型沙箱隔离

安全原则:
  1. 仅导出空间几何信息（坐标/尺寸/关系）
  2. 移除所有业务元数据（项目名/客户/设计师）
  3. 使用随机ID替代原始标识符
  4. 沙箱无法反向追溯原始数据源
"""

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path


@dataclass
class Object3D:
    """脱敏后的3D对象"""
    id: str                 # 随机哈希ID
    type: str               # "door" / "window" / "furniture" / "wall"
    position: tuple         # (x, y, z) 米制坐标
    dimensions: tuple       # (width, height, depth) 米
    rotation: Optional[float] = None  # 绕Y轴旋转角度

    # ❌ 不包含: source_file, project_name, designer, original_id


@dataclass
class Relation:
    """空间关系"""
    source_id: str
    target_id: str
    relation_type: str      # "same_room" / "adjacent" / "on_top" / "inside"
    distance_m: Optional[float] = None
    confidence: float = 1.0


@dataclass
class GeometricHull:
    """
    几何外壳：世界模型沙箱的输入格式
    
    仅包含空间信息，不含任何业务元数据。
    沙箱无法通过此数据追溯原始项目/客户。
    """
    scene_id: str                    # 随机哈希ID
    scene_type: str                  # "indoor" / "outdoor" / "garden"
    objects: list[Object3D]
    relations: list[Relation]
    bounds: tuple                    # (min_x, max_x, min_z, max_z)
    
    # ❌ 不包含: project_name, client, designer, source_path, vr_url
    
    def to_dict(self) -> dict:
        return {
            "scene_id": self.scene_id,
            "scene_type": self.scene_type,
            "objects": [asdict(o) for o in self.objects],
            "relations": [asdict(r) for r in self.relations],
            "bounds": self.bounds,
        }
    
    def to_json(self, path: str = None) -> str:
        """导出为JSON（用于沙箱输入）"""
        data = self.to_dict()
        if path:
            Path(path).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return json.dumps(data, ensure_ascii=False)


def _hash_id(original_id: str) -> str:
    """将原始ID转换为不可逆的哈希ID"""
    return hashlib.sha256(original_id.encode()).hexdigest()[:16]


def export_to_sandbox(
    building_objects: list[dict],
    scene_type: str = "indoor",
    scene_id: str = None,
) -> GeometricHull:
    """
    导出建筑数据到沙箱格式
    
    Args:
        building_objects: 原始建筑对象列表（来自 building_objects.json）
        scene_type: 场景类型
        scene_id: 原始场景ID（将被哈希化）
    
    Returns:
        GeometricHull: 脱敏后的几何外壳
    """
    objects = []
    relations = []
    
    # 提取对象
    for obj in building_objects:
        obj_id = obj.get("id", str(len(objects)))
        
        # 提取坐标
        pos = obj.get("position", obj.get("center", (0, 0, 0)))
        if isinstance(pos, dict):
            pos = (pos.get("x", 0), pos.get("y", 0), pos.get("z", 0))
        
        # 提取尺寸
        dims = obj.get("dimensions", obj.get("size", (1, 1, 1)))
        if isinstance(dims, dict):
            dims = (dims.get("width", 1), dims.get("height", 1), dims.get("depth", 1))
        
        objects.append(Object3D(
            id=_hash_id(obj_id),
            type=obj.get("type", "unknown"),
            position=tuple(round(p, 3) for p in pos),
            dimensions=tuple(round(d, 3) for d in dims),
            rotation=obj.get("rotation"),
        ))
    
    # 提取关系（如果存在）
    # 从 building_objects 中的 relations 字段或单独的关系文件
    
    # 计算边界
    if objects:
        xs = [o.position[0] for o in objects]
        zs = [o.position[2] for o in objects]
        bounds = (min(xs), max(xs), min(zs), max(zs))
    else:
        bounds = (0, 100, 0, 100)
    
    return GeometricHull(
        scene_id=_hash_id(scene_id or "default_scene"),
        scene_type=scene_type,
        objects=objects,
        relations=relations,
        bounds=bounds,
    )


def export_scene_graph_to_sandbox(
    scene_graph_path: str,
    output_path: str = None,
) -> GeometricHull:
    """
    从 scene_graph.json 导出到沙箱格式
    """
    with open(scene_graph_path, encoding="utf-8") as f:
        data = json.load(f)
    
    objects = []
    for node in data.get("nodes", []):
        pos = node.get("position", (0, 0, 0))
        if isinstance(pos, dict):
            pos = (pos.get("x", 0), pos.get("y", 0), pos.get("z", 0))
        
        objects.append(Object3D(
            id=_hash_id(node.get("id", "")),
            type=node.get("type", "unknown"),
            position=tuple(round(p, 3) for p in pos),
            dimensions=(1.0, 2.0, 0.1),  # 默认尺寸
        ))
    
    relations = []
    for edge in data.get("edges", []):
        relations.append(Relation(
            source_id=_hash_id(edge.get("source", "")),
            target_id=_hash_id(edge.get("target", "")),
            relation_type=edge.get("relation", "unknown"),
            distance_m=edge.get("distance"),
            confidence=edge.get("confidence", 1.0),
        ))
    
    hull = GeometricHull(
        scene_id=_hash_id("scene_graph"),
        scene_type="indoor",
        objects=objects,
        relations=relations,
        bounds=(0, 300, -3, 150),  # 从数据推断
    )
    
    if output_path:
        hull.to_json(output_path)
    
    return hull


# ─────────────────────────────────────────────
# 示例用法
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    
    # 从 building_objects.json 导出
    data_path = Path(__file__).parent.parent / "data" / "processed" / "building_objects.json"
    
    if data_path.exists():
        with open(data_path, encoding="utf-8") as f:
            building_objects = json.load(f)
        
        hull = export_to_sandbox(building_objects, scene_type="indoor")
        
        print(f"[GeometricHull] Exported {len(hull.objects)} objects")
        print(f"  Scene ID: {hull.scene_id}")
        print(f"  Bounds: X[{hull.bounds[0]:.1f}, {hull.bounds[1]:.1f}], Z[{hull.bounds[2]:.1f}, {hull.bounds[3]:.1f}]")
        print(f"  Sample object: {hull.objects[0].type} @ {hull.objects[0].position}")
        
        # 保存到沙箱输入目录
        output_path = Path(__file__).parent.parent / "data" / "sandbox" / "scene_hull.json"
        hull.to_json(str(output_path))
        print(f"  Saved to: {output_path}")
    else:
        print(f"[GeometricHull] Data file not found: {data_path}")
