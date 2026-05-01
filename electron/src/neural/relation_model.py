"""
relation_model.py — 关系建模 Transformer
==========================================
Transformer 关系建模：

  输入：对象特征 + 场景图边
  处理：自注意力 → 关系更新 → 场景状态

  核心思想（来自键值查询分析）：
    - Q（Query）：我想找什么关系
    - K（Key）：每个对象提供了什么信息
    - V（Value）：关系的内容是什么

  自注意力的本质 = 让对象自己发现彼此的关系（替代硬编码规则）
"""

from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from typing import Optional
import math


# ─────────────────────────────────────────────────────────
# 关系 Transformer
# ─────────────────────────────────────────────────────────

class RelationAttention(nn.Module):
    """
    关系注意力 — 替换硬编码空间规则

    对比：
      硬编码规则：
        if distance < 1m → next_to
        if height_diff > 0.5m → above

      关系注意力：
        Q = 对象查询向量（我想找它的邻居）
        K = 对象键向量（它能提供什么关系信息）
        V = 对象值向量（关系的内容）

        注意力权重 = softmax(QK^T / √d) × 距离衰减
        这让关系从数据中学习，而非手工定义
    """

    def __init__(self, embed_dim: int, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % num_heads == 0

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5

        # QKV 投影
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

        # 距离编码（注入几何先验）
        self.distance_encode = nn.Sequential(
            nn.Linear(1, embed_dim // num_heads),
            nn.ReLU(),
            nn.Linear(embed_dim // num_heads, embed_dim // num_heads),
        )

        self.attn_drop = nn.Dropout(dropout)
        self.proj_drop = nn.Dropout(dropout)

    def forward(self,
               node_features: Tensor,          # (B, N, D)
               edge_distance: Optional[Tensor] = None,  # (B, N, N) or None
               edge_mask: Optional[Tensor] = None  # (B, N, N) bool mask
               ) -> tuple[Tensor, Tensor]:
        """
        Args:
            node_features:  (B, N, D) 对象特征
            edge_distance:  (B, N, N) 对象间距离（用于注意力衰减）
            edge_mask:      (B, N, N) 布尔掩码（1=有边，0=无边）

        Returns:
            updated_features: (B, N, D) 更新后的对象特征
            attention_weights: (B, N, N) 注意力权重
        """
        B, N, D = node_features.shape

        # QKV
        Q = self.q_proj(node_features)  # (B, N, D)
        K = self.k_proj(node_features)
        V = self.v_proj(node_features)

        # 多头 reshape
        Q = Q.view(B, N, self.num_heads, self.head_dim).transpose(1, 2)
        K = K.view(B, N, self.num_heads, self.head_dim).transpose(1, 2)
        V = V.view(B, N, self.num_heads, self.head_dim).transpose(1, 2)

        # 注意力分数
        attn = (Q @ K.transpose(-2, -1)) * self.scale  # (B, heads, N, N)

        # 注入距离先验（距离越远，注意力越弱）
        if edge_distance is not None:
            # edge_distance: (B, N, N) → (B, 1, N, N)
            dist = edge_distance.unsqueeze(1).clamp(0.1, 10.0)
            dist_encoding = self.distance_encode(1.0 / dist)  # 距离衰减编码
            dist_encoding = dist_encoding.unsqueeze(1).expand(-1, self.num_heads, -1, -1)
            attn = attn + dist_encoding

        # 掩码（无边的地方注意力设为 -inf）
        if edge_mask is not None:
            attn = attn.masked_fill(~edge_mask.unsqueeze(1), float("-inf"))

        attn = F.softmax(attn, dim=-1)
        attn = self.attn_drop(attn)

        # 输出
        out = attn @ V  # (B, heads, N, head_dim)
        out = out.transpose(1, 2).reshape(B, N, D)
        out = self.out_proj(out)
        out = self.proj_drop(out)

        # 平均多头注意力权重
        attn_weights = attn.mean(dim=1)  # (B, N, N)

        return out, attn_weights


class TransformerBlock(nn.Module):
    """关系 Transformer 块"""
    def __init__(self, embed_dim: int, num_heads: int = 8,
                 mlp_ratio: float = 4.0, dropout: float = 0.1):
        super().__init__()

        self.norm1 = nn.LayerNorm(embed_dim)
        self.relation_attn = RelationAttention(embed_dim, num_heads, dropout)
        self.norm2 = nn.LayerNorm(embed_dim)

        mlp_hidden = int(embed_dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, mlp_hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden, embed_dim),
            nn.Dropout(dropout),
        )

    def forward(self,
                x: Tensor,
                edge_distance: Optional[Tensor] = None,
                edge_mask: Optional[Tensor] = None) -> tuple[Tensor, Tensor]:
        # 关系注意力 + 残差
        attn_out, attn_weights = self.relation_attn(self.norm1(x), edge_distance, edge_mask)
        x = x + attn_out

        # MLP + 残差
        x = x + self.mlp(self.norm2(x))

        return x, attn_weights


class RelationTransformer(nn.Module):
    """
    关系建模 Transformer

    核心功能：
      - 输入：一组对象特征 + 它们之间的几何关系
      - 处理：多层关系注意力 + 前馈网络
      - 输出：每个对象的关系感知特征

    对应"规则引擎 → 神经网络"的演进：
      - 旧：硬编码规则（distance < 1m → next_to）
      - 新：让注意力从数据中学习关系模式
    """

    def __init__(self,
                 embed_dim: int = 256,
                 num_layers: int = 4,
                 num_heads: int = 8,
                 mlp_ratio: float = 4.0,
                 dropout: float = 0.1,
                 use_edge_features: bool = True):
        super().__init__()

        self.embed_dim = embed_dim
        self.num_layers = num_layers
        self.use_edge_features = use_edge_features

        # 输入归一化（解决特征尺度不一致问题）
        self.input_norm = nn.LayerNorm(embed_dim)

        # 输入投影
        self.input_proj = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
        )

        # 多层关系 Transformer
        self.blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, mlp_ratio, dropout)
            for _ in range(num_layers)
        ])

        self.norm = nn.LayerNorm(embed_dim)

        # 关系预测头（预测边的类型和方向）
        self.relation_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.ReLU(),
            nn.Linear(embed_dim // 2, 8),  # 8 种关系类型
        )

        # 注意力收集（用于可视化）
        self.all_attention_weights: list[Tensor] = []

    def forward(self,
                node_features: Tensor,     # (B, N, D)
                edge_distance: Optional[Tensor] = None,  # (B, N, N)
                edge_mask: Optional[Tensor] = None,      # (B, N, N)
                return_attention: bool = True
                ) -> dict[str, Tensor]:
        """
        Args:
            node_features:  (B, N, D) 对象特征
            edge_distance:  (B, N, N) 对象间距离
            edge_mask:      (B, N, N) 有效边掩码

        Returns:
            {
                "updated_features": (B, N, D) 关系感知特征
                "relation_logits":  (B, N, N, 8) 关系类型预测
                "attention_weights": list of (B, N, N)
            }
        """
        self.all_attention_weights = []

        # 归一化 + 投影
        x = self.input_norm(node_features)
        x = self.input_proj(x)

        for block in self.blocks:
            x, attn_w = block(x, edge_distance, edge_mask)
            if return_attention:
                self.all_attention_weights.append(attn_w)

        x = self.norm(x)

        # 预测关系类型（每对对象之间）
        # (B, N, D) → (B, N, N, 8)
        relation_logits = self._predict_relations(x)

        return {
            "updated_features": x,
            "relation_logits": relation_logits,
            "attention_weights": self.all_attention_weights,
        }

    def _predict_relations(self, features: Tensor) -> Tensor:
        """从更新后的特征预测关系类型"""
        B, N, D = features.shape

        # 节点 → 边：组合两个节点的特征
        # 方法：对每个节点对，取 [h_i || h_j || h_i - h_j || h_i * h_j]
        h_i = features.unsqueeze(2).expand(-1, -1, N, -1)      # (B, N, N, D)
        h_j = features.unsqueeze(1).expand(-1, N, -1, -1)      # (B, N, N, D)
        h_diff = h_i - h_j                                     # (B, N, N, D)
        h_prod = h_i * h_j                                     # (B, N, N, D)

        h_pair = torch.cat([h_i, h_j, h_diff, h_prod], dim=-1)  # (B, N, N, 4D)
        logits = self.relation_head(h_pair)                     # (B, N, N, 8)

        return logits


