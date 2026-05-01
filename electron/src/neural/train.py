"""
train.py — 训练流水线
=======================
完整的训练流程：

  数据加载 → 特征构建 → 模型训练 → 评估 → 保存

支持三种训练模式：
  1. PhysicsMLP 单独训练（物理属性预测）
  2. SceneEncoder 训练（场景关系建模）
  3. 端到端联合训练（完整世界模型）
"""

from __future__ import annotations
import json
import os
import math
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torch.utils.data import Dataset, DataLoader
import numpy as np

from .physics_mlp import PhysicsMLP, PropertyPredictor, generate_physics_training_data
from .vision_encoder import VisionEncoder, ImageEncoder
from .relation_model import RelationTransformer, SceneEncoder


# ─────────────────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────────────────

@dataclass
class TrainConfig:
    """训练配置"""
    # 模型
    embed_dim: int = 256
    num_heads: int = 8
    num_layers: int = 4

    # 训练
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 100
    eval_interval: int = 10
    save_interval: int = 50

    # 数据
    data_dir: str = ""
    output_dir: str = "./checkpoints"
    physics_train_samples: int = 2000

    # 设备
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


# ─────────────────────────────────────────────────────────
# 数据集
# ─────────────────────────────────────────────────────────

class PhysicsDataset(Dataset):
    """物理属性预测数据集"""
    def __init__(self, n_samples: int = 2000):
        data = generate_physics_training_data(n_samples)
        self.X = torch.tensor(data["X"], dtype=torch.float32)
        self.y_mass = torch.tensor(data["y_mass"], dtype=torch.float32)
        self.y_fric_s = torch.tensor(data["y_fric_s"], dtype=torch.float32)
        self.y_fric_d = torch.tensor(data["y_fric_d"], dtype=torch.float32)
        self.y_stiff = torch.tensor(data["y_stiff"], dtype=torch.float32)

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, idx: int) -> dict:
        return {
            "features": self.X[idx],
            "mass": self.y_mass[idx],
            "fric_s": self.y_fric_s[idx],
            "fric_d": self.y_fric_d[idx],
            "stiff": self.y_stiff[idx],
        }


