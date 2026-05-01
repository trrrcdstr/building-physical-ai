"""
文本→4D动态场景生成管线

核心流程:
1. 文本理解 → 场景描述
2. 场景检索 → 高斯泼斯初始化
3. CAD约束 → 几何精修
4. 动作生成 → 4D时变高斯
"""

from .text_parser import TextToSceneParser
from .scene_retriever import SceneRetriever
from .gaussian_splatting import GaussianSplatting3D, GaussianSplatting4D
from .cad_constraint import CADGeometryConstraint
from .physics_sim import PhysicsSimulator
from .renderer import RealtimeRenderer

__all__ = [
    'TextToSceneParser',
    'SceneRetriever', 
    'GaussianSplatting3D',
    'GaussianSplatting4D',
    'CADGeometryConstraint',
    'PhysicsSimulator',
    'RealtimeRenderer',
]
