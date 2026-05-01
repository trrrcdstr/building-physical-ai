"""
data_schema.py — 统一对象数据模型
====================================
建筑物理 AI 世界模型的核心 schema 定义。

核心设计原则（来自 CNN vs Transformer 分析）：
- CNN 层次化抽象 → schema 分层设计，从几何到语义到物理
- Transformer 动态关系 → 对象之间通过 scene_graph 建立关系
- 物理属性先验 → MLP 可解释的物理层

三层架构：
  L1 几何层 (Geometry)      — 来自 CAD/Vision，固定结构
  L2 语义层 (Semantic)       — 来自 VR/知识库，可扩展标签
  L3 物理层 (Physics)        — 来自材料库/ML预测，数值型向量
"""

from __future__ import annotations
import math
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal
from enum import Enum


# ─────────────────────────────────────────────────────────
# 枚举定义
# ─────────────────────────────────────────────────────────

class ObjectCategory(str, Enum):
    STRUCTURE = "structure"       # 建筑结构：墙/柱/梁/板/楼梯
    FURNITURE = "furniture"        # 家具：沙发/床/柜/桌/椅
    APPLIANCE = "appliance"        # 家电：电视/空调/冰箱/洗衣机
    MATERIAL = "material"          # 装饰材料：瓷砖/地板/涂料/吊顶
    LIGHTING = "lighting"          # 照明灯具
    DOOR_WINDOW = "door_window"    # 门窗
    UTILITY = "utility"            # 机电设施：开关/插座/水龙头/传感器
    SOFT = "soft"                  # 软装：窗帘/地毯/抱枕/装饰画


class RoomType(str, Enum):
    LIVING = "客厅"          # 客厅
    BEDROOM = "卧室"          # 卧室
    MASTER_BEDROOM = "主卧"    # 主卧
    SECOND_BEDROOM = "次卧"    # 次卧
    KITCHEN = "厨房"          # 厨房
    BATHROOM = "卫生间"        # 卫生间
    BALCONY = "阳台"          # 阳台
    CORRIDOR = "走廊"          # 走廊
    DINING = "餐厅"           # 餐厅
    STUDY = "书房"            # 书房
    GARAGE = "车库"           # 车库
    TERRACE = "庭院"           # 庭院
    STAIR = "楼梯"            # 楼梯间
    HALL = "大堂"             # 大堂
    MEETING = "会议室"         # 会议室
    OFFICE = "办公区"          # 办公区
    HOTEL_ROOM = "酒店客房"    # 酒店客房
    SHOP = "商铺"             # 商铺
    RESTAURANT = "餐饮"        # 餐饮
    PUBLIC_TOILET = "公卫"     # 公共卫生间


class SurfaceType(str, Enum):
    HARD_SMOOTH = "hard_smooth"      # 硬光滑：玻璃/大理石/光面瓷砖
    HARD_ROUGH = "hard_rough"        # 硬粗糙：石材/混凝土/哑光瓷砖
    WOOD = "wood"                    # 木材
    FABRIC = "fabric"                # 织物：布艺/窗帘/地毯
    METAL = "metal"                  # 金属
    COMPOSITE = "composite"          # 复合材料
    ORGANIC = "organic"              # 有机材质：绿植/皮革


class DeformationType(str, Enum):
    RIGID = "rigid"                     # 刚性：陶瓷/石材/玻璃
    ELASTIC = "elastic"                 # 弹性：金属弹簧/橡胶
    SOFT_FLEXIBLE = "soft_flexible"     # 软柔性：布料/海绵/纸张
    VISCOUS = "viscous"                 # 粘弹性：胶水/密封胶


class GraspType(str, Enum):
    TWO_HAND = "two_hand"           # 双手：大型家具
    SINGLE_HAND = "single_hand"     # 单手：小型物品
    PRECISION = "precision"         # 精密：按钮/旋钮/细小物
    SIDE = "side"                   # 侧向：板状物/抽屉
    HOOK = "hook"                   # 钩挂：把手/挂杆


# ─────────────────────────────────────────────────────────
# L1: 几何层 — 来自 CAD/Vision
# ─────────────────────────────────────────────────────────

@dataclass
class BoundingBox:
    """轴对齐包围盒（AABB）"""
    x: float = 0.0    # X方向尺寸 (m)
    y: float = 0.0    # Y方向尺寸 = 高度 (m)
    z: float = 0.0    # Z方向尺寸 = 深度 (m)

    @property
    def volume(self) -> float:
        return self.x * self.y * self.z

    @property
    def footprint_area(self) -> float:
        """投影面积（用于地面占用）"""
        return self.x * self.z


