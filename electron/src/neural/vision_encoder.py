"""
vision_encoder.py — 视觉编码器
================================
CNN + ViT 双编码器架构：

  输入图像（VR效果图/CAD截图）
    │
    ├─→ ResNet（CNN层次化特征提取）
    │     像素 → 边缘 → 纹理 → 部件 → 物体
    │
    └─→ ViT（Transformer全局关系建模）
          Patch Embedding → Self-Attention → 全局表示

输出：对象级视觉特征向量 + 场景级全局特征向量
"""

from __future__ import annotations
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from typing import Optional


# ─────────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────────

def mlp(input_dim: int,
        hidden_dims: list[int],
        output_dim: int,
        activation: type[nn.Module] = nn.ReLU,
        dropout: float = 0.0) -> nn.Module:
    """
    构建 MLP 多层感知机

    用于物理属性预测、特征投影等
    """
    layers = []
    prev_dim = input_dim

    for hidden_dim in hidden_dims:
        layers.append(nn.Linear(prev_dim, hidden_dim))
        if activation:
            layers.append(activation())
        if dropout > 0:
            layers.append(nn.Dropout(dropout))
        prev_dim = hidden_dim

    layers.append(nn.Linear(prev_dim, output_dim))
    return nn.Sequential(*layers)


class PositionalEncoding2D(nn.Module):
    """
    2D 位置编码 — 给空间特征图注入位置信息

    类比 Transformer 的 positional encoding，但针对 2D 空间：
    - 将 (H, W) 坐标编码为向量
    - 融合 sin/cos 位置编码
    """
    def __init__(self, d_model: int, height: int = 32, width: int = 32):
        super().__init__()
        pe = torch.zeros(d_model, height, width)

        # (d_model,) 位置信息
        d_model_h = d_model // 2
        d_model_w = d_model - d_model_h

        # H 维度
        position_h = torch.arange(0, height).unsqueeze(1)
        div_term_h = torch.exp(
            torch.arange(0, d_model_h, 2) * (-math.log(10000.0) / d_model_h))
        pe[0::4, :, :] = torch.sin(position_h * div_term_h).unsqueeze(2).expand(-1, -1, width)
        pe[1::4, :, :] = torch.cos(position_h * div_term_h).unsqueeze(2).expand(-1, -1, width)

        # W 维度
        position_w = torch.arange(0, width).unsqueeze(0)
        div_term_w = torch.exp(
            torch.arange(0, d_model_w, 2) * (-math.log(10000.0) / d_model_w))
        pe[d_model_h::2, :, :] = torch.sin(position_w * div_term_w).unsqueeze(1).expand(-1, height, -1)
        pe[d_model_h+1::2, :, :] = torch.cos(position_w * div_term_w).unsqueeze(1).expand(-1, height, -1)

        self.register_buffer("pe", pe)

    def forward(self, x: Tensor) -> Tensor:
        # x: (B, d_model, H, W)
        return x + self.pe.unsqueeze(0)


# ─────────────────────────────────────────────────────────
# ResNet CNN 编码器 — 层次化特征提取
# ─────────────────────────────────────────────────────────

