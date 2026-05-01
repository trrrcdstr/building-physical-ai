"""
scene_graph_builder.py — 场景图谱构建器
=========================================
将 VR 数据 + CAD 数据 + 知识库 → 场景图谱 (Scene Graph)

核心设计（来自 Transformer 键值查询分析）：
  - 节点 = 建筑对象（统一 schema）
  - 边   = 空间关系（从 VR 布局统计学习）
  - 属性 = 物理/语义标签（从知识库补充）

工作流程：
  VR效果图 ──→ 对象检测 ──→ 节点
                     ↓
  CAD施工图 ──→ 空间坐标 ──→ 边（空间关系）
                     ↓
  知识库   ──→ 物理属性 ──→ 节点属性
                     ↓
              Scene Graph (可训练格式)
"""

from __future__ import annotations
import json
import math
import uuid
import sys
import os
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal
from pathlib import Path
from collections import defaultdict

# 动态导入 data_schema（避免循环导入）
_builder_dir = Path(__file__).parent
sys.path.insert(0, str(_builder_dir))
from data_schema import (
    BuildingObject, ObjectLibrary, ObjectCategory,
    Geometry, Semantic, PhysicsProperties, BoundingBox,
    GraspPoint, Clearance,
    RoomType, SurfaceType, DeformationType,
    create_furniture_templates, create_appliance_templates,
)


# ─────────────────────────────────────────────────────────
# 空间关系定义（从 Transformer 注意力模式类比）
# ─────────────────────────────────────────────────────────

class SpatialRelation(str):
    """空间关系类型（类似 Transformer 中的关系类型 token）"""
    # 水平方向
    NEXT_TO = "next_to"           # 相邻（左右）
    FACING = "facing"             # 面对面（客厅沙发-电视）
    PARALLEL = "parallel"         # 平行排列（餐椅）
    DIAGONAL = "diagonal"         # 对角线

    # 垂直方向
    ABOVE = "above"              # 正上方
    BELOW = "below"              # 正下方
    ON_TOP_OF = "on_top_of"       # 放在上面（茶几在地毯上）
    UNDER = "under"              # 在下面（地毯在茶几下）

    # 包含关系
    INSIDE = "inside"            # 在里面（物品在柜子里）
    CONTAINS = "contains"         # 包含（柜子包含物品）
    ATTACHED_TO = "attached_to"  # 固定连接（壁挂电视）

    # 功能关系
    PART_OF = "part_of"          # 属于同一功能组
    OFTEN_NEAR = "often_near"    # 常靠近（从 VR 统计得出）


@dataclass
class SceneEdge:
    """场景图中的一条边（对象之间的关系）"""
    subject_id: str              # 源对象
    object_id: str               # 目标对象
    relation: str                # 关系类型

    # 关系属性（从 VR 数据统计得出）
    typical_distance_m: float = 0.0    # 典型距离 (m)
    distance_range: tuple[float, float] = (0.0, 5.0)  # 距离范围
    confidence: float = 0.5            # 关系置信度
    source: str = "vr_statistics"      # 数据来源

    # Transformer attention 类属性（用于热力图可视化）
    attention_weight: float = 0.0