@dataclass
class GraspPoint:
    """机器人抓取点"""
    type: Literal["edge", "center", "corner", "side", "handle", "top"] = "center"
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)  # 相对于物体中心
    orientation_needed: float = 0.0    # 需要的抓取角度 (rad)
    force_min_N: float = 1.0           # 最小抓取力 (N)
    preferred_hand: Literal["left", "right", "both"] = "both"


@dataclass
class Clearance:
    """物体周围所需间隙"""
    front: float = 0.6     # 前面需要间隙 (m)
    back: float = 0.3     # 后面需要间隙 (m)
    left: float = 0.3      # 左侧间隙 (m)
    right: float = 0.3     # 右侧间隙 (m)
    above: float = 0.5     # 上方间隙（机器人臂活动空间）
    below: float = 0.0     # 下方（通常贴地）


@dataclass
class Geometry:
    """L1 几何层 — 来自 CAD 解析或视觉估计"""
    bounding_box: BoundingBox = field(default_factory=BoundingBox)
    center_offset: tuple[float, float, float] = (0.0, 0.0, 0.0)  # 几何中心偏移
    grasp_points: list[GraspPoint] = field(default_factory=list)
    clearance: Clearance = field(default_factory=Clearance)
    wall_mounted: bool = False       # 是否壁挂
    floor_mounted: bool = True       # 是否落地
    ceiling_mounted: bool = False    # 是否吊装
    # 从效果图估计的参数（vision uncertainty）
    vision_confidence: float = 1.0   # 视觉估计置信度 0-1
    depth_estimated: bool = False    # 深度是否从2D估计


# ─────────────────────────────────────────────────────────
# L2: 语义层 — 来自 VR/知识库
# ─────────────────────────────────────────────────────────

@dataclass
class Semantic:
    """L2 语义层 — 功能标签、风格、使用场景"""
    room_types: list[str] = field(default_factory=list)      # 适用房间类型
    style_tags: list[str] = field(default_factory=list)      # 风格标签
    color_family: str = "neutral"                             # 主色调系
    design_era: str = "contemporary"                         # 设计年代
    # 共现关系（从 VR 数据统计得到）
    typical_neighbors: list[str] = field(default_factory=list)  # 常一起出现的物体类型
    typical_pairs: list[list[str]] = field(default_factory=list)  # 典型搭配 [物体A, 物体B]
    functional_group: str = ""                                # 功能分组：seating/dining/sleeping/hygiene


# ─────────────────────────────────────────────────────────
# L3: 物理层 — 来自材料库/物理查询/ML 预测
# ─────────────────────────────────────────────────────────

@dataclass
class PhysicsProperties:
    """
    L3 物理层 — 机器人操作所需的所有物理参数。

    数据来源优先级（CNN 推理 vs 知识库查询）：
      1. 知识库已有（如：瓷砖、木地板）：精确值
      2. 材料属性推理（如：布艺沙发）：ML 预测 + 物理先验
      3. 安全默认值（保守估计）
    """
    # 质量相关
    mass_kg: float = 10.0             # 质量 (kg)
    density_gcm3: float = 0.5          # 密度 (g/cm³)

    # 摩擦特性（对抓取/推动至关重要）
    friction_static: float = 0.4       # 静摩擦系数
    friction_dynamic: float = 0.3      # 动摩擦系数
    friction_surface: SurfaceType = SurfaceType.HARD_SMOOTH

    # 力学特性
    compliance: float = 0.1            # 柔顺性 0(刚性)-1(完全弹性)
    stiffness_Nm: float = 10000.0      # 刚度 (N/m)
    young_modulus_GPa: float = 1.0     # 杨氏模量 (GPa) - 查表得到

    # 变形特性
    deformable: bool = False
    deformation_type: DeformationType = DeformationType.RIGID
    fracture_risk: float = 0.0         # 破损风险 0-1

    # 表面特性
    surface_hardness: Literal["soft", "medium", "hard"] = "medium"
    roughness_um: float = 10.0          # 表面粗糙度 (μm)

    # 热工特性（来自材料库）
    thermal_conductivity_WmK: float = 0.5  # 导热系数 (W/m·K)
    thermal_mass: float = 1000.0       # 热容 (J/K)

    # 光学特性（来自照明库）
    is_light_source: bool = False
    light_power_W: float = 0.0        # 光源功率
    light_color_K: int = 4000         # 色温 (K)
    light_lumen: int = 0              # 光通量 (lm)
    is_translucent: bool = False       # 是否透光

    # 来源追踪
    physics_source: Literal["knowledge_base", "ml_prediction", "default"] = "default"
    physics_confidence: float = 0.5     # 物理参数置信度 0-1
    ml_model_version: str = ""         # 如果是ML预测，记录模型版本