class CNNEncoder(nn.Module):
    """
    CNN 编码器 — 实现像素→边缘→纹理→部件→物体的层次化抽象

    结构（参考 ResNet18 架构）：
      Conv1 → ResBlock1×2 → ResBlock2×2 → ResBlock3×2 → ResBlock4×2
        ↓           ↓           ↓            ↓           ↓
      (64ch)     (64ch)      (128ch)       (256ch)     (512ch)
       边缘        纹理        部件          物体         场景

    每个阶段提取不同层次的特征，对应 CNN 的多层抽象规则
    """

    def __init__(self,
                 input_channels: int = 3,
                 embed_dim: int = 256,
                 pretrained: bool = False,
                 freeze_bn: bool = True):
        super().__init__()

        # 用 torchvision 的 ResNet 作为 backbone（如果可用）
        try:
            import torchvision.models as models
            self.backbone = models.resnet18(pretrained=pretrained)
            self.backbone.fc = nn.Identity()
            feature_dim = 512
        except ImportError:
            # 手写轻量版 ResNet（无 torchvision 时）
            self.backbone = None
            feature_dim = 512
            self._build_from_scratch(input_channels)

        self.embed_dim = embed_dim
        self.projection = nn.Linear(feature_dim, embed_dim)

        # 冻结 BatchNorm
        if freeze_bn:
            self._freeze_bn()

    def _freeze_bn(self):
        """冻结 BatchNorm 层"""
        for m in self.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eval()
                for p in m.parameters():
                    p.requires_grad = False

    def _build_from_scratch(self, in_channels: int):
        """在没有 torchvision 时构建轻量 ResNet"""
        self.conv1 = nn.Conv2d(in_channels, 64, 7, 2, 3)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(3, 2, 1)

        # 简化的 ResNet blocks
        self.layer1 = self._make_layer(64, 64, 2)
        self.layer2 = self._make_layer(64, 128, 2)
        self.layer3 = self._make_layer(128, 256, 2)
        self.layer4 = self._make_layer(256, 512, 2)

        self.backbone = None

    def _make_layer(self, in_ch: int, out_ch: int, blocks: int) -> nn.Sequential:
        layers = [ResBlock(in_ch, out_ch)]
        for _ in range(1, blocks):
            layers.append(ResBlock(out_ch, out_ch))
        return nn.Sequential(*layers)

    def forward(self, x: Tensor) -> dict[str, Tensor]:
        """
        前向传播

        Args:
            x: (B, 3, H, W) 输入图像

        Returns:
            {
                "features":    (B, embed_dim) 全局特征向量
                "layer1-4":   各层特征图 (B, C, H', W')
                "spatial":    (B, embed_dim, H', W') 空间特征图
            }
        """
        if self.backbone is not None:
            x = self.backbone.conv1(x)
            x = self.backbone.bn1(x)
            x = self.backbone.relu(x)
            x = self.backbone.maxpool(x)
            x = self.backbone.layer1(x)
            layer2 = self.backbone.layer2(x)
            layer3 = self.backbone.layer3(layer2)
            layer4 = self.backbone.layer4(layer3)

            # 全局平均池化 → 全局特征
            global_feat = F.adaptive_avg_pool2d(layer4, 1).flatten(1)
            global_feat = self.projection(global_feat)

            return {
                "features": global_feat,
                "layer2": layer2,    # 部件级别特征
                "layer3": layer3,    # 物体级别特征
                "layer4": layer4,    # 场景级别特征
            }
        else:
            # 手写版本
            x = self.conv1(x)
            x = self.bn1(x)
            x = self.relu(x)
            x = self.maxpool(x)

            l1 = self.layer1(x)
            l2 = self.layer2(l1)
            l3 = self.layer3(l2)
            l4 = self.layer4(l3)

            global_feat = F.adaptive_avg_pool2d(l4, 1).flatten(1)
            global_feat = self.projection(global_feat)

            return {
                "features": global_feat,
                "layer1": l1, "layer2": l2, "layer3": l3, "layer4": l4,
            }


class ResBlock(nn.Module):
    """残差块"""
    def __init__(self, in_ch: int, out_ch: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_ch, out_ch, 3, stride, 1)
        self.bn1 = nn.BatchNorm2d(out_ch)
        self.conv2 = nn.Conv2d(out_ch, out_ch, 3, 1, 1)
        self.bn2 = nn.BatchNorm2d(out_ch)

        self.shortcut = nn.Identity() if in_ch == out_ch and stride == 1 \
            else nn.Sequential(
                nn.Conv2d(in_ch, out_ch, 1, stride),
                nn.BatchNorm2d(out_ch)
            )

    def forward(self, x: Tensor) -> Tensor:
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return F.relu(out + self.shortcut(x))