# ─────────────────────────────────────────────────────────
# 场景编码器：整合所有特征
# ─────────────────────────────────────────────────────────

class SceneEncoder(nn.Module):
    """
    场景编码器 — 整合视觉 + 物理 + 关系特征

    架构：
      视觉特征 (ViT/CNN) ──┐
                           ├──→ 融合 → Transformer → 场景状态表示
      物理特征 (MLP)     ──┤
                           │
      几何特征 (手工)     ──┘

    输出：
      - scene_state: (B, embed_dim) 场景级状态向量
      - object_states: (B, N, embed_dim) 对象级状态向量
      - relation_matrix: (B, N, N, num_relations) 关系矩阵
    """

    def __init__(self,
                 embed_dim: int = 256,
                 num_objects: int = 50,
                 num_relation_types: int = 8):
        super().__init__()

        self.embed_dim = embed_dim
        self.num_relation_types = num_relation_types

        # 特征融合层
        self.feature_fusion = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
            nn.Dropout(0.1),
        )

        # 关系 Transformer
        self.relation_transformer = RelationTransformer(
            embed_dim=embed_dim,
            num_layers=3,
            num_heads=8,
            use_edge_features=True,
        )

        # 场景状态池化
        self.scene_pool = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, embed_dim),
        )

        # 关系类型嵌入
        self.relation_embed = nn.Embedding(num_relation_types, embed_dim)

    def forward(self,
                visual_features: Tensor,   # (B, N, D_visual)
                physics_features: Tensor,   # (B, N, D_physics)
                geometry_features: Tensor,  # (B, N, D_geo)
                edge_distance: Optional[Tensor] = None,
                edge_mask: Optional[Tensor] = None,
                ) -> dict[str, Tensor]:
        """
        Args:
            visual_features:    (B, N, D_visual) 视觉特征
            physics_features:   (B, N, D_physics) 物理特征
            geometry_features:  (B, N, D_geo)   几何特征
            edge_distance:      (B, N, N)       对象间距离
            edge_mask:          (B, N, N)       有效边掩码

        Returns:
            {
                "scene_state":     (B, embed_dim) 场景状态
                "object_states":   (B, N, embed_dim) 对象状态
                "relation_matrix": (B, N, N, num_relations) 关系矩阵
            }
        """
        B, N = visual_features.shape[:2]

        # 投影到统一维度
        v = visual_features[:, :, :self.embed_dim]
        p = physics_features[:, :, :self.embed_dim]
        g = geometry_features[:, :, :self.embed_dim]

        # 融合
        fused = torch.cat([v, p, g], dim=-1)  # (B, N, 3*embed_dim)
        node_features = self.feature_fusion(fused)  # (B, N, embed_dim)

        # 关系建模
        relation_out = self.relation_transformer(
            node_features,
            edge_distance=edge_distance,
            edge_mask=edge_mask,
        )

        # 场景状态（注意力加权池化）
        attn_weights = relation_out["attention_weights"]
        if attn_weights:
            # 用最后一层注意力权重做加权平均
            last_attn = attn_weights[-1]  # (B, N, N)
            scene_weights = last_attn.sum(dim=-1)  # (B, N)
            scene_weights = F.softmax(scene_weights, dim=-1)
            scene_state = (node_features * scene_weights.unsqueeze(-1)).sum(dim=1)  # (B, D)
        else:
            scene_state = node_features.mean(dim=1)

        scene_state = self.scene_pool(scene_state)

        # 关系矩阵
        rel_logits = relation_out["relation_logits"]  # (B, N, N, 8)
        rel_probs = torch.softmax(rel_logits, dim=-1)  # (B, N, N, 8)

        return {
            "scene_state": scene_state,
            "object_states": relation_out["updated_features"],
            "relation_matrix": rel_probs,
            "attention_weights": attn_weights,
        }