# ─────────────────────────────────────────────────────────
# 机器人交互层
# ─────────────────────────────────────────────────────────

@dataclass
class RobotActions:
    """机器人可执行的动作及其难度评估"""
    push: bool = True                          # 是否可以推
    pull: bool = False                         # 是否可以拉（通常需要抓取）
    lift: bool = True                          # 是否可以抬起
    tilt: bool = False                         # 是否可以倾斜
    rotate: bool = False                       # 是否可以旋转
    openable: bool = False                     # 是否可开合（门/抽屉/柜门）
    attachable: bool = False                   # 是否可壁挂/固定

    # 难度评估（0=不可能，1=非常简单，5=非常困难）
    push_difficulty: int = 1
    pull_difficulty: int = 3
    lift_difficulty: int = 2
    rearrange_difficulty: int = 2

    # 力/扭矩需求估算
    force_push_N: float = 10.0          # 推动所需力 (N)
    force_lift_N: float = 100.0         # 抬起所需力 (N)
    torque_Nm: float = 0.0             # 操作扭矩 (N·m)

    # 夹爪建议
    grasp_type: GraspType = GraspType.TWO_HAND
    suction_possible: bool = False     # 是否可用吸盘
    magnetic_possible: bool = False    # 是否可用磁性夹爪


@dataclass
class SafetyConstraints:
    """安全约束 — 机器人操作边界"""
    electrical_hazard: bool = False     # 电气危险
    hot_surface: bool = False           # 表面高温
    fragile: bool = False               # 易碎
    chemical_hazard: bool = False       # 化学危险
    weight_limit_kg: float = 50.0       # 单次搬运重量上限
    children_safe: bool = True          # 儿童接触是否安全


@dataclass
class RobotInteraction:
    """机器人交互描述"""
    graspable: bool = True
    moveable: bool = True
    path_obstacle: bool = False         # 是否会阻碍机器人路径
    under_clearance_needed: float = 0.0 # 下方净空需求
    actions: RobotActions = field(default_factory=RobotActions)
    safety: SafetyConstraints = field(default_factory=SafetyConstraints)


# ─────────────────────────────────────────────────────────
# 统一对象模型 — 完整 schema
# ─────────────────────────────────────────────────────────

@dataclass
class BuildingObject:
    """
    建筑对象统一数据模型

    采用 CNN 层次化设计：
      - geometry   (L1): 像素级几何 → CAD 线条 → 包围盒
      - semantic   (L2): 部件 → 物体类型 → 场景语义
      - physics    (L3): 物理属性向量（ML 可处理）

    对象 ID 命名规范：
      {category}-{subcategory}-{index:03d}
      例：furniture-sofa-001, appliance-tv-003, structure-wall-001
    """
    # 身份标识
    id: str = ""
    name: str = ""                       # 显示名称（中文）
    name_en: str = ""                    # 英文名称（用于模型）

    # 分类
    category: ObjectCategory = ObjectCategory.FURNITURE
    subcategory: str = ""                # 细分类型：sofa/bed/cabinet/tv...

    # 三层抽象（CNN 层次）
    geometry: Geometry = field(default_factory=Geometry)
    semantic: Semantic = field(default_factory=Semantic)
    physics: PhysicsProperties = field(default_factory=PhysicsProperties)

    # 机器人交互
    robot: RobotInteraction = field(default_factory=RobotInteraction)

    # 来源追踪
    source_file: str = ""               # 来源文件
    source_type: Literal["cad", "vr", "material_catalog", "manual", "ml"] = "manual"
    scene_id: str = ""                  # 所属场景
    position_3d: tuple[float, float, float] = (0.0, 0.0, 0.0)   # 世界坐标
    rotation_y: float = 0.0             # Y轴旋转角 (rad)
    visible_in_vr: bool = False         # VR 中是否可见

    # 向量嵌入（由 neural encoder 生成，保存时为 None）
    embedding: Optional[list[float]] = None
    physics_vector: Optional[list[float]] = None  # 物理属性向量

    def __post_init__(self):
        if not self.id:
            cat_prefix = self.category.value[:3]
            self.id = f"{cat_prefix}-{self.subcategory}-{uuid.uuid4().hex[:6]}"