# ─────────────────────────────────────────────────────────
# ViT 编码器 — Transformer 全局关系建模
# ─────────────────────────────────────────────────────────

class PatchEmbedding(nn.Module):
    """图像 → Patch 嵌入（ViT 的第一步）"""
    def __init__(self, img_size: int = 224, patch_size: int = 16,
                 in_channels: int = 3, embed_dim: int = 256):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2

        # 将图像分割为 patch 并线性投影
        self.proj = nn.Conv2d(in_channels, embed_dim,
                               kernel_size=patch_size, stride=patch_size)

        # 可学习的 [CLS] token（代表整个图像）
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))

        # 位置编码
        self.pos_embed = nn.Parameter(
            torch.zeros(1, self.num_patches + 1, embed_dim))

        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)

    def forward(self, x: Tensor) -> tuple[Tensor, dict]:
        # x: (B, 3, H, W) → (B, num_patches, embed_dim)
        x = self.proj(x)  # (B, embed_dim, H/P, W/P)
        B, E, H, W = x.shape
        x = x.flatten(2).transpose(1, 2)  # (B, num_patches, embed_dim)

        # 添加 [CLS] token
        cls = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls, x], dim=1)

        # 添加位置编码
        x = x + self.pos_embed

        return x, {"cls": cls, "patch_grid": (H, W)}


class MultiHeadAttention(nn.Module):
    """
    多头自注意力 — Transformer 的核心

    键值查询机制（KQV）：
      Q = 查询向量（我想找什么）
      K = 键向量（我有什么可以被找到）
      V = 内容向量（找到后返回什么内容）

    公式：Attention(Q,K,V) = softmax(QK^T / √d_k) V
    """
    def __init__(self, embed_dim: int, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % num_heads == 0

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5

        self.qkv = nn.Linear(embed_dim, embed_dim * 3, bias=False)
        self.attn_drop = nn.Dropout(dropout)
        self.proj = nn.Linear(embed_dim, embed_dim)
        self.proj_drop = nn.Dropout(dropout)

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        B, N, C = x.shape

        # QKV 投影
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # (3, B, heads, N, head_dim)
        q, k, v = qkv[0], qkv[1], qkv[2]

        # 注意力计算
        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        # 输出
        out = attn @ v  # (B, heads, N, head_dim)
        out = out.transpose(1, 2).reshape(B, N, C)
        out = self.proj(out)
        out = self.proj_drop(out)

        return out, attn


class TransformerBlock(nn.Module):
    """Transformer 编码器块"""
    def __init__(self, embed_dim: int, num_heads: int = 8,
                 mlp_ratio: float = 4.0, dropout: float = 0.1):
        super().__init__()

        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = MultiHeadAttention(embed_dim, num_heads, dropout)
        self.norm2 = nn.LayerNorm(embed_dim)

        mlp_hidden = int(embed_dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, mlp_hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden, embed_dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        # Self-Attention + 残差
        attn_out, attn_weights = self.attn(self.norm1(x))
        x = x + attn_out

        # MLP + 残差
        x = x + self.mlp(self.norm2(x))

        return x, attn_weights


class VisionTransformer(nn.Module):
    """
    ViT 编码器 — 全局关系建模

    与 CNN 的区别：
      - CNN：局部卷积，层次化抽象（固定感受野）
      - ViT：全局自注意力，动态关系发现（自适应感受野）

    对于建筑场景：
      - ViT 能发现对象之间的长距离依赖关系
      - 比如沙发和茶几之间的搭配关系，不需要手工定义规则
    """

    def __init__(self,
                 img_size: int = 224,
                 patch_size: int = 16,
                 in_channels: int = 3,
                 embed_dim: int = 256,
                 depth: int = 6,
                 num_heads: int = 8,
                 mlp_ratio: float = 4.0,
                 dropout: float = 0.1):
        super().__init__()

        self.patch_embed = PatchEmbedding(
            img_size, patch_size, in_channels, embed_dim)

        self.blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, mlp_ratio, dropout)
            for _ in range(depth)
        ])

        self.norm = nn.LayerNorm(embed_dim)

        # [CLS] token 输出
        self.head = nn.Linear(embed_dim, embed_dim)

        # 注意力权重（用于可视化）
        self.attention_maps: list[Tensor] = []

    def forward(self, x: Tensor) -> dict[str, Tensor]:
        B = x.shape[0]
        self.attention_maps = []

        x, info = self.patch_embed(x)

        for block in self.blocks:
            x, attn = block(x)
            self.attention_maps.append(attn.detach())

        x = self.norm(x)

        # [CLS] token 作为全局表示
        cls_output = x[:, 0]  # (B, embed_dim)
        patch_output = x[:, 1:]  # (B, num_patches, embed_dim)

        return {
            "features": cls_output,        # 全局特征
            "patch_features": patch_output,  # Patch 级别特征
            "cls_token": x[:, 0],
            "attention_weights": self.attention_maps,
        }


