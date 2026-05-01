"""
建筑物理 AI 世界模型 Demo - 完整版
==================================
包含：建筑结构、家具、家电、软装、机电设施

启动方式：
    streamlit run app_complete.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# ============================================================
# 数据模型
# ============================================================

@dataclass
class PhysicsProperties:
    """物理属性"""
    mass: Optional[float] = None
    material: Optional[str] = None
    stiffness: Optional[float] = None
    friction: Optional[float] = None
    is_structural: Optional[bool] = None
    conductivity: Optional[float] = None
    hardness: Optional[str] = None  # 硬度等级

@dataclass
class FunctionProperties:
    """功能属性"""
    type: str
    circuit: Optional[str] = None
    voltage: Optional[float] = None
    power: Optional[float] = None  # 功率 W
    water_pipe: Optional[str] = None  # 水管编号
    gas_pipe: Optional[str] = None  # 燃气管编号

@dataclass
class RobotInteraction:
    """机器人交互属性"""
    graspable: bool = False
    openable: bool = False
    movable: bool = False  # 是否可移动
    path_obstacle: bool = False
    fragile: bool = False  # 是否易碎
    max_force: Optional[float] = None  # 最大施力 N

@dataclass
class BuildingObject:
    """建筑对象"""
    id: str
    name: str
    type: str
    category: str  # structure, furniture, appliance, soft, utility
    position: List[float]
    rotation: List[float]
    dimensions: Dict[str, float]
    color: str
    physics: Optional[PhysicsProperties] = None
    function: Optional[FunctionProperties] = None
    robot_interaction: Optional[RobotInteraction] = None


# ============================================================
# 完整建筑数据 - 客厅+厨房+卧室场景
# ============================================================

def create_complete_building() -> List[BuildingObject]:
    """创建完整建筑场景"""
    objects = []
    
    # ========================================
    # 1. 建筑结构 - structure
    # ========================================
    
    # 地板 - 客厅
    objects.append(BuildingObject(
        id="floor-living",
        name="客厅地板",
        type="floor",
        category="structure",
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        dimensions={"width": 8, "height": 0.15, "depth": 6},
        color="#E8E0D5",
        physics=PhysicsProperties(
            mass=0,
            material="大理石瓷砖",
            friction=0.5,
            is_structural=True,
            hardness="硬"
        )
    ))
    
    # 地板 - 厨房
    objects.append(BuildingObject(
        id="floor-kitchen",
        name="厨房地板",
        type="floor",
        category="structure",
        position=[6, 0, 0],
        rotation=[0, 0, 0],
        dimensions={"width": 4, "height": 0.15, "depth": 6},
        color="#D4C4B0",
        physics=PhysicsProperties(
            mass=0,
            material="防滑瓷砖",
            friction=0.7,
            is_structural=True,
            hardness="硬"
        )
    ))
    
    # 墙体 - 后墙（带窗户）
    objects.append(BuildingObject(
        id="wall-back",
        name="后承重墙",
        type="wall",
        category="structure",
        position=[0, 1.5, -3],
        rotation=[0, 0, 0],
        dimensions={"width": 8, "height": 3, "depth": 0.24},
        color="#C4B5A0",
        physics=PhysicsProperties(
            mass=2400,
            material="钢筋混凝土",
            stiffness=30000,
            friction=0.5,
            is_structural=True,
            hardness="极硬"
        )
    ))
    
    # 墙体 - 左墙
    objects.append(BuildingObject(
        id="wall-left",
        name="左侧承重墙",
        type="wall",
        category="structure",
        position=[-4, 1.5, 0],
        rotation=[0, 90, 0],
        dimensions={"width": 6, "height": 3, "depth": 0.24},
        color="#C4B5A0",
        physics=PhysicsProperties(
            mass=1800,
            material="钢筋混凝土",
            stiffness=30000,
            friction=0.5,
            is_structural=True,
            hardness="极硬"
        )
    ))
    
    # 墙体 - 右墙（隔墙到厨房）
    objects.append(BuildingObject(
        id="wall-right-living",
        name="客厅右墙",
        type="wall",
        category="structure",
        position=[4, 1.5, -2.5],
        rotation=[0, 90, 0],
        dimensions={"width": 1, "height": 3, "depth": 0.12},
        color="#D4C4B0",
        physics=PhysicsProperties(
            mass=300,
            material="轻质砖",
            stiffness=8000,
            friction=0.4,
            is_structural=False,
            hardness="中"
        )
    ))
    
    # 墙体 - 厨房右墙
    objects.append(BuildingObject(
        id="wall-right-kitchen",
        name="厨房右墙",
        type="wall",
        category="structure",
        position=[4, 1.5, 2],
        rotation=[0, 90, 0],
        dimensions={"width": 2, "height": 3, "depth": 0.12},
        color="#D4C4B0",
        physics=PhysicsProperties(
            mass=600,
            material="轻质砖",
            stiffness=8000,
            friction=0.4,
            is_structural=False,
            hardness="中"
        )
    ))
    
    # 厨房后墙
    objects.append(BuildingObject(
        id="wall-kitchen-back",
        name="厨房后墙",
        type="wall",
        category="structure",
        position=[6, 1.5, -3],
        rotation=[0, 0, 0],
        dimensions={"width": 4, "height": 3, "depth": 0.24},
        color="#C4B5A0",
        physics=PhysicsProperties(
            mass=1200,
            material="钢筋混凝土",
            stiffness=30000,
            friction=0.5,
            is_structural=True,
            hardness="极硬"
        )
    ))
    
    # 门 - 客厅入口
    objects.append(BuildingObject(
        id="door-living",
        name="客厅入口门",
        type="door",
        category="structure",
        position=[4, 0, 0.5],
        rotation=[0, 0, 0],
        dimensions={"width": 0.9, "height": 2.1, "depth": 0.05},
        color="#8B5A2B",
        physics=PhysicsProperties(
            mass=25,
            material="实木",
            stiffness=12000,
            friction=0.3,
            hardness="中"
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            openable=True,
            max_force=50
        )
    ))
    
    # 窗户 - 客厅大窗
    objects.append(BuildingObject(
        id="window-living",
        name="客厅落地窗",
        type="window",
        category="structure",
        position=[0, 1.2, -3],
        rotation=[0, 0, 0],
        dimensions={"width": 2.5, "height": 2.2, "depth": 0.08},
        color="#87CEEB",
        physics=PhysicsProperties(
            mass=45,
            material="铝合金+中空玻璃",
            stiffness=70000,
            friction=0.2,
            hardness="硬"
        )
    ))
    
    # ========================================
    # 2. 家具 - furniture
    # ========================================
    
    # 沙发 - 三人位
    objects.append(BuildingObject(
        id="sofa-main",
        name="三人位沙发",
        type="sofa",
        category="furniture",
        position=[0, 0.4, 1.5],
        rotation=[0, 0, 0],
        dimensions={"width": 2.2, "height": 0.8, "depth": 0.9},
        color="#4A4A4A",
        physics=PhysicsProperties(
            mass=80,
            material="布艺+海绵+木框架",
            stiffness=50,
            friction=0.6,
            hardness="软"
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            movable=False,
            path_obstacle=True
        )
    ))
    
    # 茶几
    objects.append(BuildingObject(
        id="coffee-table",
        name="茶几",
        type="table",
        category="furniture",
        position=[0, 0.35, 0],
        rotation=[0, 0, 0],
        dimensions={"width": 1.2, "height": 0.45, "depth": 0.6},
        color="#654321",
        physics=PhysicsProperties(
            mass=25,
            material="实木+钢化玻璃",
            stiffness=12000,
            friction=0.4,
            hardness="中"
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            movable=True,
            path_obstacle=True,
            fragile=True,
            max_force=100
        )
    ))
    
    # 电视柜
    objects.append(BuildingObject(
        id="tv-stand",
        name="电视柜",
        type="cabinet",
        category="furniture",
        position=[0, 0.35, -2.3],
        rotation=[0, 0, 0],
        dimensions={"width": 2.0, "height": 0.45, "depth": 0.45},
        color="#3D2914",
        physics=PhysicsProperties(
            mass=40,
            material="密度板",
            stiffness=8000,
            friction=0.4,
            hardness="中"
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            movable=False,
            path_obstacle=True
        )
    ))
    
    # 单人沙发
    objects.append(BuildingObject(
        id="sofa-single",
        name="单人沙发",
        type="sofa",
        category="furniture",
        position=[-2.5, 0.4, 1],
        rotation=[0, 45, 0],
        dimensions={"width": 0.8, "height": 0.75, "depth": 0.8},
        color="#5D4E37",
        physics=PhysicsProperties(
            mass=35,
            material="布艺+海绵",
            stiffness=50,
            friction=0.6,
            hardness="软"
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            movable=True,
            path_obstacle=True
        )
    ))
    
    # 边几
    objects.append(BuildingObject(
        id="side-table",
        name="边几",
        type="table",
        category="furniture",
        position=[-2.8, 0.45, 0],
        rotation=[0, 0, 0],
        dimensions={"width": 0.5, "height": 0.55, "depth": 0.5},
        color="#4A3728",
        physics=PhysicsProperties(
            mass=8,
            material="实木",
            stiffness=12000,
            friction=0.4,
            hardness="中"
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            movable=True,
            path_obstacle=False,
            max_force=50
        )
    ))
    
    # 书架
    objects.append(BuildingObject(
        id="bookshelf",
        name="书架",
        type="shelf",
        category="furniture",
        position=[-3.5, 1, -1],
        rotation=[0, 90, 0],
        dimensions={"width": 1.5, "height": 2.0, "depth": 0.35},
        color="#8B7355",
        physics=PhysicsProperties(
            mass=60,
            material="实木",
            stiffness=10000,
            friction=0.5,
            hardness="中"
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            movable=False,
            path_obstacle=True
        )
    ))
    
    # 餐桌（厨房区域）
    objects.append(BuildingObject(
        id="dining-table",
        name="餐桌",
        type="table",
        category="furniture",
        position=[6, 0.75, 0],
        rotation=[0, 0, 0],
        dimensions={"width": 1.4, "height": 0.75, "depth": 0.8},
        color="#5D4037",
        physics=PhysicsProperties(
            mass=50,
            material="实木",
            stiffness=12000,
            friction=0.4,
            hardness="中"
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            movable=True,
            path_obstacle=True
        )
    ))
    
    # 餐椅 x4
    for i, (dx, dz) in enumerate([(-0.5, -0.6), (0.5, -0.6), (-0.5, 0.6), (0.5, 0.6)]):
        objects.append(BuildingObject(
            id=f"dining-chair-{i+1}",
            name=f"餐椅{i+1}",
            type="chair",
            category="furniture",
            position=[6 + dx, 0.45, 0 + dz],
            rotation=[0, 90 if i < 2 else -90, 0],
            dimensions={"width": 0.45, "height": 0.9, "depth": 0.5},
            color="#6D4C41",
            physics=PhysicsProperties(
                mass=5,
                material="实木+布艺",
                stiffness=8000,
                friction=0.5,
                hardness="中"
            ),
            robot_interaction=RobotInteraction(
                graspable=True,
                movable=True,
                path_obstacle=True
            )
        ))
    
    # ========================================
    # 3. 家电 - appliance
    # ========================================
    
    # 电视
    objects.append(BuildingObject(
        id="tv-main",
        name="液晶电视",
        type="tv",
        category="appliance",
        position=[0, 1.1, -2.5],
        rotation=[0, 0, 0],
        dimensions={"width": 1.5, "height": 0.85, "depth": 0.08},
        color="#1A1A1A",
        physics=PhysicsProperties(
            mass=25,
            material="金属+玻璃",
            stiffness=70000,
            friction=0.3,
            hardness="硬"
        ),
        function=FunctionProperties(
            type="display",
            circuit="L2-客厅电视",
            voltage=220,
            power=150
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            movable=False,
            path_obstacle=False,
            fragile=True,
            max_force=30
        )
    ))
    
    # 空调挂机
    objects.append(BuildingObject(
        id="ac-living",
        name="客厅空调",
        type="air_conditioner",
        category="appliance",
        position=[-3.5, 2.3, 0],
        rotation=[0, 90, 0],
        dimensions={"width": 1.0, "height": 0.32, "depth": 0.25},
        color="#FFFFFF",
        physics=PhysicsProperties(
            mass=15,
            material="塑料+金属",
            stiffness=5000,
            hardness="硬"
        ),
        function=FunctionProperties(
            type="air_conditioner",
            circuit="AC-客厅空调",
            voltage=220,
            power=2600
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            path_obstacle=False
        )
    ))
    
    # 冰箱
    objects.append(BuildingObject(
        id="refrigerator",
        name="双门冰箱",
        type="refrigerator",
        category="appliance",
        position=[7.5, 0.9, -2],
        rotation=[0, 0, 0],
        dimensions={"width": 0.9, "height": 1.8, "depth": 0.7},
        color="#E0E0E0",
        physics=PhysicsProperties(
            mass=80,
            material="金属+塑料",
            stiffness=5000,
            hardness="硬"
        ),
        function=FunctionProperties(
            type="refrigerator",
            circuit="K-厨房插座",
            voltage=220,
            power=200
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            openable=True,
            movable=False,
            path_obstacle=True
        )
    ))
    
    # 洗衣机
    objects.append(BuildingObject(
        id="washing-machine",
        name="滚筒洗衣机",
        type="washing_machine",
        category="appliance",
        position=[7.5, 0.45, 2],
        rotation=[0, 0, 0],
        dimensions={"width": 0.6, "height": 0.85, "depth": 0.6},
        color="#F5F5F5",
        physics=PhysicsProperties(
            mass=70,
            material="金属+塑料",
            stiffness=5000,
            hardness="硬"
        ),
        function=FunctionProperties(
            type="washing_machine",
            circuit="K-厨房插座",
            water_pipe="W-洗衣机",
            voltage=220,
            power=500
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            openable=True,
            path_obstacle=True
        )
    ))
    
    # 微波炉
    objects.append(BuildingObject(
        id="microwave",
        name="微波炉",
        type="microwave",
        category="appliance",
        position=[6, 1.2, -2.5],
        rotation=[0, 0, 0],
        dimensions={"width": 0.5, "height": 0.35, "depth": 0.4},
        color="#C0C0C0",
        physics=PhysicsProperties(
            mass=12,
            material="金属+塑料",
            stiffness=5000,
            hardness="硬"
        ),
        function=FunctionProperties(
            type="microwave",
            circuit="K-厨房插座",
            voltage=220,
            power=1200
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            openable=True,
            path_obstacle=False
        )
    ))
    
    # 电饭煲
    objects.append(BuildingObject(
        id="rice-cooker",
        name="电饭煲",
        type="rice_cooker",
        category="appliance",
        position=[6.5, 0.9, -2.5],
        rotation=[0, 0, 0],
        dimensions={"width": 0.3, "height": 0.25, "depth": 0.3},
        color="#FFFFFF",
        physics=PhysicsProperties(
            mass=4,
            material="塑料+金属",
            hardness="中"
        ),
        function=FunctionProperties(
            type="rice_cooker",
            circuit="K-厨房插座",
            voltage=220,
            power=800
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            movable=True,
            path_obstacle=False
        )
    ))
    
    # ========================================
    # 4. 软装 - soft
    # ========================================
    
    # 地毯
    objects.append(BuildingObject(
        id="carpet-living",
        name="客厅地毯",
        type="carpet",
        category="soft",
        position=[0, 0.02, 0],
        rotation=[0, 0, 0],
        dimensions={"width": 3.0, "height": 0.02, "depth": 2.5},
        color="#8B7355",
        physics=PhysicsProperties(
            mass=5,
            material="羊毛",
            friction=0.7,
            hardness="软"
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            movable=True,
            path_obstacle=False
        )
    ))
    
    # 窗帘
    objects.append(BuildingObject(
        id="curtain-living",
        name="客厅窗帘",
        type="curtain",
        category="soft",
        position=[-0.8, 1.5, -2.96],
        rotation=[0, 0, 0],
        dimensions={"width": 1.2, "height": 2.5, "depth": 0.02},
        color="#D4A574",
        physics=PhysicsProperties(
            mass=3,
            material="亚麻",
            friction=0.3,
            hardness="软"
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            movable=True,
            path_obstacle=False
        )
    ))
    
    objects.append(BuildingObject(
        id="curtain-living-2",
        name="客厅窗帘右",
        type="curtain",
        category="soft",
        position=[0.8, 1.5, -2.96],
        rotation=[0, 0, 0],
        dimensions={"width": 1.2, "height": 2.5, "depth": 0.02},
        color="#D4A574",
        physics=PhysicsProperties(
            mass=3,
            material="亚麻",
            friction=0.3,
            hardness="软"
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            movable=True,
            path_obstacle=False
        )
    ))
    
    # 抱枕 x3
    for i, (dx, dz) in enumerate([(-0.7, 0), (0, 0), (0.7, 0)]):
        objects.append(BuildingObject(
            id=f"cushion-{i+1}",
            name=f"抱枕{i+1}",
            type="cushion",
            category="soft",
            position=[dx, 0.55, 1.3],
            rotation=[0, 0, 0],
            dimensions={"width": 0.45, "height": 0.45, "depth": 0.15},
            color=["#E57373", "#81C784", "#64B5F6"][i],
            physics=PhysicsProperties(
                mass=0.5,
                material="棉麻",
                friction=0.5,
                hardness="软"
            ),
            robot_interaction=RobotInteraction(
                graspable=True,
                movable=True,
                path_obstacle=False
            )
        ))
    
    # 装饰画
    objects.append(BuildingObject(
        id="painting-main",
        name="装饰画",
        type="painting",
        category="soft",
        position=[-3.5, 1.8, 1.5],
        rotation=[0, 90, 0],
        dimensions={"width": 0.8, "height": 0.6, "depth": 0.03},
        color="#D4A574",
        physics=PhysicsProperties(
            mass=3,
            material="画布+木框",
            hardness="中"
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            movable=True,
            path_obstacle=False,
            fragile=True
        )
    ))
    
    # 绿植
    objects.append(BuildingObject(
        id="plant-1",
        name="绿萝盆栽",
        type="plant",
        category="soft",
        position=[-3.5, 0.5, -2],
        rotation=[0, 0, 0],
        dimensions={"width": 0.4, "height": 1.0, "depth": 0.4},
        color="#228B22",
        physics=PhysicsProperties(
            mass=8,
            material="陶瓷+土壤+植物",
            friction=0.6,
            hardness="中"
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            movable=True,
            path_obstacle=False
        )
    ))
    
    # 台灯
    objects.append(BuildingObject(
        id="lamp-table",
        name="台灯",
        type="lamp",
        category="soft",
        position=[-2.8, 0.75, 0],
        rotation=[0, 0, 0],
        dimensions={"width": 0.25, "height": 0.45, "depth": 0.25},
        color="#F5DEB3",
        physics=PhysicsProperties(
            mass=2,
            material="金属+布艺灯罩",
            hardness="中"
        ),
        function=FunctionProperties(
            type="lamp",
            circuit="L3-卧室灯",
            voltage=220,
            power=40
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            movable=True,
            path_obstacle=False,
            fragile=True
        )
    ))
    
    # ========================================
    # 5. 机电设施 - utility
    # ========================================
    
    # 开关 - 客厅主灯
    objects.append(BuildingObject(
        id="switch-living-main",
        name="客厅主灯开关",
        type="switch",
        category="utility",
        position=[-3.88, 1.3, 0],
        rotation=[0, 90, 0],
        dimensions={"width": 0.086, "height": 0.086, "depth": 0.01},
        color="#F5F5F5",
        physics=PhysicsProperties(
            mass=0.1,
            material="塑料",
            hardness="硬"
        ),
        function=FunctionProperties(
            type="switch",
            circuit="L1-客厅主灯",
            voltage=220,
            power=0
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            path_obstacle=False,
            max_force=10
        )
    ))
    
    # 开关 - 空调
    objects.append(BuildingObject(
        id="switch-ac",
        name="空调开关",
        type="switch",
        category="utility",
        position=[-3.88, 1.6, 0],
        rotation=[0, 90, 0],
        dimensions={"width": 0.086, "height": 0.086, "depth": 0.01},
        color="#F5F5F5",
        physics=PhysicsProperties(
            mass=0.1,
            material="塑料",
            hardness="硬"
        ),
        function=FunctionProperties(
            type="switch",
            circuit="AC-客厅空调",
            voltage=220
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            path_obstacle=False
        )
    ))
    
    # 插座 - 客厅电视区
    objects.append(BuildingObject(
        id="outlet-tv",
        name="电视插座",
        type="outlet",
        category="utility",
        position=[0, 0.3, -2.88],
        rotation=[0, 0, 0],
        dimensions={"width": 0.086, "height": 0.086, "depth": 0.01},
        color="#F5F5F5",
        physics=PhysicsProperties(
            mass=0.05,
            material="塑料",
            conductivity=0.9,
            hardness="硬"
        ),
        function=FunctionProperties(
            type="outlet",
            circuit="插座回路-客厅电视",
            voltage=220
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            path_obstacle=False
        )
    ))
    
    # 插座 - 厨房台面
    objects.append(BuildingObject(
        id="outlet-kitchen",
        name="厨房台面插座",
        type="outlet",
        category="utility",
        position=[6, 1.1, -2.88],
        rotation=[0, 0, 0],
        dimensions={"width": 0.086, "height": 0.086, "depth": 0.01},
        color="#F5F5F5",
        physics=PhysicsProperties(
            mass=0.05,
            material="塑料",
            conductivity=0.9,
            hardness="硬"
        ),
        function=FunctionProperties(
            type="outlet",
            circuit="插座回路-厨房",
            voltage=220
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            path_obstacle=False
        )
    ))
    
    # 燃气表
    objects.append(BuildingObject(
        id="gas-meter",
        name="燃气表",
        type="meter",
        category="utility",
        position=[7.88, 1.5, 0],
        rotation=[0, 90, 0],
        dimensions={"width": 0.3, "height": 0.4, "depth": 0.2},
        color="#FFA726",
        physics=PhysicsProperties(
            mass=5,
            material="金属",
            hardness="硬"
        ),
        function=FunctionProperties(
            type="gas_meter",
            gas_pipe="G-主管道"
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            path_obstacle=False
        )
    ))
    
    # 水龙头
    objects.append(BuildingObject(
        id="faucet-kitchen",
        name="厨房水龙头",
        type="faucet",
        category="utility",
        position=[7.3, 0.9, -2],
        rotation=[0, 0, 0],
        dimensions={"width": 0.15, "height": 0.35, "depth": 0.15},
        color="#C0C0C0",
        physics=PhysicsProperties(
            mass=2,
            material="不锈钢",
            hardness="硬"
        ),
        function=FunctionProperties(
            type="faucet",
            water_pipe="W-厨房冷水"
        ),
        robot_interaction=RobotInteraction(
            graspable=True,
            openable=True,
            path_obstacle=False,
            max_force=20
        )
    ))
    
    # 烟雾报警器
    objects.append(BuildingObject(
        id="smoke-detector",
        name="烟雾报警器",
        type="sensor",
        category="utility",
        position=[2, 2.95, 0],
        rotation=[0, 0, 0],
        dimensions={"width": 0.12, "height": 0.05, "depth": 0.12},
        color="#FFFFFF",
        physics=PhysicsProperties(
            mass=0.2,
            material="塑料",
            hardness="硬"
        ),
        function=FunctionProperties(
            type="smoke_sensor"
        ),
        robot_interaction=RobotInteraction(
            graspable=False,
            path_obstacle=False
        )
    ))
    
    return objects


# ============================================================
# 3D 可视化
# ============================================================

def create_3d_scene(building_objects: List[BuildingObject], selected_id: str = None, category_filter: str = "全部"):
    """创建 3D 建筑场景"""
    fig = go.Figure()
    
    # 类别颜色
    category_colors = {
        "structure": {"base": "#C4B5A0", "selected": "#FF5722"},
        "furniture": {"base": "#8D6E63", "selected": "#FF5722"},
        "appliance": {"base": "#78909C", "selected": "#FF5722"},
        "soft": {"base": "#A1887F", "selected": "#FF5722"},
        "utility": {"base": "#FFB74D", "selected": "#FF5722"}
    }
    
    # 类别透明度
    category_opacity = {
        "structure": 0.8,
        "furniture": 0.75,
        "appliance": 0.85,
        "soft": 0.6,
        "utility": 0.9
    }
    
    for obj in building_objects:
        # 过滤类别
        if category_filter != "全部" and obj.category != category_filter:
            continue
            
        # 获取尺寸
        w = obj.dimensions.get("width", 1)
        h = obj.dimensions.get("height", 1)
        d = obj.dimensions.get("depth", 1)
        
        # 位置
        x, y, z = obj.position
        
        # 判断是否选中
        is_selected = obj.id == selected_id
        colors = category_colors.get(obj.category, {"base": "#888888", "selected": "#4CAF50"})
        color = colors["selected"] if is_selected else obj.color
        opacity = 1.0 if is_selected else category_opacity.get(obj.category, 0.7)
        
        # 创建 3D 方块
        fig.add_trace(go.Mesh3d(
            x=[x-w/2, x-w/2, x+w/2, x+w/2, x-w/2, x-w/2, x+w/2, x+w/2],
            y=[y-h/2, y+h/2, y+h/2, y-h/2, y-h/2, y+h/2, y+h/2, y-h/2],
            z=[z-d/2, z-d/2, z-d/2, z-d/2, z+d/2, z+d/2, z+d/2, z+d/2],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 6, 2, 2, 0],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 3, 1, 1],
            k=[0, 7, 2, 3, 6, 7, 1, 4, 4, 5, 5, 3],
            color=color,
            opacity=opacity,
            name=obj.name,
            customdata=[obj.id] * 8,
            hovertemplate=f"<b>{obj.name}</b><br>类型: {obj.type}<br>类别: {obj.category}<br>点击查看详情<extra></extra>"
        ))
    
    # 设置场景
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (m)", range=[-5, 10], gridcolor="#E0E0E0"),
            yaxis=dict(title="Y 高度 (m)", range=[-0.5, 4], gridcolor="#E0E0E0"),
            zaxis=dict(title="Z (m)", range=[-4, 5], gridcolor="#E0E0E0"),
            aspectmode="data",
            camera=dict(
                eye=dict(x=2.5, y=2.0, z=2.5),
                center=dict(x=0.3, y=0, z=0)
            ),
            bgcolor="#FAFAFA"
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        showlegend=False
    )
    
    return fig


def create_floorplan(building_objects: List[BuildingObject], selected_id: str = None):
    """创建平面图"""
    fig = go.Figure()
    
    # 绘制地板轮廓
    fig.add_shape(
        type="rect",
        x0=-4, y0=-3, x1=8, y1=3,
        line=dict(color="#333333", width=3),
        fillcolor="#F5F5F5"
    )
    
    for obj in building_objects:
        if obj.category not in ["structure", "utility"]:
            continue
            
        x, y, z = obj.position
        w = obj.dimensions.get("width", 1)
        d = obj.dimensions.get("depth", 1)
        
        is_selected = obj.id == selected_id
        color = "#4CAF50" if is_selected else obj.color
        
        if obj.type in ["wall"]:
            # 墙体用粗线
            fig.add_shape(
                type="rect",
                x0=x - w/2, y0=z - d/2,
                x1=x + w/2, y1=z + d/2,
                line=dict(color=color, width=4),
                fillcolor=color,
                opacity=0.8
            )
        elif obj.type in ["door"]:
            # 门用圆弧表示
            fig.add_shape(
                type="rect",
                x0=x - w/2, y0=z - d/2,
                x1=x + w/2, y1=z + d/2,
                line=dict(color=color, width=2, dash="dot"),
                fillcolor=color,
                opacity=0.6
            )
        elif obj.type in ["switch", "outlet"]:
            # 开关插座用圆点
            fig.add_trace(go.Scatter(
                x=[x], y=[z],
                mode="markers+text",
                marker=dict(size=12, color=color),
                text=["⚡"],
                textposition="middle center",
                name=obj.name,
                customdata=[obj.id]
            ))
    
    fig.update_layout(
        xaxis=dict(title="X (m)", range=[-5, 10], scaleanchor="y"),
        yaxis=dict(title="Z (m)", range=[-4, 5]),
        height=450,
        margin=dict(l=50, r=50, t=20, b=50),
        showlegend=False,
        plot_bgcolor="#FAFAFA"
    )
    
    return fig


# ============================================================
# 信息面板
# ============================================================

def display_object_info(obj: BuildingObject):
    """显示建筑对象详细信息"""
    
    # 类别图标
    category_icons = {
        "structure": "🏗️",
        "furniture": "🪑",
        "appliance": "🔌",
        "soft": "🛋️",
        "utility": "⚡"
    }
    
    icon = category_icons.get(obj.category, "📦")
    
    st.markdown(f"### {icon} {obj.name}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**类型:** `{obj.type}`")
    with col2:
        st.markdown(f"**类别:** `{obj.category}`")
    with col3:
        st.markdown(f"**ID:** `{obj.id}`")
    
    # 几何属性
    st.markdown("---")
    st.markdown("#### 📐 几何属性")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("宽度", f"{obj.dimensions.get('width', 0):.2f} m")
    with col2:
        st.metric("高度", f"{obj.dimensions.get('height', 0):.2f} m")
    with col3:
        st.metric("深度", f"{obj.dimensions.get('depth', 0):.2f} m")
    
    # 位置
    st.markdown(f"**位置:** X={obj.position[0]:.2f}, Y={obj.position[1]:.2f}, Z={obj.position[2]:.2f}")
    
    # 物理属性
    if obj.physics:
        st.markdown("---")
        st.markdown("#### ⚛️ 物理属性")
        
        physics_data = []
        if obj.physics.mass is not None:
            physics_data.append(("质量", f"{obj.physics.mass} kg"))
        if obj.physics.material:
            physics_data.append(("材质", obj.physics.material))
        if obj.physics.stiffness is not None:
            physics_data.append(("刚度", f"{obj.physics.stiffness} MPa"))
        if obj.physics.friction is not None:
            physics_data.append(("摩擦系数", str(obj.physics.friction)))
        if obj.physics.hardness:
            physics_data.append(("硬度", obj.physics.hardness))
        if obj.physics.is_structural is not None:
            physics_data.append(("承重", "✅ 是" if obj.physics.is_structural else "❌ 否"))
        
        for label, value in physics_data:
            st.markdown(f"**{label}:** {value}")
    
    # 功能属性
    if obj.function:
        st.markdown("---")
        st.markdown("#### ⚡ 功能属性")
        st.markdown(f"**类型:** {obj.function.type}")
        if obj.function.circuit:
            st.markdown(f"**电路编号:** `{obj.function.circuit}`")
        if obj.function.voltage:
            st.markdown(f"**电压:** {obj.function.voltage}V")
        if obj.function.power:
            st.markdown(f"**功率:** {obj.function.power}W")
        if obj.function.water_pipe:
            st.markdown(f"**水管编号:** `{obj.function.water_pipe}`")
        if obj.function.gas_pipe:
            st.markdown(f"**燃气管编号:** `{obj.function.gas_pipe}`")
    
    # 机器人交互
    if obj.robot_interaction:
        st.markdown("---")
        st.markdown("#### 🤖 机器人交互能力")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**可抓取:** {'✅' if obj.robot_interaction.graspable else '❌'}")
        with col2:
            st.markdown(f"**可移动:** {'✅' if obj.robot_interaction.movable else '❌'}")
        with col3:
            st.markdown(f"**可开启:** {'✅' if obj.robot_interaction.openable else '❌'}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**路径障碍:** {'⚠️ 是' if obj.robot_interaction.path_obstacle else '✅ 否'}")
        with col2:
            st.markdown(f"**易碎品:** {'⚠️ 是' if obj.robot_interaction.fragile else '✅ 否'}")
        
        if obj.robot_interaction.max_force:
            st.markdown(f"**最大施力:** {obj.robot_interaction.max_force}N")
    
    # 物理常识说明
    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(76,175,80,0.1); border-left: 3px solid #4CAF50; padding: 12px; border-radius: 0 8px 8px 0;">
        <strong style="color: #4CAF50;">💡 物理常识注入</strong>
        <p style="color: #666; margin-top: 4px;">
        机器人已从施工图源头获得此物体的真实物理属性，无需统计学习拟合，可直接进行安全力控交互。
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 统计面板
# ============================================================

def display_statistics(building_objects: List[BuildingObject]):
    """显示建筑统计信息"""
    
    st.markdown("### 📊 建筑空间统计")
    
    # 按类别统计
    categories = {}
    for obj in building_objects:
        categories[obj.category] = categories.get(obj.category, 0) + 1
    
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    category_names = {
        "structure": "🏗️ 结构",
        "furniture": "🪑 家具",
        "appliance": "🔌 家电",
        "soft": "🛋️ 软装",
        "utility": "⚡ 设施"
    }
    
    for i, (cat, count) in enumerate(categories.items()):
        with cols[i]:
            st.metric(category_names.get(cat, cat), count)
    
    st.markdown("---")
    
    # 物理属性统计
    st.markdown("#### ⚛️ 物理属性覆盖")
    
    has_mass = sum(1 for obj in building_objects if obj.physics and obj.physics.mass)
    has_material = sum(1 for obj in building_objects if obj.physics and obj.physics.material)
    has_friction = sum(1 for obj in building_objects if obj.physics and obj.physics.friction is not None)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("质量数据", f"{has_mass}/{len(building_objects)}")
    with col2:
        st.metric("材质信息", f"{has_material}/{len(building_objects)}")
    with col3:
        st.metric("摩擦系数", f"{has_friction}/{len(building_objects)}")
    
    st.markdown("---")
    
    # 机器人交互统计
    st.markdown("#### 🤖 机器人交互潜力")
    
    graspable = sum(1 for obj in building_objects if obj.robot_interaction and obj.robot_interaction.graspable)
    movable = sum(1 for obj in building_objects if obj.robot_interaction and obj.robot_interaction.movable)
    openable = sum(1 for obj in building_objects if obj.robot_interaction and obj.robot_interaction.openable)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("可抓取", graspable)
    with col2:
        st.metric("可移动", movable)
    with col3:
        st.metric("可开启", openable)


# ============================================================
# 任务数据
# ============================================================

TASKS = [
    {
        "id": "task-door",
        "name": "🚪 开门任务",
        "description": "机器人理解门的物理属性，安全开门通过",
        "steps": [
            "定位门把手位置（高度约1.0m）",
            "识别门的质量：25kg",
            "计算所需力矩：F × 0.45m < 5Nm",
            "施力开门（最大力 50N）",
            "检测门的开合角度",
            "通过后关闭门"
        ],
        "physicsKnowledge": [
            "门板质量: 25kg",
            "铰链摩擦系数: 0.1",
            "把手高度: 1.0m",
            "门板厚度: 50mm",
            "开启方向: 向内",
            "最大力矩: 5Nm"
        ]
    },
    {
        "id": "task-light",
        "name": "💡 开灯任务",
        "description": "机器人理解电路布局，精准操作开关",
        "steps": [
            "定位开关位置：(-3.88, 1.3, 0)",
            "识别电路编号：L1-客厅主灯",
            "移动末端执行器到开关位置",
            "按压开关（压力 < 10N）",
            "通过视觉检测灯光状态",
            "确认任务完成"
        ],
        "physicsKnowledge": [
            "开关高度: 1.3m（符合国标）",
            "开关类型: 单开单控",
            "电路电压: 220V AC",
            "按压行程: 3mm",
            "触发力: 5-10N",
            "响应时间: < 100ms"
        ]
    },
    {
        "id": "task- dishes",
        "name": "🍽️ 洗碗任务",
        "description": "理解水路布局和餐具物理属性",
        "steps": [
            "定位厨房水槽位置",
            "识别水龙头类型：旋转式",
            "理解热水管编号：W-厨房热水",
            "抓取餐具（陶瓷碗质量约200g）",
            "控制清洗力度（< 20N）",
            "放置到沥水架"
        ],
        "physicsKnowledge": [
            "水槽深度: 200mm",
            "水龙头高度: 350mm",
            "水压: 0.3 MPa",
            "餐具质量: 100-500g",
            "陶瓷摩擦系数: 陶瓷-橡胶 = 0.4",
            "易碎品最大力: 30N"
        ]
    },
    {
        "id": "task-tv",
        "name": "📺 打开电视",
        "description": "理解家电控制方式，安全操作电子设备",
        "steps": [
            "识别电视位置：(0, 1.1, -2.5)",
            "定位遥控器或电源按钮",
            "理解电路编号：L2-客厅电视",
            "按压电源键（力 < 30N，防碎）",
            "检测屏幕亮起状态",
            "调节音量/频道"
        ],
        "physicsKnowledge": [
            "电视质量: 25kg",
            "屏幕材质: LCD玻璃",
            "电源功率: 150W",
            "易碎品最大力: 30N",
            "遥控器电池: 2xAAA"
        ]
    },
    {
        "id": "task-laundry",
        "name": "👕 洗衣服任务",
        "description": "理解水电路交叉系统，安全操作洗衣机",
        "steps": [
            "定位洗衣机位置：(7.5, 0.45, 2)",
            "识别电路：K-厨房插座 220V",
            "识别水管：W-洗衣机进水管",
            "打开机门（铰链门，力矩 < 3Nm）",
            "放入衣物（识别衣物类型）",
            "添加洗涤剂，选择程序，启动"
        ],
        "physicsKnowledge": [
            "洗衣机质量: 70kg",
            "最大功率: 500W",
            "进水管压力: 0.3 MPa",
            "门开启力矩: < 3Nm",
            "滚筒转速: 1200 RPM",
            "水位传感器精度: ±5mm"
        ]
    }
]


def display_task_info(task: Dict):
    """显示任务信息"""
    
    st.markdown(f"### {task['name']}")
    st.markdown(task['description'])
    
    st.markdown("---")
    st.markdown("#### 📋 执行步骤")
    for i, step in enumerate(task['steps'], 1):
        st.markdown(f"{i}. {step}")
    
    st.markdown("---")
    st.markdown("#### 🧠 物理常识（注入模型）")
    for knowledge in task['physicsKnowledge']:
        st.markdown(f"- {knowledge}")
    
    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(33,150,243,0.1); border-left: 3px solid #2196F3; padding: 12px; border-radius: 0 8px 8px 0;">
        <strong style="color: #2196F3;">🎯 核心差异</strong>
        <p style="color: #666; margin-top: 4px;">
        传统方法：机器人需要通过大量试错学习物体的物理属性<br>
        我们的方法：从施工图源头直接注入真实物理属性，零试错成本
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 主界面
# ============================================================

def main():
    # 页面配置
    st.set_page_config(
        page_title="建筑物理 AI 世界模型",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 自定义样式
    st.markdown("""
    <style>
    .stMetric {
        background: #F5F5F5;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 标题
    st.title("🏗️ 建筑物理 AI 世界模型")
    st.markdown("**让机器人理解建筑空间的物理常识** | Physical AI + 具身智能 | [完整场景 Demo]")
    
    # 加载数据
    building_objects = create_complete_building()
    
    # 侧边栏
    with st.sidebar:
        st.header("🎯 场景控制")
        
        # 类别过滤
        st.subheader("📦 显示类别")
        category_filter = st.selectbox(
            "过滤显示内容",
            ["全部", "structure", "furniture", "appliance", "soft", "utility"],
            format_func=lambda x: {
                "全部": "全部",
                "structure": "🏗️ 建筑结构",
                "furniture": "🪑 家具",
                "appliance": "🔌 家电",
                "soft": "🛋️ 软装",
                "utility": "⚡ 机电设施"
            }.get(x, x)
        )
        
        st.markdown("---")
        
        # 对象选择
        st.subheader("🔍 选择建筑对象")
        
        # 分类显示对象
        objects_by_category = {}
        for obj in building_objects:
            if obj.category not in objects_by_category:
                objects_by_category[obj.category] = []
            objects_by_category[obj.category].append(obj)
        
        category_names = {
            "structure": "🏗️ 建筑结构",
            "furniture": "🪑 家具",
            "appliance": "🔌 家电",
            "soft": "🛋️ 软装",
            "utility": "⚡ 机电设施"
        }
        
        object_names = ["请选择..."]
        for cat, objs in objects_by_category.items():
            object_names.append(f"--- {category_names.get(cat, cat)} ---")
            for obj in objs:
                object_names.append(obj.name)
        
        selected_name = st.selectbox("点击或选择", object_names)
        
        # 找到选中对象
        selected_obj = None
        if selected_name not in ["请选择...", "--- 建筑结构 ---", "--- 家具 ---", "--- 家电 ---", "--- 软装 ---", "--- 机电设施 ---"] and selected_name.startswith("---") == False:
            for obj in building_objects:
                if obj.name == selected_name:
                    selected_obj = obj
                    break
        
        st.markdown("---")
        
        # 任务选择
        st.subheader("🤖 机器人任务")
        task_names = ["请选择任务..."] + [t['name'] for t in TASKS]
        selected_task_name = st.selectbox("选择演示任务", task_names)
        
        selected_task = None
        if selected_task_name != "请选择任务...":
            for task in TASKS:
                if task['name'] == selected_task_name:
                    selected_task = task
                    break
    
    # 主内容区
    tab1, tab2, tab3 = st.tabs(["🏠 3D 场景", "📐 平面图", "📊 统计分析"])
    
    with tab1:
        col1, col2 = st.columns([2.5, 1])
        
        with col1:
            # 视图控制
            view_col1, view_col2, view_col3 = st.columns([2, 1, 1])
            with view_col1:
                st.markdown("**🖱️ 操作：拖拽旋转 | 滚轮缩放 | 双击重置**")
            with view_col2:
                st.checkbox("显示物理标签", value=False, key="show_physics_labels")
            with view_col3:
                st.checkbox("显示路径规划", value=False, key="show_paths")
            
            # 渲染 3D 场景
            selected_id = selected_obj.id if selected_obj else None
            fig = create_3d_scene(building_objects, selected_id, category_filter)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 信息面板
            if selected_obj:
                display_object_info(selected_obj)
            elif selected_task:
                display_task_info(selected_task)
            else:
                st.info("👈 从左侧选择建筑对象或任务查看详情")
                
                st.markdown("---")
                st.markdown("""
                ### 🎯 核心能力
                
                **1. 工程级几何精度**
                - 基于施工图毫米级精度
                - 无漂移、无穿模
                
                **2. 真实物理属性**
                - 质量刚度摩擦系数
                - 从源头定义非拟合
                
                **3. 建筑空间先验**
                - 理解墙门窗通道
                - 安全边界承重结构
                
                **4. 4D 世界模型**
                - 3D + 时间演化
                - 物理推演因果逻辑
                
                **5. 全链路统一**
                - 世界模型=仿真物理
                - 虚实零迁移损耗
                """)
    
    with tab2:
        st.markdown("### 📐 建筑平面图")
        selected_id = selected_obj.id if selected_obj else None
        fig = create_floorplan(building_objects, selected_id)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **图例说明：**
        - 🟫 深色：承重墙（不可拆改）
        - 🟨 浅色：隔墙（可调整）
        - ⚡ 圆点：开关/插座位置
        """)
    
    with tab3:
        display_statistics(building_objects)
    
    # 底部说明
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 20px;">
        <strong>建筑物理 AI 世界模型</strong> | 
        从工程源头定义世界 | 
        Physical AI 时代建筑场景基础设施 |
        <span style="color: #4CAF50;">✅ 真实物理属性 ✅ 工程级精度 ✅ 零迁移损耗</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