# ─────────────────────────────────────────────────────────
# 物理属性自动补全引擎
# （ML 预测 + 知识库查询）
# ─────────────────────────────────────────────────────────

class PhysicsPropertyEstimator:
    """
    物理属性自动补全

    工作流程（CNN 推理类）：
      输入特征 → [材质先验 | 几何先验 | 视觉特征] → 预测物理参数

    对于没有精确数据的物体，用 ML 预测 + 物理先验填充
    """

    # 材质默认密度表 (g/cm³)
    MATERIAL_DENSITY = {
        "fabric": 0.35,
        "wood": 0.65,
        "metal": 7.8,
        "glass": 2.5,
        "ceramic": 2.4,
        "stone": 2.7,
        "plastic": 0.95,
        "composite": 1.2,
        "rubber": 1.1,
    }

    # 材质摩擦系数表
    MATERIAL_FRICTION = {
        "fabric": (0.6, 0.5),
        "wood": (0.5, 0.4),
        "metal": (0.3, 0.2),
        "glass": (0.2, 0.15),
        "ceramic": (0.3, 0.25),
        "stone": (0.55, 0.45),
        "plastic": (0.35, 0.3),
        "rubber": (0.8, 0.7),
        "composite": (0.4, 0.35),
    }

    # 家具典型重量估算 (kg)
    FURNITURE_WEIGHTS = {
        "sofa": (40, 120),
        "bed_single": (30, 50),
        "bed_double": (50, 90),
        "dining_table": (20, 60),
        "dining_chair": (3, 8),
        "desk": (15, 40),
        "office_chair": (10, 20),
        "cabinet": (20, 80),
        "wardrobe": (40, 120),
        "tv_stand": (20, 50),
        "coffee_table": (10, 30),
        "bookshelf": (15, 50),
        "nightstand": (5, 15),
        "dresser": (20, 40),
        "bathroom_vanity": (15, 35),
    }

    # 家电典型重量
    APPLIANCE_WEIGHTS = {
        "tv": (10, 80),
        "refrigerator": (50, 150),
        "washing_machine": (55, 85),
        "air_conditioner_indoor": (8, 15),
        "air_conditioner_outdoor": (30, 70),
        "microwave": (10, 20),
        "dishwasher": (30, 60),
        "oven": (30, 60),
        "vacuum_robot": (3, 6),
    }

    def estimate_from_geometry(self, obj: BuildingObject) -> PhysicsProperties:
        """从几何信息估算物理属性（CNN 几何特征流）"""
        bbox = obj.geometry.bounding_box
        vol_m3 = bbox.volume

        # 识别材质（从 subcategory + semantic 推断）
        primary_material = self._infer_material(obj.subcategory, obj.semantic.functional_group)
        density = self.MATERIAL_DENSITY.get(primary_material, 0.5)

        # 估算质量
        typical_range = self.FURNITURE_WEIGHTS.get(obj.subcategory,
                    self.APPLIANCE_WEIGHTS.get(obj.subcategory, (5, 30)))
        est_mass = sum(typical_range) / 2

        # 用体积密度验证（如果体积异常大/小，用体积算）
        vol_density_mass = density * 1000 * vol_m3  # g/cm3 → kg/m3
        if vol_m3 > 0.01:  # 体积大于 10L，用体积估算
            est_mass = 0.7 * est_mass + 0.3 * vol_density_mass

        # 摩擦系数
        fric_static, fric_dynamic = self.MATERIAL_FRICTION.get(
            primary_material, (0.4, 0.3))

        # 刚度（材质决定）
        stiffness_map = {
            "metal": 50000,
            "glass": 70000,
            "ceramic": 60000,
            "wood": 10000,
            "plastic": 5000,
            "fabric": 100,
        }
        stiffness = stiffness_map.get(primary_material, 10000)

        return PhysicsProperties(
            mass_kg=round(est_mass, 1),
            density_gcm3=density,
            friction_static=fric_static,
            friction_dynamic=fric_dynamic,
            friction_surface=SurfaceType.HARD_SMOOTH if primary_material in ["glass", "ceramic"]
                          else SurfaceType.WOOD if primary_material == "wood"
                          else SurfaceType.FABRIC if primary_material == "fabric"
                          else SurfaceType.HARD_ROUGH,
            stiffness_Nm=stiffness,
            young_modulus_GPa=stiffness / 1e9,
            physics_source="ml_prediction",
            physics_confidence=0.6,
        )

    def estimate_from_category(self, subcategory: str, category: str) -> PhysicsProperties:
        """从类别直接估算（最简化快速路径）"""
        weights = self.FURNITURE_WEIGHTS.copy()
        weights.update(self.APPLIANCE_WEIGHTS)
        typical_range = weights.get(subcategory, (5, 30))
        est_mass = sum(typical_range) / 2
        return self.estimate_from_geometry(
            BuildingObject(subcategory=subcategory, category=ObjectCategory(category))
        )

    def _infer_material(self, subcategory: str, functional_group: str) -> str:
        """从子类别推断主要材质"""
        material_map = {
            "sofa": "fabric",
            "chair": "wood",
            "table": "wood",
            "bed": "fabric",
            "cabinet": "wood",
            "wardrobe": "wood",
            "tv": "metal",
            "refrigerator": "metal",
            "oven": "metal",
            "microwave": "metal",
            "shelf": "wood",
            "desk": "wood",
            "dining_table": "wood",
            "curtain": "fabric",
            "rug": "fabric",
            "mirror": "glass",
            "plant": "organic",
            "lamp": "metal",
            "tv": "glass",
        }
        return material_map.get(subcategory, "composite")

    def merge_with_knowledge(self,
                             estimated: PhysicsProperties,
                             knowledge: Optional[PhysicsProperties]) -> PhysicsProperties:
        """合并 ML 预测和知识库数据（知识优先）"""
        if knowledge is None:
            return estimated

        # 知识库数据替换默认值
        result = estimated
        for field_name in ["mass_kg", "density_gcm3", "friction_static",
                           "friction_dynamic", "stiffness_Nm", "young_modulus_GPa",
                           "thermal_conductivity_WmK"]:
            know_val = getattr(knowledge, field_name, None)
            if know_val is not None and know_val != 0:
                setattr(result, field_name, know_val)

        result.physics_source = "knowledge_base"
        result.physics_confidence = max(estimated.physics_confidence, 0.9)
        return result