# ─────────────────────────────────────────────────────────
# 融合编码器：CNN + ViT
# ─────────────────────────────────────────────────────────

class VisionEncoder(nn.Module):
    """
    融合视觉编码器 — CNN + ViT 双流

    设计原理（来自架构分析）：
      - CNN 流：提供局部层次化特征（边缘→纹理→部件→物体）
      - ViT 流：提供全局关系特征（对象之间的依赖）

    输出：
      - object_features: (B, num_objects, embed_dim) 对象级特征
      - scene_features:  (B, embed_dim)            场景级特征
    """

    def __init__(self,
                 embed_dim: int = 256,
                 cnn_pretrained: bool = False,
                 use_vit: bool = True):
        super().__init__()

        self.embed_dim = embed_dim
        self.use_vit = use_vit

        # CNN 分支（局部特征）
        self.cnn = CNNEncoder(
            input_channels=3,
            embed_dim=embed_dim,
            pretrained=cnn_pretrained,
        )

        # ViT 分支（全局关系）
        if use_vit:
            self.vit = VisionTransformer(
                img_size=224,
                patch_size=16,
                embed_dim=embed_dim,
                depth=6,
                num_heads=8,
            )

        # 特征融合层
        fusion_dim = embed_dim * (2 if use_vit else 1)
        self.fusion = nn.Sequential(
            nn.Linear(fusion_dim, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
            nn.Dropout(0.1),
        )

        # 对象检测头（轻量）
        self.detection_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.ReLU(),
            nn.Linear(embed_dim // 2, 4 + 1),  # bbox (x,y,w,h) + confidence
        )

    def forward(self, images: Tensor) -> dict[str, Tensor]:
        """
        Args:
            images: (B, 3, H, W) or (B, C, H, W)

        Returns:
            scene_features:  (B, embed_dim)   场景级全局特征
            object_features: (B, N, embed_dim) 对象级特征
            detection:       (B, N, 5)        检测框
        """
        # CNN 特征
        cnn_out = self.cnn(images)
        cnn_feat = cnn_out["features"]  # (B, embed_dim)

        if self.use_vit:
            # ViT 特征
            vit_out = self.vit(images)
            vit_feat = vit_out["features"]  # (B, embed_dim)

            # 融合
            fused = torch.cat([cnn_feat, vit_feat], dim=-1)
        else:
            fused = cnn_feat

        scene_feat = self.fusion(fused)  # (B, embed_dim)

        return {
            "scene_features": scene_feat,
            "cnn_features": cnn_feat,
            "vit_features": vit_feat if self.use_vit else None,
            "layer_features": cnn_out,  # 包含各层 CNN 特征
        }


# ─────────────────────────────────────────────────────────
# 图像编码器（简化版，给不在真实图像时用）
# ─────────────────────────────────────────────────────────

class ImageEncoder(nn.Module):
    """
    图像编码器（简化版）

    用于没有真实图像的情况：
      - 输入：图像路径列表
      - 输出：预计算的视觉特征

    在实际部署时，可以用这个从效果图批量提取特征向量，
    然后存入向量数据库（如 FAISS）做检索
    """

    def __init__(self,
                 embed_dim: int = 256,
                 model_name: str = "resnet18",
                 pretrained: bool = False):
        super().__init__()

        self.embed_dim = embed_dim

        try:
            import torchvision.models as models
            weights = "DEFAULT" if pretrained else None
            if model_name == "resnet18":
                self.backbone = models.resnet18(weights=weights)
                feat_dim = 512
            elif model_name == "resnet50":
                self.backbone = models.resnet50(weights=weights)
                feat_dim = 2048
            elif model_name == "efficientnet_b0":
                self.backbone = models.efficientnet_b0(weights=weights)
                feat_dim = 1280
            else:
                self.backbone = models.resnet18(weights=weights)
                feat_dim = 512

            self.backbone.fc = nn.Identity()
        except ImportError:
            # Fallback：无 torchvision
            self.backbone = nn.Sequential(
                nn.Conv2d(3, 64, 7, 2, 3),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.MaxPool2d(3, 2, 1),
                ResBlock(64, 128, 2),
                ResBlock(128, 256, 2),
                ResBlock(256, 512, 2),
                nn.AdaptiveAvgPool2d(1),
            )
            feat_dim = 512

        self.projection = nn.Linear(feat_dim, embed_dim)

    def forward(self, x: Tensor) -> Tensor:
        """
        Args:
            x: (B, 3, H, W) 图像张量
        Returns:
            (B, embed_dim) 特征向量
        """
        feat = self.backbone(x)
        if isinstance(feat, tuple):
            feat = feat[0]
        feat = feat.flatten(1)
        return self.projection(feat)

    def extract_from_pil(self, images: list, device: str = "cpu") -> Tensor:
        """批量从 PIL Image 提取特征"""
        import torchvision.transforms as T
        from PIL import Image

        transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225]),
        ])

        tensors = []
        for img in images:
            if isinstance(img, str):
                img = Image.open(img).convert("RGB")
            tensors.append(transform(img))

        batch = torch.stack(tensors).to(device)
        with torch.no_grad():
            return self.forward(batch)


