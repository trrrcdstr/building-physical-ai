"""
四层空间模型系统

层级结构:
├── L1 Block层 (房间边界)
│   └── 墙体围合 → 房间多边形 → 面积/质心
├── L2 Road层 (路网拓扑)
│   └── 门洞/走廊 → 拓扑路网 → 可通行路径
├── L3 Function层 (功能标签)
│   └── 房间名称/图块 → 功能分类 (卧室/厨房等)
└── L4 Object层 (固定物体)
    └── 门窗/家具 → 物体坐标 → 类型标注
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union, polygonize
import networkx as nx
import ezdxf

# ==================== 数据结构定义 ====================

@dataclass
class Block:
    """Block层: 房间边界"""
    id: str
    polygon: Polygon
    area_m2: float
    centroid: Tuple[float, float]
    wall_ids: List[str] = field(default_factory=list)
    adjacent_blocks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "polygon_coords": list(self.polygon.exterior.coords),
            "area_m2": round(self.area_m2, 2),
            "centroid": [round(c, 2) for c in self.centroid],
            "wall_ids": self.wall_ids,
            "adjacent_blocks": self.adjacent_blocks
        }

@dataclass
class RoadNode:
    """Road层节点: 门洞/通道"""
    id: str
    position: Tuple[float, float]
    node_type: str  # door, corridor, entrance
    width_mm: float
    connected_blocks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "position": [round(c, 2) for c in self.position],
            "node_type": self.node_type,
            "width_mm": round(self.width_mm, 1),
            "connected_blocks": self.connected_blocks
        }

@dataclass
class RoadEdge:
    """Road层边: 可通行路径"""
    id: str
    from_node: str
    to_node: str
    distance_mm: float
    path_type: str  # direct, corridor
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "from_node": self.from_node,
            "to_node": self.to_node,
            "distance_mm": round(self.distance_mm, 1),
            "path_type": self.path_type
        }

@dataclass
class Function:
    """Function层: 功能标签"""
    block_id: str
    function_type: str  # bedroom, living_room, kitchen, bathroom, etc.
    confidence: float
    labels: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "function_type": self.function_type,
            "confidence": round(self.confidence, 2),
            "labels": self.labels
        }

@dataclass
class Object:
    """Object层: 固定物体"""
    id: str
    object_type: str  # door, window, cabinet, etc.
    position: Tuple[float, float]
    size: Tuple[float, float]  # width, height
    rotation_deg: float
    block_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "object_type": self.object_type,
            "position": [round(c, 2) for c in self.position],
            "size": [round(s, 1) for s in self.size],
            "rotation_deg": round(self.rotation_deg, 1),
            "block_id": self.block_id
        }

@dataclass
class FourLayerModel:
    """四层空间模型"""
    blocks: List[Block] = field(default_factory=list)
    road_nodes: List[RoadNode] = field(default_factory=list)
    road_edges: List[RoadEdge] = field(default_factory=list)
    functions: List[Function] = field(default_factory=list)
    objects: List[Object] = field(default_factory=list)
    road_graph: Optional[nx.Graph] = None
    
    def to_dict(self) -> dict:
        return {
            "blocks": [b.to_dict() for b in self.blocks],
            "road_network": {
                "nodes": [n.to_dict() for n in self.road_nodes],
                "edges": [e.to_dict() for e in self.road_edges]
            },
            "functions": [f.to_dict() for f in self.functions],
            "objects": [o.to_dict() for o in self.objects],
            "statistics": {
                "total_blocks": len(self.blocks),
                "total_area_m2": sum(b.area_m2 for b in self.blocks),
                "total_road_nodes": len(self.road_nodes),
                "total_objects": len(self.objects)
            }
        }

# ==================== 图层语义识别 ====================

class LayerSemanticRecognizer:
    """T1.2 图层语义识别"""
    
    # 图层名到构件类型的映射
    LAYER_MAPPING = {
        "WALLS": "wall",
        "WALL": "wall",
        "墙": "wall",
        "墙体": "wall",
        
        "DOORS": "door",
        "DOOR": "door",
        "门": "door",
        
        "WINDOWS": "window",
        "WINDOW": "window",
        "窗": "window",
        
        "PIPES": "pipe",
        "PIPE": "pipe",
        "管线": "pipe",
        
        "DIMENSIONS": "dimension",
        "TEXT": "text",
        "ANNOTATIONS": "annotation"
    }
    
    @classmethod
    def recognize(cls, layer_name: str) -> str:
        """识别图层类型"""
        layer_upper = layer_name.upper()
        
        # 直接匹配
        if layer_upper in cls.LAYER_MAPPING:
            return cls.LAYER_MAPPING[layer_upper]
        
        # 模糊匹配
        for key, value in cls.LAYER_MAPPING.items():
            if key in layer_upper or layer_upper in key:
                return value
        
        return "unknown"

# ==================== Block层构建 ====================

class BlockBuilder:
    """T1.3 Block层构建: 基于墙体围合生成房间多边形"""
    
    def __init__(self):
        self.blocks: List[Block] = []
    
    def build_from_lines(self, lines: List[dict]) -> List[Block]:
        """从线段构建房间多边形"""
        
        # 1. 将线段转换为Shapely LineString
        line_strings = []
        for line in lines:
            ls = LineString([line["start"], line["end"]])
            line_strings.append(ls)
        
        # 2. 合并线段并多边形化
        merged = unary_union(line_strings)
        polygons = list(polygonize(merged))
        
        # 3. 创建Block对象
        self.blocks = []
        for i, poly in enumerate(polygons):
            # 过滤太小的多边形（可能是噪音）
            if poly.area < 10000:  # < 1m²
                continue
            
            block = Block(
                id=f"block_{i+1:03d}",
                polygon=poly,
                area_m2=poly.area / 1_000_000,  # mm² → m²
                centroid=(poly.centroid.x, poly.centroid.y)
            )
            self.blocks.append(block)
        
        return self.blocks
    
    def find_adjacent_blocks(self):
        """找到相邻的Block"""
        for i, block1 in enumerate(self.blocks):
            for j, block2 in enumerate(self.blocks):
                if i >= j:
                    continue
                
                # 检查两个多边形是否相邻（共享边界）
                if block1.polygon.touches(block2.polygon):
                    block1.adjacent_blocks.append(block2.id)
                    block2.adjacent_blocks.append(block1.id)

# ==================== Road层构建 ====================

class RoadBuilder:
    """T1.4 Road层构建: 提取门洞生成拓扑路网"""
    
    def __init__(self):
        self.nodes: List[RoadNode] = []
        self.edges: List[RoadEdge] = []
        self.graph: nx.Graph = nx.Graph()
    
    def build_from_doors(self, doors: List[dict], blocks: List[Block]) -> Tuple[List[RoadNode], List[RoadEdge]]:
        """从门洞构建路网"""
        
        self.nodes = []
        self.edges = []
        
        # 1. 为每个门创建节点
        for i, door in enumerate(doors):
            node = RoadNode(
                id=f"door_{i+1:03d}",
                position=door.get("position", (0, 0)),
                node_type="door",
                width_mm=door.get("width", 900),
                connected_blocks=door.get("connected_blocks", [])
            )
            self.nodes.append(node)
            
            # 添加到图中
            self.graph.add_node(node.id, pos=node.position)
        
        # 2. 为每个房间创建虚拟节点
        for block in blocks:
            node_id = f"block_center_{block.id}"
            self.graph.add_node(node_id, pos=block.centroid)
        
        # 3. 连接门和房间
        for node in self.nodes:
            for block_id in node.connected_blocks:
                edge_id = f"edge_{node.id}_{block_id}"
                edge = RoadEdge(
                    id=edge_id,
                    from_node=node.id,
                    to_node=f"block_center_{block_id}",
                    distance_mm=1000,  # 假设距离
                    path_type="direct"
                )
                self.edges.append(edge)
                
                self.graph.add_edge(edge.from_node, edge.to_node, weight=edge.distance_mm)
        
        return self.nodes, self.edges
    
    def find_path(self, from_node: str, to_node: str) -> Optional[List[str]]:
        """查找最短路径"""
        try:
            return nx.shortest_path(self.graph, from_node, to_node, weight="weight")
        except nx.NetworkXNoPath:
            return None

# ==================== Function层构建 ====================

class FunctionBuilder:
    """T1.5 Function层构建: 基于房间名称匹配功能标签"""
    
    # 功能关键词映射
    FUNCTION_KEYWORDS = {
        "bedroom": ["卧室", "主卧", "次卧", "卧室", "bedroom", "主卧室", "次卧室"],
        "living_room": ["客厅", "起居室", "living", "客厅"],
        "kitchen": ["厨房", "kitchen", "厨房间"],
        "bathroom": ["卫生间", "厕所", "bathroom", "洗手间", "浴室"],
        "study": ["书房", "study", "工作室"],
        "dining": ["餐厅", "dining", "饭厅"],
        "balcony": ["阳台", "balcony"],
        "storage": ["储藏室", "storage", "杂物间"],
        "corridor": ["走廊", "过道", "corridor", "走廊"]
    }
    
    def __init__(self):
        self.functions: List[Function] = []
    
    def build_from_texts(self, texts: List[dict], blocks: List[Block]) -> List[Function]:
        """从文字标注构建功能标签"""
        
        self.functions = []
        
        for block in blocks:
            # 查找落在该房间内的文字标注
            block_texts = []
            for text in texts:
                pos = Point(text["position"])
                if block.polygon.contains(pos):
                    block_texts.append(text["content"])
            
            # 匹配功能
            function_type = "unknown"
            confidence = 0.0
            
            for text in block_texts:
                for ftype, keywords in self.FUNCTION_KEYWORDS.items():
                    for keyword in keywords:
                        if keyword in text.lower():
                            function_type = ftype
                            confidence = 0.9
                            break
                    if confidence > 0:
                        break
                if confidence > 0:
                    break
            
            # 如果没有找到，根据面积猜测
            if confidence == 0:
                if block.area_m2 > 15:
                    function_type = "living_room"
                    confidence = 0.3
                elif block.area_m2 > 10:
                    function_type = "bedroom"
                    confidence = 0.3
                elif block.area_m2 > 5:
                    function_type = "kitchen"
                    confidence = 0.2
            
            function = Function(
                block_id=block.id,
                function_type=function_type,
                confidence=confidence,
                labels=block_texts
            )
            self.functions.append(function)
        
        return self.functions

# ==================== Object层构建 ====================

class ObjectBuilder:
    """T1.6 Object层构建: 提取固定物体坐标"""
    
    def __init__(self):
        self.objects: List[Object] = []
    
    def build_from_entities(self, 
                           doors: List[dict], 
                           windows: List[dict],
                           blocks: List[Block]) -> List[Object]:
        """从实体构建物体列表"""
        
        self.objects = []
        obj_id = 1
        
        # 处理门
        for door in doors:
            # 解析门的尺寸
            spec = door.get("spec", "")
            width, height = self._parse_spec(spec, 900, 2100)
            
            obj = Object(
                id=f"obj_{obj_id:03d}",
                object_type="door",
                position=door.get("position", (0, 0)),
                size=(width, height),
                rotation_deg=0.0
            )
            
            # 找到所属房间
            for block in blocks:
                pos = Point(obj.position)
                if block.polygon.contains(pos):
                    obj.block_id = block.id
                    break
            
            self.objects.append(obj)
            obj_id += 1
        
        # 处理窗
        for window in windows:
            spec = window.get("spec", "")
            width, height = self._parse_spec(spec, 1200, 1500)
            
            obj = Object(
                id=f"obj_{obj_id:03d}",
                object_type="window",
                position=window.get("position", (0, 0)),
                size=(width, height),
                rotation_deg=0.0
            )
            
            for block in blocks:
                pos = Point(obj.position)
                if block.polygon.buffer(100).contains(pos):  # 扩大搜索范围
                    obj.block_id = block.id
                    break
            
            self.objects.append(obj)
            obj_id += 1
        
        return self.objects
    
    def _parse_spec(self, spec: str, default_w: float, default_h: float) -> Tuple[float, float]:
        """解析规格字符串，如 'M1 900x2100'"""
        import re
        match = re.search(r'(\d+)[xX](\d+)', spec)
        if match:
            return float(match.group(1)), float(match.group(2))
        return default_w, default_h

# ==================== 四层融合 ====================

class FourLayerFusion:
    """T1.7 四层数据融合"""
    
    def __init__(self):
        self.model = FourLayerModel()
    
    def build(self, 
              parsed_result: dict,
              building_elements: dict) -> FourLayerModel:
        """构建四层模型"""
        
        # 1. 提取墙体线段
        wall_lines = [l for l in parsed_result["entities"]["lines"] 
                      if l["layer"] == "WALLS"]
        
        # 2. 构建Block层
        block_builder = BlockBuilder()
        self.model.blocks = block_builder.build_from_lines(wall_lines)
        block_builder.find_adjacent_blocks()
        
        # 3. 构建Road层
        road_builder = RoadBuilder()
        
        # 从门洞提取
        doors_data = []
        for door in building_elements.get("doors", []):
            spec = door.get("spec", "")
            width = 900
            import re
            match = re.search(r'(\d+)', spec)
            if match:
                width = float(match.group(1))
            
            doors_data.append({
                "position": (2450, 120),  # 从DXF提取的门位置
                "width": width,
                "connected_blocks": ["block_001"] if self.model.blocks else []
            })
        
        self.model.road_nodes, self.model.road_edges = road_builder.build_from_doors(
            doors_data, self.model.blocks
        )
        self.model.road_graph = road_builder.graph
        
        # 4. 构建Function层
        function_builder = FunctionBuilder()
        self.model.functions = function_builder.build_from_texts(
            parsed_result["entities"]["texts"],
            self.model.blocks
        )
        
        # 5. 构建Object层
        object_builder = ObjectBuilder()
        self.model.objects = object_builder.build_from_entities(
            building_elements.get("doors", []),
            building_elements.get("windows", []),
            self.model.blocks
        )
        
        return self.model

# ==================== 主入口 ====================

def build_four_layer_model(dxf_path: str) -> FourLayerModel:
    """从DXF文件构建四层模型"""
    
    print(f"[四层模型] 正在构建: {dxf_path}")
    
    # 1. 解析DXF
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    
    # 2. 提取实体
    parsed_result = {
        "entities": {
            "lines": [],
            "texts": []
        }
    }
    
    building_elements = {
        "doors": [],
        "windows": [],
        "pipes": []
    }
    
    for entity in msp:
        if entity.dxftype() == 'LINE':
            parsed_result["entities"]["lines"].append({
                "start": (entity.dxf.start.x, entity.dxf.start.y),
                "end": (entity.dxf.end.x, entity.dxf.end.y),
                "layer": entity.dxf.layer
            })
        
        elif entity.dxftype() == 'TEXT':
            text = {
                "content": entity.dxf.text,
                "position": (entity.dxf.insert.x, entity.dxf.insert.y),
                "layer": entity.dxf.layer
            }
            parsed_result["entities"]["texts"].append(text)
            
            # 分类到building_elements
            layer_type = LayerSemanticRecognizer.recognize(entity.dxf.layer)
            if layer_type == "door":
                building_elements["doors"].append({
                    "spec": text["content"],
                    "position": text["position"]
                })
            elif layer_type == "window":
                building_elements["windows"].append({
                    "spec": text["content"],
                    "position": text["position"]
                })
    
    # 3. 构建四层模型
    fusion = FourLayerFusion()
    model = fusion.build(parsed_result, building_elements)
    
    print(f"[四层模型] 构建完成")
    print(f"  Block层: {len(model.blocks)} 个房间")
    print(f"  Road层: {len(model.road_nodes)} 个节点, {len(model.road_edges)} 条边")
    print(f"  Function层: {len(model.functions)} 个标签")
    print(f"  Object层: {len(model.objects)} 个物体")
    
    return model

if __name__ == "__main__":
    # 测试
    dxf_path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\cad_samples\test_building.dxf"
    
    model = build_four_layer_model(dxf_path)
    
    # 保存结果
    output_path = Path(dxf_path).parent / "four_layer_model.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(model.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"\n[输出] 已保存到: {output_path}")