@dataclass
class SceneGraph:
    """
    场景图谱

    结构（类比 Transformer 的键值存储）：
      - nodes:      对象节点（K=键, V=值）
      - edges:      关系边（Q=查询注意力）
      - room_type:  房间类型（语义上下文）
      - meta:       元数据

    类比图神经网络（GNN）的消息传递：
      每个节点从邻居节点接收"消息"，更新自己的状态
    """
    scene_id: str = ""
    scene_name: str = ""
    room_type: str = ""
    platform: str = ""

    # 节点（BuildingObject 实例）
    nodes: dict[str, BuildingObject] = field(default_factory=dict)

    # 边（关系）
    edges: list[SceneEdge] = field(default_factory=list)

    # 统计信息
    num_objects: int = 0
    num_relations: int = 0

    # 来源
    source_vr_id: Optional[int] = None
    source_file: str = ""

    def add_node(self, obj: BuildingObject):
        self.nodes[obj.id] = obj

    def add_edge(self, subject: str, obj: str, relation: str,
                 distance: float = 0.0, confidence: float = 0.5,
                 source: str = "vr_statistics"):
        edge = SceneEdge(
            subject_id=subject,
            object_id=obj,
            relation=relation,
            typical_distance_m=distance,
            confidence=confidence,
            source=source,
        )
        self.edges.append(edge)

    def get_neighbors(self, node_id: str, relation: Optional[str] = None) -> list[str]:
        """获取节点邻居（用于 GNN 消息传递）"""
        neighbors = []
        for e in self.edges:
            if e.subject_id == node_id and (relation is None or e.relation == relation):
                neighbors.append(e.object_id)
        return neighbors

    def to_dict(self) -> dict:
        return {
            "scene_id": self.scene_id,
            "scene_name": self.scene_name,
            "room_type": self.room_type,
            "platform": self.platform,
            "num_objects": len(self.nodes),
            "num_relations": len(self.edges),
            "source_vr_id": self.source_vr_id,
            "source_file": self.source_file,
            "nodes": {k: asdict(v) for k, v in self.nodes.items()},
            "edges": [asdict(e) for e in self.edges],
        }

    @classmethod
    def from_dict(cls, data: dict) -> SceneGraph:
        """从字典重建场景图"""
        scene = cls(
            scene_id=data["scene_id"],
            scene_name=data.get("scene_name", ""),
            room_type=data.get("room_type", ""),
            platform=data.get("platform", ""),
            num_objects=data.get("num_objects", 0),
            num_relations=data.get("num_relations", 0),
            source_vr_id=data.get("source_vr_id"),
            source_file=data.get("source_file", ""),
        )
        for nid, ndata in data.get("nodes", {}).items():
            scene.nodes[nid] = BuildingObject(**ndata)
        for edata in data.get("edges", []):
            scene.edges.append(SceneEdge(**edata))
        return scene


# ─────────────────────────────────────────────────────────
# VR → 场景图谱 转换器
# ─────────────────────────────────────────────────────────