# ─────────────────────────────────────────────────────────
# 对象库管理
# ─────────────────────────────────────────────────────────

class ObjectLibrary:
    """
    对象库 — 管理所有建筑对象，支持 schema 验证和导出。

    主要功能：
      - add_object()     添加对象（自动 schema 验证）
      - query()          按类别/房间/标签查询
      - export()         导出为 JSON / CSV
      - to_scene_graph() 导出为场景图谱格式
    """

    def __init__(self):
        self._objects: dict[str, BuildingObject] = {}
        self._estimator = PhysicsPropertyEstimator()

    @property
    def objects(self) -> list[BuildingObject]:
        return list(self._objects.values())

    def add_object(self, obj: BuildingObject,
                   auto_fill_physics: bool = True) -> BuildingObject:
        """添加对象，自动补全物理属性"""
        if auto_fill_physics and obj.physics.physics_source == "default":
            obj.physics = self._estimator.estimate_from_geometry(obj)
        self._objects[obj.id] = obj
        return obj

    def add_objects_batch(self, objs: list[BuildingObject]) -> int:
        """批量添加"""
        count = 0
        for obj in objs:
            if isinstance(obj, dict):
                obj = BuildingObject(**obj)
            self.add_object(obj)
            count += 1
        return count

    def query(self,
              category: Optional[str] = None,
              room_type: Optional[str] = None,
              style: Optional[str] = None,
              subcategory: Optional[str] = None) -> list[BuildingObject]:
        """多条件查询"""
        results = self._objects.values()
        if category:
            results = [o for o in results if o.category.value == category]
        if subcategory:
            results = [o for o in results if o.subcategory == subcategory]
        if room_type:
            results = [o for o in results
                      if room_type in o.semantic.room_types]
        if style:
            results = [o for o in results
                      if style in o.semantic.style_tags]
        return list(results)

    def export_json(self, path: Optional[str] = None) -> str:
        """导出为 JSON"""
        data = [asdict(o) for o in self._objects.values()]
        import json
        s = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(s)
        return s

    def import_json(self, path: str) -> int:
        """从 JSON 导入"""
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            obj = BuildingObject(**item)
            self.add_object(obj, auto_fill_physics=False)
            count += 1
        return count

    def __len__(self) -> int:
        return len(self._objects)


# ─────────────────────────────────────────────────────────
# 预定义对象模板库
# ─────────────────────────────────────────────────────────

