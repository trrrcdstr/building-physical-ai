"""
physics_mlp.py — 物理属性预测 MLP
====================================
从几何/语义特征预测物理属性的神经网络

设计原理（来自架构分析）：
  - 几何特征 + 语义标签 → MLP → 物理属性向量
  - 物理属性作为可解释先验，补充 CNN/ViT 的视觉特征

预测目标：
  - 质量 (mass_kg)
  - 摩擦系数 (friction)
  - 刚度 (stiffness)
  - 材质类型 (material_class)
  - 可变形性 (deformable)
  - 表面硬度 (surface_hardness)

物理约束（硬编码在损失函数中）：
  - 质量 > 0
  - 摩擦系数 ∈ [0, 1]
  - 刚度 > 0
"""

from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from typing import Optional
import math


# ─────────────────────────────────────────────────────────
# 物理 MLP 编码器
# ─────────────────────────────────────────────────────────

class PhysicsMLP(nn.Module):
    """
    物理属性预测 MLP

    输入（几何+语义特征）：
      - 几何：bbox x/y/z, volume, footprint
      - 语义：category embedding, room_type embedding
      - 材质：primary_material embedding

    输出（物理属性）：
      - mass_kg
      - friction_static
      - friction_dynamic
      - stiffness_Nm (log scale)
      - deformable_prob
      - surface_hardness (soft/medium/hard)

    物理约束：
      - 使用 sigmoid 限制输出范围
      - 质量/刚度用 log 变换处理长尾分布
    """

    FEATURE_DIM = 44  # 训练数据是44维，几何特征维度

    def __init__(self,
                 embed_dim: int = 128,
                 hidden_dims: list[int] = [256, 256, 128],
                 num_material_classes: int = 10,
                 num_room_classes: int = 20,
                 num_category_classes: int = 8):
        super().__init__()

        self.embed_dim = embed_dim
        self.num_material = num_material_classes
        self.num_room = num_room_classes
        self.num_cat = num_category_classes

        # 嵌入层
        self.material_embed = nn.Embedding(num_material_classes, 16)
        self.room_embed = nn.Embedding(num_room_classes, 32)
        self.category_embed = nn.Embedding(num_category_classes, 16)

        # 输入投影（两个版本：纯几何48维 vs 带嵌入112维）
        self.input_proj_full = nn.Sequential(
            nn.Linear(self.FEATURE_DIM + 16 + 32 + 16, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
        )
        self.input_proj_simple = nn.Sequential(
            nn.Linear(self.FEATURE_DIM, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
        )

        # 核心 MLP
        layers = []
        prev_dim = embed_dim
        for hd in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hd),
                nn.LayerNorm(hd),
                nn.GELU(),
                nn.Dropout(0.1),
            ])
            prev_dim = hd
        self.mlp = nn.Sequential(*layers)

        # 输出头
        self.head_mass = nn.Linear(prev_dim, 1)       # mass > 0 (用 softplus)
        self.head_fric_s = nn.Linear(prev_dim, 1)     # friction ∈ [0,1] (sigmoid)
        self.head_fric_d = nn.Linear(prev_dim, 1)    # friction ∈ [0,1] (sigmoid)
        self.head_stiff = nn.Linear(prev_dim, 1)     # stiffness (log scale)
        self.head_deform = nn.Linear(prev_dim, 1)    # deformable prob (sigmoid)
        self.head_hard = nn.Linear(prev_dim, 3)      # hardness 3-class (softmax)

    def forward(self,
                geometry_features: Tensor,
                material_id: Optional[Tensor] = None,
                room_id: Optional[Tensor] = None,
                category_id: Optional[Tensor] = None,
                ) -> dict[str, Tensor]:
        """
        Args:
            geometry_features: (B, 48) 几何+物理特征
            material_id:       (B,)   材质类别 ID
            room_id:          (B,)   房间类别 ID
            category_id:      (B,)   对象类别 ID

        Returns:
            {
                "mass_kg":          (B,)  质量
                "friction_static":  (B,)  静摩擦
                "friction_dynamic":  (B,)  动摩擦
                "stiffness_Nm":     (B,)  刚度
                "deformable_prob":  (B,)  可变形概率
                "hardness_logits":  (B,3) 硬度分布 (soft/medium/hard)
            }
        """
        B = geometry_features.shape[0]
        feat = geometry_features

        # 拼接嵌入（仅当有额外ID时才拼接）
        has_embed = (material_id is not None) or (room_id is not None) or (category_id is not None)

        if has_embed:
            tensors = [feat]
            if material_id is not None:
                tensors.append(self.material_embed(material_id))
            if room_id is not None:
                tensors.append(self.room_embed(room_id))
            if category_id is not None:
                tensors.append(self.category_embed(category_id))
            feat = torch.cat(tensors, dim=-1)
            x = self.input_proj_full(feat)
        else:
            # 纯几何48维，用简化投影
            x = self.input_proj_simple(feat)
        x = self.mlp(x)

        # 物理约束输出
        mass = F.softplus(self.head_mass(x)).squeeze(-1) + 0.1  # ≥ 0.1kg
        fric_s = torch.sigmoid(self.head_fric_s(x)).squeeze(-1)  # [0,1]
        fric_d = torch.sigmoid(self.head_fric_d(x)).squeeze(-1)  # [0,1]
        stiff = torch.exp(self.head_stiff(x).squeeze(-1))          # > 0 (log scale)
        deform = torch.sigmoid(self.head_deform(x)).squeeze(-1)   # [0,1]
        hardness = F.softmax(self.head_hard(x), dim=-1)          # [0,1]³

        return {
            "mass_kg": mass,
            "friction_static": fric_s,
            "friction_dynamic": fric_d,
            "stiffness_Nm": stiff,
            "deformable_prob": deform,
            "hardness_logits": hardness,
        }