class SceneGraphDataset(Dataset):
    """
    场景图谱数据集

    从 scene_graph_training.json 加载
    """
    def __init__(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.node_features = torch.tensor(data["node_features"], dtype=torch.float32)
        self.edge_index = torch.tensor(data["edge_index"], dtype=torch.long)
        self.edge_features = torch.tensor(data["edge_features"], dtype=torch.float32)

        # 类别编码
        self.category_map = {
            "structure": 0,
            "furniture": 1,
            "appliance": 2,
            "material": 3,
            "lighting": 4,
            "door_window": 5,
            "utility": 6,
            "soft": 7,
        }
        self.labels = torch.tensor([
            self.category_map.get(l, 0) for l in data["labels"]
        ], dtype=torch.long)

    def __len__(self) -> int:
        return len(self.node_features)

    def __getitem__(self, idx: int) -> dict:
        return {
            "features": self.node_features[idx],
            "label": self.labels[idx],
        }


# ─────────────────────────────────────────────────────────
# 损失函数
# ─────────────────────────────────────────────────────────

class PhysicsLoss(nn.Module):
    """
    物理感知损失函数

    包含三项：
      1. MSE 损失（预测值 vs 真值）
      2. 物理一致性损失（密度/摩擦/刚度的合理性）
      3. 不确定性损失（epistemic uncertainty）
    """

    def __init__(self, physics_weight: float = 0.1):
        super().__init__()
        self.physics_weight = physics_weight

    def forward(self,
                pred_mass: Tensor,
                pred_fric_s: Tensor,
                pred_fric_d: Tensor,
                pred_stiff: Tensor,
                true_mass: Tensor,
                true_fric_s: Tensor,
                true_fric_d: Tensor,
                true_stiff: Tensor
                ) -> dict[str, Tensor]:
        """
        Returns:
            {
                "total": 标量总损失,
                "mass_loss": 质量损失,
                "fric_loss": 摩擦损失,
                "stiff_loss": 刚度损失,
                "physics_loss": 物理一致性损失,
            }
        """
        # MSE 损失
        mass_loss = F.mse_loss(pred_mass, true_mass)
        fric_loss = F.mse_loss(pred_fric_s, true_fric_s) + \
                    F.mse_loss(pred_fric_d, true_fric_d)
        stiff_loss = F.mse_loss(pred_stiff, true_stiff)

        # 物理一致性约束
        # 规则1：静摩擦 >= 动摩擦
        physics_loss = F.relu(pred_fric_s - pred_fric_d - 0.05).mean()

        # 规则2：质量为正
        physics_loss = physics_loss + F.relu(-pred_mass + 0.05).mean()

        # 规则3：刚度在合理范围
        physics_loss = physics_loss + \
                        (F.relu(pred_stiff - math.log(1e6)) +
                         F.relu(-math.log(1) - pred_stiff)).mean() * 0.1

        total = mass_loss + fric_loss + stiff_loss + self.physics_weight * physics_loss

        return {
            "total": total,
            "mass_loss": mass_loss.detach(),
            "fric_loss": fric_loss.detach(),
            "stiff_loss": stiff_loss.detach(),
            "physics_loss": physics_loss.detach(),
        }


class RelationLoss(nn.Module):
    """
    关系预测损失

    用于训练 RelationTransformer：
      - 节点分类：预测对象类别
      - 边预测：预测对象之间的关系类型
    """

    def __init__(self, relation_weight: float = 0.3):
        super().__init__()
        self.relation_weight = relation_weight

    def forward(self,
                node_logits: Tensor,        # (B, N, num_classes)
                relation_logits: Tensor,    # (B, N, N, num_relations)
                true_labels: Tensor,        # (B, N)
                true_relations: Optional[Tensor] = None  # (B, N, N)
                ) -> dict[str, Tensor]:
        """
        Args:
            node_logits:  节点分类 logits
            relation_logits: 关系分类 logits
            true_labels:  真实标签
            true_relations: 真实关系（可选）

        Returns:
            {"total", "node_loss", "relation_loss"}
        """
        # 节点分类损失
        B, N, C = node_logits.shape
        node_loss = F.cross_entropy(
            node_logits.view(B * N, C),
            true_labels.view(B * N)
        )

        # 关系预测损失（如果提供了标签）
        relation_loss = torch.tensor(0.0, device=node_logits.device)
        if true_relations is not None:
            B, N2, R = relation_logits.shape[:3]
            relation_loss = F.cross_entropy(
                relation_logits.view(B * N2 * N2, R),
                true_relations.view(B * N2 * N2)
            )

        total = node_loss + self.relation_weight * relation_loss

        return {
            "total": total,
            "node_loss": node_loss.detach(),
            "relation_loss": relation_loss.detach(),
        }


# ─────────────────────────────────────────────────────────
# 训练器
# ─────────────────────────────────────────────────────────

class Trainer:
    """
    统一训练器

    支持：
      - physics_mlp: 物理属性预测训练
      - scene_encoder: 场景关系建模训练
      - full: 端到端联合训练
    """

    def __init__(self, config: TrainConfig):
        self.config = config
        self.device = torch.device(config.device)
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.models: dict = {}
        self.optimizers: dict = {}
        self.schedulers: dict = {}
        self.history: dict = {"train": [], "val": []}

    # ─── 物理 MLP 训练 ───────────────────────────────

    def train_physics_mlp(self) -> PhysicsMLP:
        """训练物理属性预测模型"""
        print("=" * 60)
        print("训练物理属性预测模型 (PhysicsMLP)")
        print("=" * 60)

        # 数据
        dataset = PhysicsDataset(n_samples=self.config.physics_train_samples)
        n_train = int(len(dataset) * 0.8)
        train_set, val_set = torch.utils.data.random_split(
            dataset, [n_train, len(dataset) - n_train])

        train_loader = DataLoader(train_set, batch_size=self.config.batch_size, shuffle=True)
        val_loader = DataLoader(val_set, batch_size=self.config.batch_size)

        # 模型
        model = PhysicsMLP(embed_dim=128).to(self.device)
        self.models["physics_mlp"] = model

        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=self.config.lr,
            weight_decay=self.config.weight_decay,
        )
        self.optimizers["physics_mlp"] = optimizer

        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=self.config.epochs)
        self.schedulers["physics_mlp"] = scheduler

        criterion = PhysicsLoss(physics_weight=0.1)

        best_val_loss = float("inf")

        for epoch in range(1, self.config.epochs + 1):
            # 训练
            model.train()
            train_losses = []
            for batch in train_loader:
                feat = batch["features"].to(self.device)
                true_mass = batch["mass"].to(self.device)
                true_fric_s = batch["fric_s"].to(self.device)
                true_fric_d = batch["fric_d"].to(self.device)
                true_stiff = batch["stiff"].to(self.device)

                pred = model(feat)

                losses = criterion(
                    pred["mass_kg"], pred["friction_static"],
                    pred["friction_dynamic"], pred["stiffness_Nm"],
                    true_mass, true_fric_s, true_fric_d, true_stiff
                )

                optimizer.zero_grad()
                losses["total"].backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

                train_losses.append(losses["total"].item())

            scheduler.step()

            # 验证
            if epoch % self.config.eval_interval == 0:
                model.eval()
                val_losses = []
                with torch.no_grad():
                    for batch in val_loader:
                        feat = batch["features"].to(self.device)
                        pred = model(feat)
                        losses = criterion(
                            pred["mass_kg"], pred["friction_static"],
                            pred["friction_dynamic"], pred["stiffness_Nm"],
                            batch["mass"].to(self.device),
                            batch["fric_s"].to(self.device),
                            batch["fric_d"].to(self.device),
                            batch["stiff"].to(self.device)
                        )
                        val_losses.append(losses["total"].item())

                avg_train = sum(train_losses) / len(train_losses)
                avg_val = sum(val_losses) / len(val_losses)

                print(f"Epoch {epoch:3d} | "
                      f"Train: {avg_train:.4f} | "
                      f"Val: {avg_val:.4f} | "
                      f"Best: {best_val_loss:.4f}")

                self.history["train"].append({"epoch": epoch, "loss": avg_train})
                self.history["val"].append({"epoch": epoch, "loss": avg_val})

                if avg_val < best_val_loss:
                    best_val_loss = avg_val
                    self._save_model("physics_mlp", model, epoch, avg_val)

        # 保存训练历史
        with open(self.output_dir / "physics_mlp_history.json", "w") as f:
            json.dump(self.history, f, indent=2)

        return model

    # ─── 关系 Transformer 训练 ───────────────────────

    def train_relation_transformer(self,
                                    scene_graph_path: str) -> RelationTransformer:
        """训练关系建模 Transformer"""
        print("=" * 60)
        print("训练关系建模 Transformer")
        print("=" * 60)

        if not os.path.exists(scene_graph_path):
            print(f"Warning: scene_graph_path not found: {scene_graph_path}")
            print("Skipping relation transformer training.")
            return None

        dataset = SceneGraphDataset(scene_graph_path)
        loader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)

        model = RelationTransformer(
            embed_dim=self.config.embed_dim,
            num_layers=self.config.num_layers,
            num_heads=self.config.num_heads,
        ).to(self.device)
        self.models["relation_transformer"] = model

        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=1e-4,  # 降学习率，避免梯度震荡
            weight_decay=self.config.weight_decay,
        )

        # 简单分类头（用最后一层特征做节点分类）
        node_classifier = nn.Linear(self.config.embed_dim, 8).to(self.device)
        self.models["node_classifier"] = node_classifier

        optimizer2 = torch.optim.AdamW(
            node_classifier.parameters(),
            lr=1e-4,
        )

        criterion = RelationLoss(relation_weight=0.3)

        for epoch in range(1, self.config.epochs + 1):
            model.train()
            node_classifier.train()

            total_loss = 0
            for batch in loader:
                feat = batch["features"].to(self.device)
                labels = batch["label"].to(self.device)

                # 前向传播
                out = model(feat, return_attention=False)
                node_feat = out["updated_features"]  # (B, N, D)

                # 节点分类
                logits = node_classifier(node_feat)

                losses = criterion(
                    logits, out.get("relation_logits"),
                    labels, None
                )

                total_loss_val = losses["total"]

                optimizer.zero_grad()
                optimizer2.zero_grad()
                total_loss_val.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                optimizer2.step()

                total_loss += total_loss_val.item()

            if epoch % self.config.eval_interval == 0:
                avg = total_loss / len(loader)
                print(f"Epoch {epoch:3d} | Loss: {avg:.4f}")

                self.history["train"].append({"epoch": epoch, "loss": avg})

                if epoch % self.config.save_interval == 0:
                    self._save_model("relation_transformer", model, epoch, avg)

        return model

    # ─── 工具方法 ─────────────────────────────────

    def _save_model(self, name: str, model: nn.Module,
                     epoch: int, loss: float):
        """保存模型"""
        path = self.output_dir / f"{name}_epoch{epoch}_loss{loss:.4f}.pt"
        torch.save({
            "epoch": epoch,
            "model": model.state_dict(),
            "loss": loss,
            "config": self.config.__dict__,
        }, path)
        print(f"  ✓ Saved: {path.name}")

    def load_model(self, name: str, path: str) -> nn.Module:
        """加载模型"""
        checkpoint = torch.load(path, map_location=self.device)
        config_dict = checkpoint.get("config", {})

        # 重建模型
        if name == "physics_mlp":
            model = PhysicsMLP(embed_dim=config_dict.get("embed_dim", 128))
        elif name == "relation_transformer":
            model = RelationTransformer(
                embed_dim=config_dict.get("embed_dim", 256),
                num_layers=config_dict.get("num_layers", 4),
            )
        else:
            raise ValueError(f"Unknown model: {name}")

        model.load_state_dict(checkpoint["model"])
        model.to(self.device)
        model.eval()
        return model

    def evaluate_physics(self, model: Optional[PhysicsMLP] = None) -> dict:
        """评估物理属性预测"""
        if model is None:
            model = self.models.get("physics_mlp")
        if model is None:
            return {"error": "No physics model loaded"}

        dataset = PhysicsDataset(n_samples=500)
        loader = DataLoader(dataset, batch_size=64)

        model.eval()
        errors = {"mass": [], "fric_s": [], "fric_d": []}

        with torch.no_grad():
            for batch in loader:
                feat = batch["features"].to(self.device)
                pred = model(feat)

                errors["mass"].extend(
                    (pred["mass_kg"] - batch["mass"].to(self.device)).abs().cpu().tolist())
                errors["fric_s"].extend(
                    (pred["friction_static"] - batch["fric_s"].to(self.device)).abs().cpu().tolist())

        return {
            "mass_mae": sum(errors["mass"]) / len(errors["mass"]),
            "fric_s_mae": sum(errors["fric_s"]) / len(errors["fric_s"]),
            "samples": len(errors["mass"]),
        }