def create_furniture_templates() -> list[BuildingObject]:
    """从知识库创建家具对象模板"""
    templates = [
        # 客厅
        BuildingObject(
            id="furniture-sofa-001",
            name="三人位布艺沙发",
            name_en="3-seater fabric sofa",
            category=ObjectCategory.FURNITURE,
            subcategory="sofa",
            geometry=Geometry(
                bounding_box=BoundingBox(x=2.2, y=0.85, z=0.95),
                clearance=Clearance(front=0.9, back=0.3, left=0.3, right=0.3, above=0.5),
                grasp_points=[GraspPoint(type="edge", position=(1.0, 0.4, 0))],
            ),
            semantic=Semantic(
                room_types=["客厅", "大堂", "酒店大堂", "休憩区"],
                style_tags=["现代简约", "北欧", "意式极简", "奶油风"],
                functional_group="seating",
                typical_neighbors=["茶几", "地毯", "单人椅", "电视柜"],
            ),
            robot=RobotInteraction(
                graspable=True,
                moveable=True,
                path_obstacle=False,
                actions=RobotActions(
                    push=True, pull=True, lift=True,
                    push_difficulty=1, pull_difficulty=3, lift_difficulty=2,
                    force_push_N=15, force_lift_N=150,
                    grasp_type=GraspType.TWO_HAND,
                )
            ),
            source_type="manual",
        ),
        BuildingObject(
            id="furniture-coffee_table-001",
            name="客厅茶几",
            name_en="coffee table",
            category=ObjectCategory.FURNITURE,
            subcategory="coffee_table",
            geometry=Geometry(
                bounding_box=BoundingBox(x=1.2, y=0.45, z=0.6),
                clearance=Clearance(front=0.6, back=0.3, left=0.2, right=0.2, above=0.4),
                grasp_points=[GraspPoint(type="edge", position=(0.5, 0.2, 0))],
            ),
            semantic=Semantic(
                room_types=["客厅"],
                style_tags=["现代简约", "北欧", "实木"],
                functional_group="table",
                typical_neighbors=["沙发", "地毯"],
            ),
            robot=RobotInteraction(
                graspable=True,
                moveable=True,
                actions=RobotActions(
                    push=True, pull=True, lift=True,
                    push_difficulty=1, pull_difficulty=2, lift_difficulty=1,
                    force_push_N=10, force_lift_N=80,
                    grasp_type=GraspType.TWO_HAND,
                )
            ),
            source_type="manual",
        ),
        BuildingObject(
            id="furniture-dining_table-001",
            name="餐桌",
            name_en="dining table",
            category=ObjectCategory.FURNITURE,
            subcategory="dining_table",
            geometry=Geometry(
                bounding_box=BoundingBox(x=1.6, y=0.75, z=0.8),
                clearance=Clearance(front=0.8, back=0.3, left=0.3, right=0.3, above=0.5),
                grasp_points=[GraspPoint(type="edge", position=(0.7, 0.3, 0))],
            ),
            semantic=Semantic(
                room_types=["餐厅", "客厅", "开放式厨房"],
                style_tags=["现代简约", "实木", "意式"],
                functional_group="table",
                typical_neighbors=["餐椅", "餐边柜"],
            ),
            robot=RobotInteraction(
                graspable=True,
                moveable=True,
                actions=RobotActions(
                    push=True, pull=True, lift=True,
                    push_difficulty=1, lift_difficulty=3,
                    force_push_N=12, force_lift_N=200,
                    grasp_type=GraspType.TWO_HAND,
                )
            ),
            source_type="manual",
        ),
        BuildingObject(
            id="furniture-bed-001",
            name="双人床",
            name_en="double bed",
            category=ObjectCategory.FURNITURE,
            subcategory="bed_double",
            geometry=Geometry(
                bounding_box=BoundingBox(x=1.8, y=0.5, z=2.0),
                clearance=Clearance(front=0.6, back=0.3, left=0.3, right=0.3, above=0.6),
                grasp_points=[],
            ),
            semantic=Semantic(
                room_types=["卧室", "主卧", "次卧", "酒店客房"],
                style_tags=["现代简约", "北欧", "奶油风"],
                functional_group="sleeping",
                typical_neighbors=["床头柜", "衣柜", "梳妆台"],
            ),
            robot=RobotInteraction(
                graspable=False,
                moveable=False,  # 床通常固定
                path_obstacle=True,
                actions=RobotActions(push=False, pull=False, lift=False),
            ),
            source_type="manual",
        ),
        BuildingObject(
            id="furniture-wardrobe-001",
            name="衣柜",
            name_en="wardrobe",
            category=ObjectCategory.FURNITURE,
            subcategory="wardrobe",
            geometry=Geometry(
                bounding_box=BoundingBox(x=1.8, y=2.2, z=0.6),
                wall_mounted=False,
                clearance=Clearance(front=0.7, back=0.1, left=0.1, right=0.1, above=0.2),
                grasp_points=[],
            ),
            semantic=Semantic(
                room_types=["卧室", "主卧", "次卧", "衣帽间"],
                style_tags=["现代简约", "北欧", "意式"],
                functional_group="storage",
                typical_neighbors=["床", "梳妆台"],
            ),
            robot=RobotInteraction(
                graspable=False,
                moveable=True,
                path_obstacle=True,
                actions=RobotActions(
                    push=True, pull=True, lift=False,
                    push_difficulty=2, pull_difficulty=4,
                    force_push_N=20,
                )
            ),
            source_type="manual",
        ),
        # 厨房
        BuildingObject(
            id="furniture-kitchen_cabinet-001",
            name="橱柜",
            name_en="kitchen cabinet",
            category=ObjectCategory.FURNITURE,
            subcategory="kitchen_cabinet",
            geometry=Geometry(
                bounding_box=BoundingBox(x=3.0, y=0.9, z=0.6),
                wall_mounted=False,
                clearance=Clearance(front=0.7, back=0.1, left=0.1, right=0.1, above=0.5),
            ),
            semantic=Semantic(
                room_types=["厨房"],
                style_tags=["现代简约", "极简"],
                functional_group="kitchen",
                typical_neighbors=["油烟机", "水槽", "灶台"],
            ),
            robot=RobotInteraction(
                graspable=False,
                moveable=False,
                path_obstacle=True,
                actions=RobotActions(
                    openable=True,
                    push=True, lift=False,
                    push_difficulty=2,
                )
            ),
            source_type="manual",
        ),
        # 卫生间
        BuildingObject(
            id="furniture-toilet-001",
            name="马桶",
            name_en="toilet",
            category=ObjectCategory.FURNITURE,
            subcategory="toilet",
            geometry=Geometry(
                bounding_box=BoundingBox(x=0.4, y=0.8, z=0.7),
                floor_mounted=True,
                clearance=Clearance(front=0.5, back=0.2, left=0.2, right=0.2, above=0.5),
            ),
            semantic=Semantic(
                room_types=["卫生间", "公卫"],
                functional_group="hygiene",
                typical_neighbors=["洗手盆", "淋浴房", "浴室柜"],
            ),
            robot=RobotInteraction(
                graspable=False,
                moveable=False,
                path_obstacle=True,
                actions=RobotActions(push=False, lift=False),
                safety=SafetyConstraints(electrical_hazard=False, fragile=True),
            ),
            source_type="manual",
        ),
        BuildingObject(
            id="furniture-bidet-001",
            name="智能马桶",
            name_en="smart toilet",
            category=ObjectCategory.FURNITURE,
            subcategory="smart_toilet",
            geometry=Geometry(
                bounding_box=BoundingBox(x=0.42, y=0.85, z=0.72),
                floor_mounted=True,
                clearance=Clearance(front=0.5, back=0.2, left=0.25, right=0.25, above=0.5),
            ),
            semantic=Semantic(
                room_types=["卫生间"],
                functional_group="hygiene",
                typical_neighbors=["洗手盆"],
            ),
            robot=RobotInteraction(
                graspable=False,
                moveable=False,
                path_obstacle=True,
                actions=RobotActions(push=False, lift=False),
                safety=SafetyConstraints(electrical_hazard=True, fragile=True),
            ),
            source_type="manual",
        ),
        BuildingObject(
            id="furniture-bathtub-001",
            name="浴缸",
            name_en="bathtub",
            category=ObjectCategory.FURNITURE,
            subcategory="bathtub",
            geometry=Geometry(
                bounding_box=BoundingBox(x=1.7, y=0.6, z=0.75),
                floor_mounted=True,
                clearance=Clearance(front=0.5, back=0.3, left=0.3, right=0.3, above=0.5),
            ),
            semantic=Semantic(
                room_types=["卫生间"],
                functional_group="hygiene",
                typical_neighbors=["浴室柜", "淋浴房"],
            ),
            robot=RobotInteraction(
                graspable=False,
                moveable=False,
                path_obstacle=True,
                actions=RobotActions(push=False, lift=False),
            ),
            source_type="manual",
        ),
    ]
    return templates