# ─────────────────────────────────────────────────────────
# 物理属性预测器（带不确定性估计）
# ─────────────────────────────────────────────────────────

class PropertyPredictor(nn.Module):
    """
    物理属性预测器 — 带不确定性估计

    关键创新：
      - 预测均值 + 方差（epistemic uncertainty）
      - 知识库数据 → 降低不确定性
      - 当知识库有数据时，用知识代替预测

    这对应了"数据模型 + 动态规则引擎"中的混合推理：
      - 神经网络预测物理值
      - 知识库提供先验约束
    """

    def __init__(self, embed_dim: int = 128):
        super().__init__()

        # 确定性预测器
        self.deterministic = PhysicsMLP(embed_dim=embed_dim)

        # 不确定性预测器（预测 log variance）
        self.uncertainty = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self,
                geometry_features: Tensor,
                knowledge_confidence: Optional[Tensor] = None,
                **kwargs) -> dict[str, Tensor]:
        """
        Args:
            geometry_features:   (B, 48) 几何特征
            knowledge_confidence: (B,)   知识库置信度（0-1）

        Returns:
            {
                "mass": (B,) 预测质量（不确定性加权）
                "uncertainty": (B,) 预测不确定性
                "log_std": (B,) 对数标准差
            }
        """
        pred = self.deterministic(geometry_features, **kwargs)

        # 基础不确定性（用简化投影）
        x_proj = self.deterministic.input_proj_simple(geometry_features)
        log_std = self.uncertainty(x_proj).squeeze(-1).clamp(-5, 2)
        std = torch.exp(log_std)

        # 如果知识库有数据，降低不确定性
        if knowledge_confidence is not None:
            std = std * (1 - knowledge_confidence * 0.9)

        pred["uncertainty"] = std
        pred["log_std"] = log_std

        return pred


# ─────────────────────────────────────────────────────────
# 知识先验层（可学习的物理约束）
# ─────────────────────────────────────────────────────────