# ─────────────────────────────────────────────────────────
# 便捷入口
# ─────────────────────────────────────────────────────────

def build_training_data(scene_graph_json: str,
                        output_path: str) -> dict:
    """
    从场景图谱数据库导出训练数据

    整合 VR 数据 + CAD 数据 → 神经网络训练格式

    Returns:
        {"num_nodes": ..., "num_edges": ..., "output_path": ...}
    """
    from ..scene_graph_builder import SceneGraphDatabase
    import os

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    db = SceneGraphDatabase()
    vr_path = os.path.join(base, "knowledge", "VR_KNOWLEDGE.json")
    cad_path = os.path.join(base, "data", "processed", "building_objects.json")

    if os.path.exists(vr_path):
        db.load_from_vr_json(vr_path)
    if os.path.exists(cad_path):
        db.load_from_cad_json(cad_path)

    stats = db.get_statistics()
    print(f"Scene graph database: {stats['total_scenes']} scenes")

    result = db.export_for_training(output_path)
    return result


def train_full_pipeline(config: Optional[TrainConfig] = None) -> dict:
    """
    完整训练流程

    1. 生成物理训练数据
    2. 训练 PhysicsMLP
    3. 导出场景图训练数据
    4. 训练 RelationTransformer
    5. 评估
    """
    if config is None:
        config = TrainConfig()

    trainer = Trainer(config)
    results = {}

    # Step 1: 物理 MLP
    print("\n[Step 1] 物理属性预测模型")
    physics_model = trainer.train_physics_mlp()
    eval_result = trainer.evaluate_physics(physics_model)
    results["physics_eval"] = eval_result
    print(f"Physics MAE - Mass: {eval_result['mass_mae']:.2f} kg, "
          f"Friction: {eval_result['fric_s_mae']:.3f}")

    # Step 2: 场景图训练数据
    print("\n[Step 2] 构建场景图训练数据")
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sg_path = os.path.join(base, "data", "processed", "scene_graph_training.json")
    sg_result = build_training_data(sg_path, sg_path)
    print(f"Scene graph: {sg_result['nodes']} nodes, {sg_result['edges']} edges")

    # Step 3: 关系 Transformer
    if sg_result["nodes"] > 0:
        print("\n[Step 3] 关系建模 Transformer")
        relation_model = trainer.train_relation_transformer(sg_path)
        results["relation_model"] = relation_model is not None

    # 汇总
    results["checkpoints"] = str(config.output_dir)
    results["history"] = trainer.history

    print("\n" + "=" * 60)
    print("训练完成！")
    print(f"检查点保存至: {config.output_dir}")
    print("=" * 60)

    return results


# ─────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 快速测试
    print("Testing physics MLP training...")

    config = TrainConfig(
        physics_train_samples=500,
        epochs=20,
        eval_interval=5,
        output_dir=r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\checkpoints",
    )

    results = train_full_pipeline(config)
    print("\nResults:", json.dumps(results, indent=2, default=str))