# ─────────────────────────────────────────────────────────
# 预训练场景编码器（可直接使用）
# ─────────────────────────────────────────────────────────

def build_scene_graph_from_features(
    object_features: list[list[float]],
    distances: list[list[float]],
    relation_types: Optional[list[str]] = None,
) -> dict:
    """
    从手工特征构建场景图（用于没有神经网络时）

    这是一个快速原型工具：
      - 输入：手工提取的特征向量
      - 处理：简单相似度计算 + 规则
      - 输出：关系矩阵

    用于测试 pipeline，或在没有 GPU 时使用
    """
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    features = np.array(object_features)
    dists = np.array(distances)

    # 相似度 = 1 - 归一化距离
    max_d = dists.max() + 1e-6
    sims = 1 - dists / max_d

    # 关系阈值
    relation_matrix = np.zeros((len(features), len(features), 8))

    for i in range(len(features)):
        for j in range(len(features)):
            if i == j:
                continue

            s = sims[i, j]
            d = dists[i, j]

            if d < 1.0:
                relation_matrix[i, j, 0] = s  # next_to
            elif d < 3.0:
                relation_matrix[i, j, 1] = s  # near
            else:
                relation_matrix[i, j, 2] = s  # far

    return {
        "relation_matrix": relation_matrix.tolist(),
        "similarity": sims.tolist(),
        "distances": dists.tolist(),
    }
