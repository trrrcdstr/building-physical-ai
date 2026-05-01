"""
neural/ — 神经网络模块
=======================
核心架构（来自 CNN vs Transformer 分析）：

  CNN 层（层次化规则）：
    像素 → 边缘 → 纹理 → 部件 → 物体 → 场景
    实现：ResNet/ViT 编码器，多层抽象

  Transformer 层（动态规则引擎）：
    自注意力 = 动态关系发现（键值查询）
    实现：RelationTransformer，替代硬编码规则

  物理 MLP（可解释先验）：
    几何 → 物理属性（ML 预测）
    保留物理可解释性

  JEPA Predictor（世界模型核心）：
    状态 s → 预测 s'
"""

from .vision_encoder import VisionEncoder, ImageEncoder
from .physics_mlp import PhysicsMLP, PropertyPredictor
from .relation_model import RelationTransformer, SceneEncoder
from .train import Trainer, build_training_data

__all__ = [
    "VisionEncoder",
    "ImageEncoder",
    "PhysicsMLP",
    "PropertyPredictor",
    "RelationTransformer",
    "SceneEncoder",
    "Trainer",
    "build_training_data",
]