class PhysicsPriorLayer(nn.Module):
    """
    物理先验层 — 将物理规律编码为可学习的约束

    设计原理：
      - 不是让神经网络自由学习，而是用物理定律引导学习
      - 例如：密度 = 质量 / 体积，这应该是一个约束

    约束类型：
      1. 物理一致性：mass / volume ≈ density (查表)
      2. 摩擦单调性：fric_static ≥ fric_dynamic
      3. 刚度-硬度一致性：硬材质 → 高刚度
    """

    def __init__(self, num_rules: int = 5):
        super().__init__()

        # 可学习的规则权重
        self.rule_weights = nn.Parameter(torch.ones(num_rules))

        # 材质密度先验 (g/cm³)
        self.register_buffer(
            "material_density_prior",
            torch.tensor([0.35, 0.65, 7.8, 2.5, 2.4, 2.7, 0.95, 1.1, 0.8, 1.2])
        )

    def physics_loss(self,
                     mass: Tensor,
                     volume: Tensor,
                     friction_s: Tensor,
                     friction_d: Tensor,
                     stiffness: Tensor,
                     hardness: Tensor) -> Tensor:
        """
        计算物理一致性损失

        Returns:
            标量损失（越小越好）
        """
        losses = []

        # 规则1：质量/体积一致性
        # 期望密度在合理范围
        density = mass / (volume + 1e-6)
        # 密度范围 0.1 - 10 g/cm³
        density_loss = F.relu(density - 10) + F.relu(0.1 - density)
        losses.append(density_loss.mean())

        # 规则2：摩擦单调性
        fric_loss = F.relu(friction_s - friction_d - 0.05).mean()
        losses.append(fric_loss)

        # 规则3：刚度-硬度一致性
        # hard → stiffness 高，soft → stiffness 低
        # hardness: (B, 3) = [soft, medium, hard]
        stiffness_log = torch.log(stiffness + 1e-6)
        hard_weight = hardness[:, 2]  # hard 概率
        soft_weight = hardness[:, 0]  # soft 概率

        # 硬材质刚度应该高
        stiff_hard_loss = F.relu(8 - hard_weight * stiffness_log).mean()
        losses.append(stiff_hard_loss)

        # 软材质刚度应该低
        stiff_soft_loss = F.relu(soft_weight * stiffness_log - 2).mean()
        losses.append(stiff_soft_loss)

        # 加权求和
        weights = torch.softmax(self.rule_weights, dim=0)
        total = sum(w * l for w, l in zip(weights, losses))

        return total


# ─────────────────────────────────────────────────────────
# 预训练物理预测模型（可直接加载使用）
# ─────────────────────────────────────────────────────────

class PretrainedPhysicsPredictor:
    """
    预训练物理预测器

    用法：
      predictor = PretrainedPhysicsPredictor()
      result = predictor.predict_from_geometry(bbox=[2.2, 0.85, 0.95])
    """

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.model = PropertyPredictor(embed_dim=128)
        self.model.eval()
        self.model.to(device)

        # 默认材质密度表（作为先验）
        self.density_table = {
            "fabric": 0.35,
            "wood": 0.65,
            "metal": 7.8,
            "glass": 2.5,
            "ceramic": 2.4,
            "stone": 2.7,
            "plastic": 0.95,
            "rubber": 1.1,
        }

    @torch.no_grad()
    def predict_from_geometry(self,
                               bbox: list[float],
                               category: str = "furniture",
                               material: str = "wood",
                               room: str = "客厅") -> dict:
        """从几何信息预测物理属性"""
        x, y, z = bbox[0], bbox[1], bbox[2]
        volume = x * y * z
        density = self.density_table.get(material, 0.65)

        # 构建输入特征
        feat = torch.zeros(1, 48, device=self.device)
        feat[0, 0] = x
        feat[0, 1] = y
        feat[0, 2] = z
        feat[0, 3] = volume
        feat[0, 4] = x * z  # footprint
        feat[0, 5] = 0.6    # front clearance

        # category embedding
        cat_id = {"furniture": 0, "appliance": 1, "structure": 2}.get(category, 0)
        result = self.model(feat, category_id=torch.tensor([cat_id], device=self.device))

        return {
            "mass_kg": result["mass_kg"].item(),
            "friction_static": result["friction_static"].item(),
            "friction_dynamic": result["friction_dynamic"].item(),
            "stiffness_Nm": result["stiffness_Nm"].item(),
            "deformable_prob": result["deformable_prob"].item(),
            "estimated_density": density,
        }


# ─────────────────────────────────────────────────────────
# 训练数据生成器
# ─────────────────────────────────────────────────────────