class VRSceneBuilder:
    """
    从 VR 效果图构建场景图谱

    数据流（CNN 层次化抽象类比）：
      VR像素 → 语义分割（房间区域）→ 对象检测（家具）→ 场景图（关系）
    """

    # VR 房间 → 典型家具配置（从知识库统计）
    ROOM_FURNITURE_CONFIG = {
        "客厅": {
            "required": ["sofa", "coffee_table"],
            "optional": ["tv", "tv_stand", "armchair", "rug", "floor_lamp", "bookshelf"],
            "spatial_rules": {
                "sofa": {"facing": "tv", "min_dist": 2.5, "max_dist": 4.0},
                "coffee_table": {"on_top_of": "rug", "in_front_of": "sofa", "dist_from_sofa": 0.8},
                "tv": {"facing": "sofa", "attached_to": "wall", "min_dist": 2.5},
                "rug": {"under": "coffee_table", "under": "sofa", "dist_from_wall": 0.3},
            }
        },
        "卧室": {
            "required": ["bed_double"],
            "optional": ["wardrobe", "nightstand", "dresser", "desk", "tv", "dressing_table"],
            "spatial_rules": {
                "bed_double": {"wall_mounted": False, "center_aligned": True},
                "wardrobe": {"wall_mounted": False, "opposite_wall": True},
                "nightstand": {"next_to": "bed_double", "dist": 0.5, "side": "left_or_right"},
            }
        },
        "厨房": {
            "required": ["kitchen_cabinet", "sink"],
            "optional": ["refrigerator", "range_hood", "dishwasher", "microwave"],
            "spatial_rules": {
                "refrigerator": {"next_to": "kitchen_cabinet", "dist": 0.3},
                "sink": {"in_front_of": "window"},
            }
        },
        "卫生间": {
            "required": ["toilet", "washbasin"],
            "optional": ["bathtub", "shower", "bidet", "mirror", "towel_rail"],
            "spatial_rules": {
                "toilet": {"not_next_to": "washbasin", "min_dist": 0.6},
                "bathtub": {"in_corner": True},
                "mirror": {"attached_to": "wall", "above": "washbasin"},
            }
        },
        "餐厅": {
            "required": ["dining_table"],
            "optional": ["dining_chair", "sideboard", "pendant_lamp"],
            "spatial_rules": {
                "dining_table": {"center": True},
                "dining_chair": {"around": "dining_table", "dist": 0.5},
            }
        },
    }

    # 从 VR 平台提取的物理标签 → schema 映射
    PHYSICS_TAG_MAP = {
        "高采光": {"semantic": {"style_tags": ["高采光"]}},
        "自然光": {"semantic": {"style_tags": ["自然采光"]}},
        "简约": {"semantic": {"style_tags": ["现代简约"]}},
        "现代": {"semantic": {"style_tags": ["现代"]}},
        "欧式": {"semantic": {"style_tags": ["欧式"]}},
        "北欧": {"semantic": {"style_tags": ["北欧"]}},
        "意式": {"semantic": {"style_tags": ["意式"]}},
        "新中式": {"semantic": {"style_tags": ["新中式"]}},
        "侘寂": {"semantic": {"style_tags": ["侘寂"]}},
        "奶油": {"semantic": {"style_tags": ["奶油风"]}},
        "金属装饰": {"physics": {"friction_surface": "metal"}},
        "石材": {"physics": {"friction_surface": "stone"}},
        "木质": {"physics": {"friction_surface": "wood"}},
        "玻璃": {"physics": {"friction_surface": "glass", "is_translucent": True}},
        "布艺": {"physics": {"friction_surface": "fabric", "deformable": True}},
        "开放通透": {"semantic": {"style_tags": ["开放式"]}},
        "干湿分离": {"semantic": {"style_tags": ["干湿分离"]}},
        "大空间": {"geometry": {"vision_confidence": 0.8}},
    }

    def __init__(self):
        # 预加载模板库
        self.library = ObjectLibrary()
        for obj in create_furniture_templates():
            self.library.add_object(obj)
        for obj in create_appliance_templates():
            self.library.add_object(obj)

        # 共现关系统计（从 VR 数据学习）
        self.cooccurrence_matrix = self._build_cooccurrence_matrix()

    def _build_cooccurrence_matrix(self) -> dict[str, dict[str, int]]:
        """
        从 VR 知识库构建共现矩阵
        统计：哪些家具类型经常一起出现在同一个 VR 中

        输出：{"sofa": {"coffee_table": 45, "tv": 38, ...}}
        """
        import os
        base = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai"

        cooc = defaultdict(lambda: defaultdict(int))

        try:
            with open(os.path.join(base, "knowledge", "VR_KNOWLEDGE.json"),
                      "r", encoding="utf-8") as f:
                vr_data = json.load(f)

            # 统计每对类型在同一个 scene 中出现的次数
            # 使用 raw_vr 数据
            for vr in vr_data.get("raw_vr", []):
                room_list = vr.get("rooms", [])
                if not room_list:
                    continue

                # 同一房间内的类型两两组合
                unique_types = list(set(room_list))
                for i, t1 in enumerate(unique_types):
                    for t2 in unique_types[i+1:]:
                        cooc[t1][t2] += 1
                        cooc[t2][t1] += 1

        except Exception as e:
            print(f"Warning: could not build cooccurrence matrix: {e}")

        return cooc

    def build_from_vr_entry(self,
                             vr_entry: dict,
                             objects: Optional[list[BuildingObject]] = None
                             ) -> SceneGraph:
        """从单个 VR 条目构建场景图"""
        scene = SceneGraph(
            scene_id=f"vr_{vr_entry.get('vr_id', uuid.uuid4().hex[:6])}",
            scene_name=vr_entry.get("title", ""),
            room_type=vr_entry.get("room_type", vr_entry.get("room", "")),
            platform=vr_entry.get("platform", ""),
            source_vr_id=vr_entry.get("vr_id"),
            source_file="VR_KNOWLEDGE.json",
        )

        rooms = vr_entry.get("rooms", [])
        physics_tags = vr_entry.get("physics_tags", [])
        designer = vr_entry.get("designer", "")

        # 确定房间类型
        if not scene.room_type and rooms:
            scene.room_type = rooms[0]

        # 加载/生成房间中的对象
        room_objects = self._resolve_room_objects(scene.room_type, rooms, objects)

        # 添加节点
        for obj in room_objects:
            obj.scene_id = scene.scene_id
            obj.visible_in_vr = True
            scene.add_node(obj)

        # 构建关系边
        self._build_spatial_edges(scene, room_objects, physics_tags)

        # 添加共现关系（软关联，不是硬约束）
        self._add_cooccurrence_relations(scene, room_objects)

        scene.num_objects = len(scene.nodes)
        scene.num_relations = len(scene.edges)

        return scene

    def _resolve_room_objects(self,
                             room_type: str,
                             room_list: list,
                             extra_objects: Optional[list[BuildingObject]]
                             ) -> list[BuildingObject]:
        """根据房间类型和房间列表确定场景中的对象"""
        objects = []
        obj_id_counter = defaultdict(int)

        # 获取该房间的模板
        config = self.ROOM_FURNITURE_CONFIG.get(room_type, {})

        # 添加必选对象
        for req in config.get("required", []):
            template = self._find_template(req)
            if template:
                obj = self._clone_with_id(template, f"{req}_{obj_id_counter[req]}")
                obj.scene_id = room_type
                obj.semantic.room_types = [room_type]
                objects.append(obj)
                obj_id_counter[req] += 1

        # 添加可选对象（基于房间中的标签）
        for opt in config.get("optional", []):
            template = self._find_template(opt)
            if template:
                obj = self._clone_with_id(template, f"{opt}_{obj_id_counter[opt]}")
                obj.scene_id = room_type
                obj.semantic.room_types = [room_type]
                objects.append(obj)
                obj_id_counter[opt] += 1

        # 如果没有配置，尝试从 room_list 中解析
        if not objects and room_list:
            for room_name in room_list:
                obj_type = self._room_name_to_object_type(room_name)
                template = self._find_template(obj_type)
                if template:
                    obj = self._clone_with_id(template, f"{obj_type}_{obj_id_counter[obj_type]}")
                    obj.scene_id = room_type
                    obj.semantic.room_types = [room_type]
                    objects.append(obj)
                    obj_id_counter[obj_type] += 1

        # 合并额外对象
        if extra_objects:
            objects.extend(extra_objects)

        return objects

    def _find_template(self, subcategory: str) -> Optional[BuildingObject]:
        """在模板库中查找匹配的对象模板"""
        matches = self.library.query(subcategory=subcategory)
        if matches:
            return matches[0]
        return None

    def _clone_with_id(self, template: BuildingObject, suffix: str) -> BuildingObject:
        """克隆模板并分配新 ID"""
        import copy
        obj = copy.deepcopy(template)
        obj.id = f"{template.subcategory}-{suffix}-{uuid.uuid4().hex[:4]}"
        return obj

    def _room_name_to_object_type(self, room_name: str) -> str:
        """将中文房间名转换为对象类型"""
        mapping = {
            "客厅": "sofa",
            "餐厅": "dining_table",
            "主卧": "bed_double",
            "次卧": "bed_double",
            "卧室": "bed_double",
            "书房": "desk",
            "厨房": "kitchen_cabinet",
            "卫生间": "toilet",
            "洗手间": "washbasin",
            "浴室": "bathtub",
            "阳台": "planter",
            "茶室": "tea_table",
            "棋牌室": "game_table",
            "影音室": "media_system",
            "衣帽间": "wardrobe",
            "瑜伽室": "yoga_mat",
            "台球室": "billiard_table",
            "乒乓球室": "pingpong_table",
            "地下室": "storage",
            "过道": "corridor",
            "玄关": "entrance_table",
        }
        for key, val in mapping.items():
            if key in room_name:
                return val
        return "furniture"

    def _build_spatial_edges(self,
                             scene: SceneGraph,
                             objects: list[BuildingObject],
                             physics_tags: list[str]) -> None:
        """
        构建空间关系边

        使用规则 + 统计混合：
        - 规则：家具布局规范（如沙发对着电视）
        - 统计：从 VR 共现矩阵学习的关系
        """
        # 简单规则：同房间内相邻的对象添加 next_to 关系
        for i, obj1 in enumerate(objects):
            for obj2 in objects[i+1:]:
                # 检查是否有功能关联
                if obj2.subcategory in obj1.semantic.typical_neighbors:
                    scene.add_edge(
                        subject=obj1.id,
                        obj=obj2.id,
                        relation=SpatialRelation.OFTEN_NEAR,
                        distance=1.0,
                        confidence=0.7,
                    )
                elif obj2.subcategory in obj1.semantic.typical_pairs:
                    # 配套家具（如茶几配套沙发）
                    scene.add_edge(
                        subject=obj1.id,
                        obj=obj2.id,
                        relation=SpatialRelation.PART_OF,
                        distance=0.5,
                        confidence=0.85,
                    )

        # 应用物理标签到对象
        for tag in physics_tags:
            tag_map = self.PHYSICS_TAG_MAP.get(tag, {})
            for obj in objects:
                if "physics" in tag_map:
                    for k, v in tag_map["physics"].items():
                        setattr(obj.physics, k, v)
                if "semantic" in tag_map:
                    for k, v in tag_map["semantic"].items():
                        if k == "style_tags":
                            obj.semantic.style_tags.extend(v)
                        else:
                            setattr(obj.semantic, k, v)

    def _add_cooccurrence_relations(self,
                                    scene: SceneGraph,
                                    objects: list[BuildingObject]) -> None:
        """添加共现关系（软关联）"""
        subcats = [o.subcategory for o in objects]
        for i, sc1 in enumerate(subcats):
            for sc2 in subcats[i+1:]:
                count = self.cooccurrence_matrix.get(sc1, {}).get(sc2, 0)
                if count >= 2:  # 共现 >= 2 次才加边
                    # 找到对应对象
                    obj1 = next((o for o in objects if o.subcategory == sc1), None)
                    obj2 = next((o for o in objects if o.subcategory == sc2), None)
                    if obj1 and obj2:
                        conf = min(count / 10, 1.0)  # 最多10次共现，置信度饱和
                        scene.add_edge(
                            subject=obj1.id,
                            obj=obj2.id,
                            relation=SpatialRelation.OFTEN_NEAR,
                            confidence=conf,
                            source="vr_cooccurrence",
                        )