def create_appliance_templates() -> list[BuildingObject]:
    """创建家电对象模板"""
    return [
        BuildingObject(
            id="appliance-tv-001",
            name="电视",
            name_en="television",
            category=ObjectCategory.APPLIANCE,
            subcategory="tv",
            geometry=Geometry(
                bounding_box=BoundingBox(x=1.4, y=0.8, z=0.1),
                wall_mounted=True,
                clearance=Clearance(front=0.5, back=0.1, left=0.1, right=0.1, above=0.1),
                grasp_points=[GraspPoint(type="edge", position=(0, 0, 0))],
            ),
            semantic=Semantic(
                room_types=["客厅", "卧室", "酒店客房", "会议室"],
                functional_group="entertainment",
                typical_neighbors=["电视柜", "沙发"],
            ),
            physics=PhysicsProperties(
                mass_kg=25.0,
                density_gcm3=0.8,
                friction_static=0.3,
                friction_dynamic=0.2,
                stiffness_Nm=5000,
                physics_source="knowledge_base",
                physics_confidence=0.9,
            ),
            robot=RobotInteraction(
                graspable=True,
                moveable=True,
                actions=RobotActions(
                    push=False, pull=False, lift=True,
                    lift_difficulty=2, force_lift_N=50,
                    grasp_type=GraspType.TWO_HAND,
                ),
                safety=SafetyConstraints(electrical_hazard=True),
            ),
            source_type="manual",
        ),
        BuildingObject(
            id="appliance-refrigerator-001",
            name="冰箱",
            name_en="refrigerator",
            category=ObjectCategory.APPLIANCE,
            subcategory="refrigerator",
            geometry=Geometry(
                bounding_box=BoundingBox(x=0.9, y=1.9, z=0.7),
                floor_mounted=True,
                clearance=Clearance(front=0.7, back=0.1, left=0.1, right=0.1, above=0.3),
            ),
            semantic=Semantic(
                room_types=["厨房", "开放式厨房"],
                functional_group="kitchen_appliance",
                typical_neighbors=["橱柜", "水槽"],
            ),
            physics=PhysicsProperties(
                mass_kg=90.0,
                density_gcm3=0.9,
                friction_static=0.4,
                friction_dynamic=0.3,
                physics_source="knowledge_base",
                physics_confidence=0.95,
            ),
            robot=RobotInteraction(
                graspable=True,
                moveable=True,
                path_obstacle=True,
                actions=RobotActions(
                    push=True, pull=False, lift=False,
                    push_difficulty=2, force_push_N=30,
                ),
                safety=SafetyConstraints(electrical_hazard=True, weight_limit_kg=30),
            ),
            source_type="manual",
        ),
        BuildingObject(
            id="appliance-ac_indoor-001",
            name="壁挂空调室内机",
            name_en="wall-mounted AC indoor unit",
            category=ObjectCategory.APPLIANCE,
            subcategory="air_conditioner_indoor",
            geometry=Geometry(
                bounding_box=BoundingBox(x=0.9, y=0.3, z=0.2),
                ceiling_mounted=False,
                wall_mounted=True,
                clearance=Clearance(front=1.0, back=0.1, left=0.2, right=0.2, above=0.1),
            ),
            semantic=Semantic(
                room_types=["客厅", "卧室", "书房", "酒店客房", "办公室"],
                functional_group="hvac",
            ),
            physics=PhysicsProperties(
                mass_kg=11.0,
                physics_source="knowledge_base",
                physics_confidence=0.95,
            ),
            robot=RobotInteraction(
                graspable=True,
                moveable=False,
                path_obstacle=False,
                actions=RobotActions(
                    push=False, pull=False, lift=True,
                    lift_difficulty=3, force_lift_N=20,
                ),
                safety=SafetyConstraints(electrical_hazard=True),
            ),
            source_type="manual",
        ),
    ]


# ─────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 演示：创建对象库
    library = ObjectLibrary()

    # 添加预定义模板
    for obj in create_furniture_templates():
        library.add_object(obj)

    for obj in create_appliance_templates():
        library.add_object(obj)

    print(f"对象库: {len(library)} 个对象")
    print("\n按类别统计:")
    from collections import Counter
    cats = Counter(o.category.value for o in library.objects)
    for cat, cnt in cats.items():
        print(f"  {cat}: {cnt}")

    # 查询演示
    living_room = library.query(room_type="客厅")
    print(f"\n客厅可用对象: {len(living_room)} 个")

    # 导出
    json_out = library.export_json()
    print(f"\n导出 JSON 大小: {len(json_out)/1024:.1f} KB")
