"""
link_train.py — Link Prediction 训练（关系建模）
=================================================
任务：给定两个节点的标准化特征，预测它们之间是否存在边（空间关系）

数据：
  data/processed/relation_training_data.json
  - num_nodes: 248
  - node_features: (248, 48) 标准化后
  - pairs: [{node_i, node_j, label}, ...]
  - task: link_prediction
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

from .relation_model import RelationTransformer


@dataclass
class TrainConfig:
    embed_dim: int = 128
    num_heads: int = 4
    num_layers: int = 3
    batch_size: int = 64
    lr: float = 5e-4
    weight_decay: float = 1e-4
    epochs: int = 200
    eval_interval: int = 20
    save_interval: int = 50
    output_dir: str = "./data/processed/checkpoints"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class LinkPredictionDataset(Dataset):
    """Link Prediction 数据集"""
    def __init__(self, json_path: str, node_features: np.ndarray):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.node_features = torch.tensor(node_features, dtype=torch.float32)
        self.pairs = data["pairs"]
        self.n_train = data["num_train"]

        self.is_train = True  # 可切换

    def set_mode(self, is_train: bool):
        self.is_train = is_train

    def __len__(self) -> int:
        if self.is_train:
            return self.n_train
        else:
            return len(self.pairs) - self.n_train

    def __getitem__(self, idx: int) -> dict:
        if self.is_train:
            pair = self.pairs[idx]
        else:
            pair = self.pairs[self.n_train + idx]

        i = pair["node_i"]
        j = pair["node_j"]
        label = pair["label"]

        feat_i = self.node_features[i]
        feat_j = self.node_features[j]

        return {
            "feat_i": feat_i,
            "feat_j": feat_j,
            "label": torch.tensor(label, dtype=torch.float32),
        }


class LinkPredictor(nn.Module):
    """
    边存在预测器

    给两个节点特征 → 预测是否存在边
    结构：双塔编码 → 拼接 → MLP → sigmoid
    """
    def __init__(self, input_dim: int, embed_dim: int = 128):
        super().__init__()
        # 两个共享编码器
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(embed_dim, embed_dim),
            nn.LayerNorm(embed_dim),
        )
        # 边预测头：拼接两个编码 + 元素积
        self.head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(embed_dim, 64),
            nn.GELU(),
            nn.Linear(64, 1),
        )

    def forward(self, feat_i: Tensor, feat_j: Tensor) -> Tensor:
        """
        feat_i: (B, D)
        feat_j: (B, D)
        返回: (B, 1) 边存在的概率
        """
        enc_i = self.encoder(feat_i)  # (B, E)
        enc_j = self.encoder(feat_j)  # (B, E)

        # 三种交互方式
        concat = torch.cat([enc_i, enc_j, enc_i * enc_j], dim=-1)  # (B, 3E)
        score = self.head(concat)  # (B, 1)
        return torch.sigmoid(score.squeeze(-1))  # (B,)


class Trainer:
    def __init__(self, config: Optional[TrainConfig] = None):
        self.config = config or TrainConfig()
        self.device = torch.device(self.config.device)
        self.models = {}

        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.history = {"train": [], "val": []}

    def train(self, data_path: str, node_features: np.ndarray):
        """主训练入口"""
        print("=" * 60)
        print("Link Prediction 训练")
        print("=" * 60)
        print(f"Device: {self.device}")
        print(f"Node features: {node_features.shape}")

        # 数据
        train_ds = LinkPredictionDataset(data_path, node_features)
        val_ds = LinkPredictionDataset(data_path, node_features)
        val_ds.set_mode(False)

        train_loader = DataLoader(train_ds, batch_size=self.config.batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=self.config.batch_size)

        print(f"Train: {len(train_ds)} samples | Val: {len(val_ds)} samples")

        # 模型
        input_dim = node_features.shape[1]  # 48
        model = LinkPredictor(input_dim=input_dim, embed_dim=self.config.embed_dim).to(self.device)
        self.models["link_predictor"] = model

        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=self.config.lr,
            weight_decay=self.config.weight_decay,
        )

        criterion = nn.BCELoss()

        best_val_acc = 0
        best_val_loss = float('inf')

        for epoch in range(1, self.config.epochs + 1):
            # 训练
            model.train()
            train_loss = 0
            train_correct = 0
            train_total = 0

            for batch in train_loader:
                feat_i = batch["feat_i"].to(self.device)
                feat_j = batch["feat_j"].to(self.device)
                labels = batch["label"].to(self.device)

                preds = model(feat_i, feat_j)
                loss = criterion(preds, labels)

                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

                train_loss += loss.item() * len(labels)
                train_correct += ((preds > 0.5) == (labels > 0.5)).sum().item()
                train_total += len(labels)

            train_loss /= train_total
            train_acc = train_correct / train_total

            # 验证
            if epoch % self.config.eval_interval == 0:
                model.eval()
                val_loss = 0
                val_correct = 0
                val_total = 0

                with torch.no_grad():
                    for batch in val_loader:
                        feat_i = batch["feat_i"].to(self.device)
                        feat_j = batch["feat_j"].to(self.device)
                        labels = batch["label"].to(self.device)

                        preds = model(feat_i, feat_j)
                        loss = criterion(preds, labels)

                        val_loss += loss.item() * len(labels)
                        val_correct += ((preds > 0.5) == (labels > 0.5)).sum().item()
                        val_total += len(labels)

                val_loss /= val_total
                val_acc = val_correct / val_total

                print(f"Epoch {epoch:3d} | "
                      f"Train loss={train_loss:.4f} acc={train_acc:.3f} | "
                      f"Val loss={val_loss:.4f} acc={val_acc:.3f} | "
                      f"best={best_val_acc:.3f}")

                self.history["train"].append({
                    "epoch": epoch, "loss": train_loss, "acc": train_acc
                })
                self.history["val"].append({
                    "epoch": epoch, "loss": val_loss, "acc": val_acc
                })

                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    best_val_loss = val_loss
                    self._save_model("link_predictor", model, epoch, val_loss, val_acc)

        # 保存训练历史
        with open(self.output_dir / "link_predictor_history.json", "w") as f:
            json.dump(self.history, f, indent=2)

        print(f"\nBest Val Acc: {best_val_acc:.3f} | Loss: {best_val_loss:.4f}")
        print(f"Checkpoints saved to: {self.output_dir}")
        return model

    def _save_model(self, name: str, model: nn.Module,
                    epoch: int, loss: float, acc: float):
        path = self.output_dir / f"{name}_best.pt"
        torch.save({
            "epoch": epoch,
            "loss": float(loss),
            "acc": float(acc),
            "model_state": model.state_dict(),
            "config": {
                "input_dim": self.config.embed_dim * 3,
                "embed_dim": self.config.embed_dim,
            }
        }, path)
        print(f"  [*] Saved: {path} (acc={acc:.3f})")


if __name__ == "__main__":
    base = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed"

    # 加载标准化后的节点特征
    with open(f"{base}\\scene_graph_training_clean.json", "r", encoding="utf-8") as f:
        d = json.load(f)
    node_features = np.array(d["node_features"], dtype=np.float32)
    useful_dims = d["useful_dims"]

    print(f"Feature dims: {node_features.shape[1]} (useful: {len(useful_dims)})")

    # 训练
    trainer = Trainer()
    trainer.train(
        data_path=f"{base}\\relation_training_data.json",
        node_features=node_features,
    )