# ─────────────────────────────────────────────────────────
# 预训练特征提取工具
# ─────────────────────────────────────────────────────────

def extract_scene_features(image_paths: list[str],
                           model_name: str = "resnet18",
                           device: str = "cpu") -> dict[str, list]:
    """
    批量提取场景视觉特征

    用于：
      1. 从 VR 效果图批量提取特征
      2. 存入向量数据库做相似度检索
      3. 作为 scene_graph_builder 的视觉特征输入

    Args:
        image_paths: 图像路径列表
        model_name:  backbone 模型
        device:      运行设备

    Returns:
        {"paths": [...], "features": [...numpy arrays...]}
    """
    import torchvision.transforms as T
    from PIL import Image
    import numpy as np

    encoder = ImageEncoder(embed_dim=256, model_name=model_name)
    encoder.eval()
    encoder.to(device)

    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406],
                   std=[0.229, 0.224, 0.225]),
    ])

    features = []
    valid_paths = []

    for path in image_paths:
        try:
            img = Image.open(path).convert("RGB")
            tensor = transform(img).unsqueeze(0).to(device)
            with torch.no_grad():
                feat = encoder(tensor).cpu().numpy()[0]
            features.append(feat.tolist())
            valid_paths.append(path)
        except Exception as e:
            print(f"Warning: failed to extract {path}: {e}")

    return {"paths": valid_paths, "features": features}
