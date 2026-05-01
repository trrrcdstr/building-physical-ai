"""
L4 双模型协同 - 场景图构建器
将建筑对象（门/窗/墙/家具）组织为语义场景图，支持空间关系推理
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional


class SceneGraphBuilder:
    """
    场景图构建器：将建筑对象构建为图结构

    图结构：
    - 节点：建筑对象（门/窗/墙/家具）
    - 边：空间关系（same_room / adjacent / connects / contains）
    - 属性：位置/尺寸/类型/材质
    """

    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: list[dict] = []
        self.adjacency: dict[str, dict[str, str]] = {}

    def add_node(
        self,
        node_id: str,
        node_type: str,          # door / window / wall / furniture / appliance
        position: dict,            # {"x", "y", "z"}
        dimensions: dict,          # {"width", "height", "depth"}
        room_id: str = None,
        material: str = None,
        properties: dict = None,
    ):
        """添加节点"""
        geo_features = self._compute_geo_features(position, dimensions)
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "position": position,
            "dimensions": dimensions,
            "room_id": room_id,
            "material": material,
            "properties": properties or {},
            "geo_features": geo_features,
        }

    @staticmethod
    def _compute_geo_features(position: dict, dimensions: dict) -> list[float]:
        """计算9维几何特征向量"""
        x = position.get("x", 0)
        z = position.get("z", 0)
        w = dimensions.get("width", 1)
        h = dimensions.get("height", 2)
        area = w * h
        aspect = w / max(h, 0.01)
        return [
            x / 300.0,                  # 归一化X
            z / 100.0,                  # 归一化Z
            w / 3.0,                    # 归一化宽度
            h / 4.0,                    # 归一化高度
            area / 12.0,                # 归一化面积
            aspect,                     # 宽高比
            x * z / 30000.0,            # 位置乘积
            min(w, h) / max(w, h, 0.01),  # 最小/最大比
            1.0 if w > 1.5 else 0.0,   # 是否大门
        ]

    def add_edge(
        self,
        source: str,
        target: str,
        relation_type: str,
        confidence: float = 1.0,
        distance: float = None,
    ):
        """添加边"""
        if source not in self.nodes or target not in self.nodes:
            return
        edge = {
            "source": source,
            "target": target,
            "relation": relation_type,
            "confidence": round(float(confidence), 3),
            "distance_m": round(float(distance), 3) if distance is not None else None,
        }
        self.edges.append(edge)
        self.adjacency.setdefault(source, {})[target] = relation_type
        self.adjacency.setdefault(target, {})[source] = relation_type

    def build_from_building_objects(self, objects_path: str):
        """从建筑对象JSON构建场景图"""
        with open(objects_path, encoding="utf-8") as f:
            data = json.load(f)

        # 支持 {"objects": [...]} 或直接 [...]
        objects = data if isinstance(data, list) else data.get("objects", [])

        for obj in objects:
            obj_type = obj.get("type", "unknown")
            pos = obj.get("position", [])
            dims = obj.get("dimensions", {})
            # position 是 [x, y, z] 列表
            if isinstance(pos, list):
                px, py, pz = pos[0], pos[1], pos[2]
            else:
                px, py, pz = pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)
            # dimensions 是 {"width": ..., "height": ..., "depth": ...}
            dw = dims.get("width", 1) if isinstance(dims, dict) else 1
            dh = dims.get("height", 2) if isinstance(dims, dict) else 2
            dd = dims.get("depth", 0.2) if isinstance(dims, dict) else 0.2

            self.add_node(
                node_id=str(obj.get("id", f"{obj_type}_{len(self.nodes)}")),
                node_type=obj_type,
                position={"x": px, "y": py, "z": pz},
                dimensions={"width": dw, "height": dh, "depth": dd},
                room_id=obj.get("room"),
                material=obj.get("physics", {}).get("material") if isinstance(obj.get("physics"), dict) else None,
                properties={"name": obj.get("name"), "category": obj.get("category")},
            )

        self._infer_spatial_relations()
        print(f"[SceneGraphBuilder] Built graph: {len(self.nodes)} nodes, {len(self.edges)} edges")

    def _infer_spatial_relations(self, same_room_dist: float = 6.0, adjacent_dist: float = 15.0):
        """基于距离推断空间关系"""
        node_ids = list(self.nodes.keys())
        for i, n1 in enumerate(node_ids):
            for n2 in node_ids[i + 1:]:
                d = self._euclidean_distance(n1, n2)
                if d < same_room_dist:
                    conf = 1.0 - d / same_room_dist
                    self.add_edge(n1, n2, "same_room", confidence=conf, distance=d)
                elif d < adjacent_dist:
                    conf = 1.0 - (d - same_room_dist) / (adjacent_dist - same_room_dist)
                    self.add_edge(n1, n2, "adjacent", confidence=conf, distance=d)

    def _euclidean_distance(self, node1: str, node2: str) -> float:
        p1 = self.nodes[node1]["position"]
        p2 = self.nodes[node2]["position"]
        return float(np.sqrt((p1["x"] - p2["x"]) ** 2 + (p1["z"] - p2["z"]) ** 2))

    def get_neighbors(self, node_id: str, relation_type: str = None) -> list[dict]:
        """获取邻居节点"""
        if node_id not in self.adjacency:
            return []
        return [
            {"node_id": n, "relation": rel, **self.nodes[n]}
            for n, rel in self.adjacency[node_id].items()
            if relation_type is None or rel == relation_type
        ]

    def find_path(self, start: str, end: str, max_hops: int = 5) -> list[str]:
        """BFS寻路：查找两节点间的最短路径"""
        from collections import deque
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            current, path = queue.popleft()
            if current == end:
                return path
            if len(path) >= max_hops:
                continue
            for neighbor in self.adjacency.get(current, {}):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def get_subgraph(self, room_id: str) -> dict:
        """获取房间子图"""
        room_nodes = {nid: n for nid, n in self.nodes.items() if n.get("room_id") == room_id}
        room_edges = [e for e in self.edges if e["source"] in room_nodes and e["target"] in room_nodes]
        return {"nodes": room_nodes, "edges": room_edges, "node_count": len(room_nodes)}

    def to_dict(self) -> dict:
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
        }

    def summary(self) -> dict:
        types: dict[str, int] = {}
        for n in self.nodes.values():
            t = n["type"]
            types[t] = types.get(t, 0) + 1
        rel_counts: dict[str, int] = {}
        for e in self.edges:
            rel_counts[e["relation"]] = rel_counts.get(e["relation"], 0) + 1
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": types,
            "relation_types": rel_counts,
        }