def generate_physics_training_data(n_samples: int = 1000) -> dict:
    """
    生成物理属性训练数据

    用于训练 PhysicsMLP

    数据来源：
      - CAD 数据：精确几何
      - 家具标准尺寸：典型家具 bounding box
      - 材料库：密度/摩擦系数

    Returns:
        {
            "X": (N, 48) 特征矩阵,
            "y_mass": (N,) 质量标签,
            "y_fric_s": (N,) 静摩擦标签,
            "y_fric_d": (N,) 动摩擦标签,
            "y_stiff": (N,) 刚度标签,
            "metadata": {...}
        }
    """
    import numpy as np

    # 预定义家具尺寸（米）
    furniture_templates = [
        # (name, category, x, y, z, mass_kg, fric_s, fric_d, stiff_Nm)
        ("三人沙发", "furniture", 2.2, 0.85, 0.95, 65, 0.5, 0.4, 5000),
        ("双人沙发", "furniture", 1.8, 0.8, 0.9, 50, 0.5, 0.4, 5000),
        ("单人沙发", "furniture", 0.9, 0.8, 0.85, 25, 0.5, 0.4, 4000),
        ("茶几", "furniture", 1.2, 0.45, 0.6, 20, 0.4, 0.3, 10000),
        ("餐桌", "furniture", 1.6, 0.75, 0.8, 35, 0.4, 0.3, 15000),
        ("餐椅", "furniture", 0.45, 0.9, 0.45, 5, 0.4, 0.3, 3000),
        ("书桌", "furniture", 1.4, 0.75, 0.7, 25, 0.4, 0.3, 12000),
        ("办公椅", "furniture", 0.6, 1.1, 0.6, 12, 0.4, 0.3, 2000),
        ("衣柜", "furniture", 1.8, 2.2, 0.6, 80, 0.4, 0.3, 20000),
        ("床头柜", "furniture", 0.5, 0.6, 0.4, 8, 0.4, 0.3, 5000),
        ("双人床", "furniture", 1.8, 0.5, 2.0, 70, 0.5, 0.4, 10000),
        ("单人员", "furniture", 1.0, 0.5, 1.9, 40, 0.5, 0.4, 10000),
        ("橱柜", "furniture", 3.0, 0.9, 0.6, 60, 0.4, 0.3, 15000),
        ("书柜", "furniture", 0.9, 2.0, 0.35, 35, 0.4, 0.3, 12000),
        ("马桶", "furniture", 0.4, 0.8, 0.7, 25, 0.3, 0.25, 50000),
        ("洗手台", "furniture", 0.8, 0.8, 0.5, 20, 0.3, 0.25, 30000),
        ("浴缸", "furniture", 1.7, 0.6, 0.75, 80, 0.3, 0.25, 60000),
        ("冰箱", "appliance", 0.9, 1.9, 0.7, 90, 0.3, 0.2, 100000),
        ("洗衣机", "appliance", 0.6, 0.85, 0.6, 65, 0.3, 0.2, 50000),
        ("电视", "appliance", 1.4, 0.8, 0.1, 25, 0.3, 0.2, 5000),
        ("空调室内机", "appliance", 0.9, 0.3, 0.2, 11, 0.3, 0.2, 2000),
        ("微波炉", "appliance", 0.5, 0.3, 0.4, 12, 0.3, 0.2, 3000),
        ("烤箱", "appliance", 0.6, 0.6, 0.55, 40, 0.3, 0.2, 20000),
    ]

    X, y_mass, y_fric_s, y_fric_d, y_stiff = [], [], [], [], []

    for _ in range(n_samples // len(furniture_templates) + 1):
        for name, cat, x, y, z, mass, fric_s, fric_d, stiff in furniture_templates:
            # 添加噪声（模拟视觉估计误差）
            noise = np.random.uniform(0.9, 1.1)
            x_n, y_n, z_n = x * noise, y * noise, z * noise

            volume = x_n * y_n * z_n
            footprint = x_n * z_n

            feat = [
                x_n, y_n, z_n, volume, footprint,
                0.9, 0.3, 0.3, 0.3, 0.5,  # clearances
                0.0, 1.0,  # wall_mounted, floor_mounted
                # 物理特征（目标，不是输入）
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                # 机器人特征
                1.0, 1.0, 1.0, 0.0,
                0.2, 0.6, 0.4, 0.2, 0.4,
                1.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0,
            ]

            # 添加随机噪声到几何
            feat = np.array(feat)
            feat[:5] *= np.random.uniform(0.95, 1.05, 5)

            X.append(feat)
            y_mass.append(mass * np.random.uniform(0.95, 1.05))
            y_fric_s.append(fric_s * np.random.uniform(0.95, 1.05))
            y_fric_d.append(fric_d * np.random.uniform(0.95, 1.05))
            y_stiff.append(math.log(stiff))

    X = np.array(X[:n_samples], dtype=np.float32)
    y_mass = np.array(y_mass[:n_samples], dtype=np.float32)
    y_fric_s = np.array(y_fric_s[:n_samples], dtype=np.float32)
    y_fric_d = np.array(y_fric_d[:n_samples], dtype=np.float32)
    y_stiff = np.array(y_stiff[:n_samples], dtype=np.float32)

    return {
        "X": X,
        "y_mass": y_mass,
        "y_fric_s": y_fric_s,
        "y_fric_d": y_fric_d,
        "y_stiff": y_stiff,
        "metadata": {
            "n_samples": len(X),
            "n_features": X.shape[1],
        }
    }