# ─────────────────────────────────────────────────────────
# CAD → 场景图谱（几何层）
# ─────────────────────────────────────────────────────────

class CADSceneBuilder:
    """
    从 CAD 数据构建几何场景图

    几何数据来源：
      - building_objects.json（CAD 解析得到的门/墙/柱）
      - CAD 图纸元数据

    CAD 数据 → 精确空间关系（米制坐标）
    """

    def __init__(self):
        self.library = ObjectLibrary()
        for obj in create_furniture_templates():
            self.library.add_object(obj)

    def build_from_cad_objects(self,
                                cad_objects: list[dict],
                                room_type: str = "cad_scene"
                                ) -> SceneGraph:
        """从 CAD 对象列表构建场景图"""
        scene = SceneGraph(
            scene_id=f"cad_{uuid.uuid4().hex[:6]}",
            scene_name=room_type,
            room_type=room_type,
            source_file="building_objects.json",
        )

        # 转换 CAD 对象
        for cad_obj in cad_objects:
            building_obj = self._cad_to_building_object(cad_obj)
            scene.add_node(building_obj)

        # 从几何坐标构建精确空间关系
        self._build_geometric_edges(scene)

        scene.num_objects = len(scene.nodes)
        scene.num_relations = len(scene.edges)

        return scene

    def _cad_to_building_object(self, cad_dict: dict) -> BuildingObject:
        """将 CAD JSON 转换为 BuildingObject"""
        obj_type = cad_dict.get("type", "unknown")
        cat = ObjectCategory.STRUCTURE

        # 从类型推断类别
        type_to_cat = {
            "door": ObjectCategory.DOOR_WINDOW,
            "window": ObjectCategory.DOOR_WINDOW,
            "wall": ObjectCategory.STRUCTURE,
            "column": ObjectCategory.STRUCTURE,
            "beam": ObjectCategory.STRUCTURE,
            "floor": ObjectCategory.STRUCTURE,
            "ceiling": ObjectCategory.STRUCTURE,
        }
        cat = type_to_cat.get(obj_type, ObjectCategory.STRUCTURE)

        dims = cad_dict.get("dimensions", {})
        bbox = BoundingBox(
            x=dims.get("width", 1.0),
            y=dims.get("height", 2.1),
            z=dims.get("depth", 0.1),
        )

        pos = cad_dict.get("position", [0, 0, 0])
        rot = cad_dict.get("rotation", [0, 0, 0])

        physics_data = cad_dict.get("physics", {})
        physics = PhysicsProperties(
            mass_kg=physics_data.get("mass", 25.0),
            friction_static=physics_data.get("friction", 0.3),
            stiffness_Nm=physics_data.get("stiffness", 12000),
            physics_source="cad",
            physics_confidence=0.95,  # CAD 解析的物理参数置信度高
        )

        obj = BuildingObject(
            id=cad_dict.get("id", f"cad-{obj_type}-{uuid.uuid4().hex[:4]}"),
            name=cad_dict.get("name", obj_type),
            category=cat,
            subcategory=obj_type,
            geometry=Geometry(
                bounding_box=bbox,
                center_offset=tuple(pos),
                vision_confidence=1.0,  # CAD 解析置信度最高
            ),
            physics=physics,
            source_type="cad",
            position_3d=tuple(pos),
            rotation_y=rot[1] if len(rot) > 1 else 0.0,
        )

        # 门可以开合
        if obj_type == "door":
            obj.robot.openable = True
            obj.robot.path_obstacle = False
            obj.robot.actions.push = True
            obj.robot.actions.pull = True
            obj.robot.actions.lift = False

        return obj

    def _build_geometric_edges(self, scene: SceneGraph) -> None:
        """基于几何坐标构建空间关系"""
        objects = list(scene.nodes.values())

        for i, obj1 in enumerate(objects):
            for obj2 in objects[i+1:]:
                pos1 = obj1.position_3d
                pos2 = obj2.position_3d

                # 计算距离
                dist = math.sqrt(
                    (pos1[0] - pos2[0])**2 +
                    (pos1[1] - pos2[1])**2 +
                    (pos1[2] - pos2[2])**2
                )

                # 高度差判断上下关系
                height_diff = abs(pos1[1] - pos2[1])

                if height_diff > 0.5:  # 高度差 > 0.5m
                    if pos1[1] > pos2[1]:
                        rel = SpatialRelation.ABOVE
                    else:
                        rel = SpatialRelation.BELOW
                elif dist < 3.0:  # 水平距离 < 3m
                    rel = SpatialRelation.NEXT_TO
                else:
                    rel = SpatialRelation.DIAGONAL

                scene.add_edge(
                    subject=obj1.id,
                    obj=obj2.id,
                    relation=rel,
                    distance=round(dist, 2),
                    confidence=0.9,
                    source="cad_geometry",
                )


# ─────────────────────────────────────────────────────────
# 场景图谱管理器
# ─────────────────────────────────────────────────────────

class SceneGraphDatabase:
    """
    场景图谱数据库 — 管理所有场景图

    支持：
      - load_from_vr()
      - load_from_cad()
      - query_by_room()
      - export_for_training() → 神经网络训练数据
    """

    def __init__(self):
        self.scenes: dict[str, SceneGraph] = {}

    def load_from_vr_json(self, vr_path: str) -> int:
        """从 VR 知识库加载所有场景"""
        with open(vr_path, "r", encoding="utf-8") as f:
            vr_data = json.load(f)

        builder = VRSceneBuilder()
        count = 0

        # 从 raw_vr 构建
        for vr in vr_data.get("raw_vr", []):
            rooms = vr.get("rooms", [])
            if not rooms:
                continue

            # 为每个房间创建一个 scene
            for room_name in rooms:
                vr_copy = dict(vr)
                vr_copy["room_type"] = room_name
                vr_copy["rooms"] = [room_name]
                try:
                    scene = builder.build_from_vr_entry(vr_copy)
                    self.scenes[scene.scene_id] = scene
                    count += 1
                except Exception as e:
                    print(f"Error building scene from VR {vr.get('vr_id')}: {e}")

        # 也从 rooms 字段构建
        for room_name, room_info in vr_data.get("rooms", {}).items():
            for sample in room_info.get("samples", []):
                vr_entry = {
                    "vr_id": sample.get("index"),
                    "platform": sample.get("platform", ""),
                    "room_type": room_name,
                    "rooms": [room_name],
                    "physics_tags": sample.get("physics_tags", []),
                    "designer": sample.get("designer", ""),
                }
                try:
                    scene = builder.build_from_vr_entry(vr_entry)
                    self.scenes[scene.scene_id] = scene
                    count += 1
                except Exception as e:
                    print(f"Error building scene: {e}")

        return count

    def load_from_cad_json(self, cad_path: str) -> int:
        """从 CAD 对象 JSON 加载场景"""
        with open(cad_path, "r", encoding="utf-8") as f:
            cad_objects = json.load(f)

        builder = CADSceneBuilder()
        scene = builder.build_from_cad_objects(cad_objects)
        self.scenes[scene.scene_id] = scene
        return 1

    def query_by_room(self, room_type: str) -> list[SceneGraph]:
        """查询特定房间类型的所有场景"""
        return [s for s in self.scenes.values()
                if room_type in s.room_type or s.room_type == room_type]

    def get_statistics(self) -> dict:
        """获取统计信息"""
        room_counts = defaultdict(int)
        total_edges = 0
        total_nodes = 0

        for scene in self.scenes.values():
            room_counts[scene.room_type] += 1
            total_edges += len(scene.edges)
            total_nodes += len(scene.nodes)

        return {
            "total_scenes": len(self.scenes),
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "avg_nodes_per_scene": total_nodes / max(len(self.scenes), 1),
            "avg_edges_per_scene": total_edges / max(len(self.scenes), 1),
            "room_distribution": dict(room_counts),
        }

    def export_for_training(self, path: str) -> dict:
        """
        导出为神经网络训练格式

        输出格式：
          {
            "scenes": [...scene_dicts...],
            "node_features": [...],    # 对象特征矩阵
            "edge_index": [...],       # 边索引 (GNN 用)
            "edge_features": [...],     # 边特征
            "labels": [...],            # 训练标签
          }
        """
        import numpy as np

        scene_list = list(self.scenes.values())
        node_features = []
        edge_index = []  # [2, num_edges]
        edge_features = []
        labels = []

        global_node_id = 0
        scene_node_offsets = {}

        for scene in scene_list:
            scene_node_offsets[scene.scene_id] = global_node_id

            for node_id, node in scene.nodes.items():
                feat = self._object_to_feature_vector(node)
                node_features.append(feat)
                labels.append(node.category.value)

            for edge in scene.edges:
                edge_index.append([
                    global_node_id + list(scene.nodes.keys()).index(edge.subject_id),
                    global_node_id + list(scene.nodes.keys()).index(edge.object_id),
                ])
                edge_features.append([edge.typical_distance_m, edge.confidence])

            global_node_id += len(scene.nodes)

        output = {
            "num_scenes": len(scene_list),
            "num_nodes": len(node_features),
            "num_edges": len(edge_index),
            "scene_ids": list(self.scenes.keys()),
            "node_features": np.array(node_features, dtype=np.float32).tolist(),
            "edge_index": edge_index,
            "edge_features": edge_features,
            "labels": labels,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        return {
            "scenes": len(scene_list),
            "nodes": len(node_features),
            "edges": len(edge_index),
            "saved_to": path,
        }

    def _object_to_feature_vector(self, obj: BuildingObject) -> list[float]:
        """
        将 BuildingObject 转换为固定维度的特征向量

        特征维度（48维）：
          - 几何特征 (12维): bbox x/y/z, volume, footprint, clearance(front/back/left/right/above)
          - 物理特征 (16维): mass, density, friction, stiffness, compliance, hardness, thermal...
          - 语义特征 (8维): room_type one-hot, category one-hot
          - 机器人特征 (12维): difficulty scores, force requirements
        """
        geo = obj.geometry
        bbox = obj.geometry.bounding_box
        phy = obj.physics
        sem = obj.semantic
        rob = obj.robot.actions

        features = [
            # 几何 (12)
            bbox.x if hasattr(bbox, 'x') else 0.0,
            bbox.y if hasattr(bbox, 'y') else 0.0,
            bbox.z if hasattr(bbox, 'z') else 0.0,
            bbox.volume if hasattr(bbox, 'volume') else 0.0,
            bbox.footprint_area if hasattr(bbox, 'footprint_area') else 0.0,
            geo.clearance.front,
            geo.clearance.back,
            geo.clearance.left,
            geo.clearance.right,
            geo.clearance.above,
            float(geo.wall_mounted),
            float(geo.floor_mounted),
            # 物理 (16)
            phy.mass_kg,
            phy.density_gcm3,
            phy.friction_static,
            phy.friction_dynamic,
            phy.compliance,
            math.log1p(phy.stiffness_Nm),
            phy.young_modulus_GPa,
            float(phy.deformable),
            float(phy.is_light_source),
            phy.light_power_W,
            phy.light_lumen / 1000.0 if phy.light_lumen else 0.0,
            phy.thermal_conductivity_WmK,
            phy.physics_confidence,
            float(phy.surface_hardness == "hard"),
            float(phy.surface_hardness == "soft"),
            # 机器人 (12)
            float(rob.push),
            float(rob.pull),
            float(rob.lift),
            float(rob.openable),
            rob.push_difficulty / 5.0,
            rob.pull_difficulty / 5.0,
            rob.lift_difficulty / 5.0,
            rob.force_push_N / 100.0,
            rob.force_lift_N / 500.0,
            float(rob.grasp_type.value == "two_hand"),
            float(rob.grasp_type.value == "precision"),
            float(rob.suction_possible),
        ]

        # padding to fixed size
        while len(features) < 48:
            features.append(0.0)

        return features[:48]


# ─────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os

    base = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai"
    vr_path = os.path.join(base, "knowledge", "VR_KNOWLEDGE.json")
    cad_path = os.path.join(base, "data", "processed", "building_objects.json")

    print("=== 场景图谱构建器 ===\n")

    # 构建场景图谱数据库
    db = SceneGraphDatabase()

    print("1. 从 VR 知识库构建...")
    if os.path.exists(vr_path):
        count = db.load_from_vr_json(vr_path)
        print(f"   VR 场景: {count} 个")

    print("2. 从 CAD 数据构建...")
    if os.path.exists(cad_path):
        cad_count = db.load_from_cad_json(cad_path)
        print(f"   CAD 场景: {cad_count} 个")

    stats = db.get_statistics()
    print(f"\n统计:")
    print(f"  总场景数: {stats['total_scenes']}")
    print(f"  总节点数: {stats['total_nodes']}")
    print(f"  总边数: {stats['total_edges']}")
    print(f"  平均节点/场景: {stats['avg_nodes_per_scene']:.1f}")
    print(f"  平均边/场景: {stats['avg_edges_per_scene']:.1f}")
    print(f"\n  房间分布:")
    for room, cnt in sorted(stats['room_distribution'].items(),
                            key=lambda x: -x[1])[:10]:
        print(f"    {room}: {cnt}")

    # 导出训练数据
    out_path = os.path.join(base, "data", "processed", "scene_graph_training.json")
    print(f"\n3. 导出神经网络训练数据...")
    result = db.export_for_training(out_path)
    print(f"   保存到: {result['saved_to']}")
    print(f"   节点数: {result['nodes']}, 边数: {result['edges']}")
