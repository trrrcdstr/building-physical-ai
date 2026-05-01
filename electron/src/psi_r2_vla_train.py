"""
Psi-R2 VLA 监督微调与数据飞轮

数据飞轮流程:
  API调用 → 生成训练样本 → 监督学习 → 模型更新 → 更好预测 → 更多数据
"""

import os
import json
import time
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader


# ─────────────────────────────────────────────
# 1. 训练数据生成器
# ─────────────────────────────────────────────
class TrainingDataGenerator:
    """
    通过 API 调用生成监督学习训练数据
    输入: 自然语言指令
    输出: (instruction_embedding, scene_embedding) → action_sequence
    """

    # 预定义训练任务池（覆盖主要场景）
    TASK_POOL = [
        # 清洁类
        ("清洁客厅地面", "地板", "清洁"),
        ("拖地", "地板", "清洁"),
        ("擦拭茶几表面", "茶几", "清洁"),
        ("打扫卧室地板", "地板", "清洁"),
        ("清理厨房油污", "厨房台面", "清洁"),
        ("擦拭窗户玻璃", "窗户", "清洁"),
        ("整理床铺", "床", "整理"),
        ("收拾桌面杂物", "桌子", "整理"),
        # 移动类
        ("把沙发移到窗户旁边", "沙发", "移动"),
        ("把茶几移到餐桌旁边", "茶几", "移动"),
        ("把椅子搬到阳台", "椅子", "移动"),
        ("把书架移到墙角", "书架", "移动"),
        ("把电视柜移到对面墙", "电视柜", "移动"),
        ("把花盆移到窗台", "花盆", "移动"),
        # 施工类
        ("安装吸顶灯", "天花板", "安装"),
        ("固定墙上挂钩", "墙壁", "固定"),
        ("打孔安装置物架", "墙壁", "安装"),
        ("布线接电", "墙壁", "布线"),
        # 巡检类
        ("巡检消防通道", "通道", "查看"),
        ("检查配电箱", "配电箱", "查看"),
        ("记录仪表读数", "仪表", "记录"),
        ("环境安全检查", "全屋", "查看"),
        # 服务类
        ("送餐到客房", "托盘", "递送"),
        ("递送快递包裹", "包裹", "递送"),
        ("引导访客到会议室", "走廊", "导航"),
        # 园林类
        ("浇花", "植物", "浇灌"),
        ("修剪草坪", "草地", "修剪"),
        ("清理落叶", "地面", "清洁"),
        ("施肥养护", "植物", "浇灌"),
    ]

    def __init__(self, api_base: str = "http://localhost:5001"):
        self.api_base = api_base
        self.samples = []
        self.stats = {"generated": 0, "safe": 0, "unsafe": 0}

    def generate_from_api(self) -> int:
        """调用 API 生成训练样本"""
        import urllib.request

        count = 0
        for instruction, target, action_type in self.TASK_POOL:
            try:
                payload = json.dumps({
                    "instruction": instruction,
                    "target_object": target,
                }, ensure_ascii=False).encode("utf-8")

                req = urllib.request.Request(
                    f"{self.api_base}/api/vla/instruction",
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )

                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())

                plan = data["plan"]
                actions = [a["primitive"] for a in plan["action_sequence"]]
                risk = plan["risk_level"]
                duration = plan["estimated_duration_s"]
                sim_tasks = [t["task"] for t in plan["similar_tasks"]]
                physics_ok = all(
                    not pc.get("can_move", True) or pc.get("can_move", False)
                    for pc in plan["physics_checks"]
                ) or not plan["physics_checks"]

                # 构建训练样本
                sample = {
                    "id": len(self.samples),
                    "timestamp": datetime.now().isoformat(),
                    "instruction": instruction,
                    "target_object": target,
                    "action_sequence": actions,
                    "primary_action": actions[0] if actions else "移动",
                    "action_type": action_type,
                    "risk_level": risk,
                    "duration_s": duration,
                    "physics_feasible": physics_ok,
                    "execution_ready": plan["execution_ready"],
                    "similar_tasks": sim_tasks,
                }

                self.samples.append(sample)
                count += 1
                self.stats["generated"] += 1
                self.stats["safe" if plan["execution_ready"] else "unsafe"] += 1

            except Exception as e:
                print(f"  [Generator] Failed: {instruction} ({e})")

        print(f"[Generator] Generated {count} samples from API")
        return count

    def generate_synthetic(self, n: int = 200) -> int:
        """生成合成训练样本（API 不可用时）"""
        instructions = [
            "移动{}", "清洁{}", "整理{}", "安装{}", "查看{}",
            "递送到{}", "浇灌{}", "巡检{}",
        ]
        objects = [
            "沙发", "茶几", "床", "餐桌", "椅子",
            "书架", "衣柜", "电视机", "花盆", "地毯",
            "窗户", "地板", "墙壁", "厨房台面",
            "冰箱", "洗衣机", "空调",
        ]
        positions = ["窗户旁边", "墙角", "门口", "阳台", "床边", "餐桌旁"]

        for i in range(n):
            tmpl = random.choice(instructions)
            obj = random.choice(objects)
            pos = random.choice(positions)
            instr = tmpl.format(obj)

            action_type = next(
                (a for a in ["清洁", "移动", "安装", "查看", "递送", "浇灌", "巡检", "整理"]
                if a in instr
            ), "移动")

            sample = {
                "id": len(self.samples),
                "timestamp": datetime.now().isoformat(),
                "instruction": instr,
                "target_object": obj,
                "action_sequence": [action_type],
                "primary_action": action_type,
                "action_type": action_type,
                "risk_level": random.choice(["LOW", "LOW", "LOW", "MEDIUM"]),
                "duration_s": round(random.uniform(2, 20), 1),
                "physics_feasible": random.random() > 0.1,
                "execution_ready": random.random() > 0.15,
                "similar_tasks": [],
                "synthetic": True,
            }
            self.samples.append(sample)

        self.stats["generated"] += n
        print(f"[Generator] Created {n} synthetic samples")
        return n

    def save(self, path: str = None):
        """保存训练数据"""
        if path is None:
            path = os.path.join(
                os.path.dirname(__file__),
                "data", "vla_training_samples.json"
            )
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "samples": self.samples,
                "stats": self.stats,
                "generated_at": datetime.now().isoformat(),
            }, f, ensure_ascii=False, indent=2)
        print(f"[Generator] Saved {len(self.samples)} samples to {path}")

    def load(self, path: str):
        """加载已有训练数据"""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.samples = data["samples"]
        self.stats = data.get("stats", {})
        print(f"[Generator] Loaded {len(self.samples)} samples from {path}")


# ─────────────────────────────────────────────
# 2. VLA 监督学习
# ─────────────────────────────────────────────
class VLAEmbedding(nn.Module):
    """
    简化的 VLA 嵌入网络
    输入: 指令 tokens + 场景 tokens
    输出: 动作类别 logits
    """

    VOCAB_SIZE = 5000
    EMBED_DIM = 128
    HIDDEN = 256
    NUM_ACTIONS = 8  # 移动/清洁/安装/查看/递送/浇灌/巡检/整理

    ACTION_MAP = {
        "移动": 0, "清洁": 1, "安装": 2, "查看": 3,
        "递送": 4, "浇灌": 5, "巡检": 6, "整理": 7,
    }

    def __init__(self):
        super().__init__()
        self.token_emb = nn.Embedding(self.VOCAB_SIZE, self.EMBED_DIM)
        self.scene_emb = nn.Embedding(self.VOCAB_SIZE, self.EMBED_DIM)
        self.fusion = nn.Sequential(
            nn.Linear(self.EMBED_DIM * 2, self.HIDDEN),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(self.HIDDEN, self.HIDDEN // 2),
            nn.ReLU(),
            nn.Linear(self.HIDDEN // 2, self.NUM_ACTIONS),
        )
        # 权重初始化
        for m in self.modules():
            if isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    def forward(self, instruction_tokens: torch.Tensor,
               scene_tokens: torch.Tensor) -> torch.Tensor:
        """
        Args:
            instruction_tokens: (batch, seq_len)
            scene_tokens: (batch, seq_len)
        Returns:
            action_logits: (batch, NUM_ACTIONS)
        """
        i_emb = self.token_emb(instruction_tokens).mean(dim=1)   # (B, D)
        s_emb = self.scene_emb(scene_tokens).mean(dim=1)         # (batch, D)
        fused = torch.cat([i_emb, s_emb], dim=1)               # (B, 2D)
        return self.fusion(fused)                                 # (B, NUM_ACTIONS)

    def predict_action(self, instruction_tokens: torch.Tensor,
                     scene_tokens: torch.Tensor) -> tuple[str, float]:
        """推理：返回动作名和置信度"""
        with torch.no_grad():
            logits = self.forward(instruction_tokens, scene_tokens)
            probs = torch.softmax(logits, dim=-1)
            conf, idx = probs.max(dim=-1)
            idx = idx.item()
            conf = conf.item()
        action_name = next(
            (k for k, v in self.ACTION_MAP.items() if v == idx), "移动"
        )
        return action_name, conf


class VLADataset(Dataset):
    """VLA 训练数据集"""

    def __init__(self, samples: list[dict], max_len: int = 32):
        self.samples = samples
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple:
        sample = self.samples[idx]

        # 指令 tokenize（简化：按字哈希）
        instr = sample["instruction"]
        instr_ids = self._tokenize(instr)

        # 场景 tokenize（简化：对象名哈希）
        scene = sample.get("target_object", "") + " " + (sample.get("similar_tasks", []) or [""])[0]
        scene_ids = self._tokenize(scene)

        # Label
        action_name = sample["primary_action"]
        label = VLAEmbedding.ACTION_MAP.get(action_name, 0)

        # Risk encoding
        risk_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        risk = risk_map.get(sample.get("risk_level", "LOW"), 0)

        return (
            torch.tensor(instr_ids, dtype=torch.long),
            torch.tensor(scene_ids, dtype=torch.long),
            torch.tensor(label, dtype=torch.long),
            torch.tensor(risk, dtype=torch.long),
        )

    def _tokenize(self, text: str) -> list[int]:
        """简化 tokenize: 按字符 ASCII 码 % VOCAB_SIZE"""
        ids = [ord(c) % VLAEmbedding.VOCAB_SIZE for c in text]
        if len(ids) < self.max_len:
            ids = ids + [0] * (self.max_len - len(ids))
        return ids[:self.max_len]


def train_vla(
    train_samples: list[dict],
    val_samples: list[dict] = None,
    epochs: int = 50,
    batch_size: int = 16,
    lr: float = 0.001,
    device: str = None,
    save_path: str = None,
) -> dict:
    """
    监督学习训练 Psi-R2 VLA

    Returns:
        training_history: {"train_loss": [...], "val_acc": [...], "best_epoch": int}
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    model = VLAEmbedding().to(device)
    print(f"[Trainer] Model params: {sum(p.numel() for p in model.parameters()):,}")
    print(f"[Trainer] Device: {device}")

    train_dataset = VLADataset(train_samples)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    val_loader = None
    if val_samples:
        val_dataset = VLADataset(val_samples)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    history = {"train_loss": [], "val_acc": []}
    best_val_acc = 0.0
    best_state = None

    print(f"[Trainer] Training on {len(train_dataset)} samples, {epochs} epochs...")
    for epoch in range(epochs):
        # Train
        model.train()
        total_loss = 0.0
        for instr, scene, label, risk in train_loader:
            instr = instr.to(device)
            scene = scene.to(device)
            label = label.to(device)

            logits = model(instr, scene)
            loss = criterion(logits, label)

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        history["train_loss"].append(round(avg_loss, 4))

        if val_loader:
            model.eval()
            correct = 0
            total = 0
            with torch.no_grad():
                for instr, scene, label, risk in val_loader:
                    instr, scene, label = instr.to(device), scene.to(device), label.to(device)
                    logits = model(instr, scene)
                    correct += (logits.argmax(1) == label).sum().item()
                    total += label.size(0)

            val_acc = correct / max(total, 1)
            history["val_acc"].append(round(val_acc, 4))

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            val_acc = 0.0

        if (epoch + 1) % 10 == 0:
            print(f"  Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f} | Val Acc: {val_acc:.4f}")

    # 保存最佳模型
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model": best_state or model.state_dict(),
            "action_map": VLAEmbedding.ACTION_MAP,
            "history": history,
        }, save_path)
        print(f"[Trainer] Model saved to {save_path}")

    print(f"[Trainer] Best Val Acc: {best_val_acc:.4f}")
    history["best_val_acc"] = round(best_val_acc, 4)
    history["best_epoch"] = int(np.argmax(history["val_acc"])) if history["val_acc"] else 0
    return history


# ─────────────────────────────────────────────
# 3. 数据飞轮主循环
# ─────────────────────────────────────────────
class DataFlywheel:
    """
    数据飞轮：自动收集数据 + 训练 + 评估 + 迭代
    """

    def __init__(
        self,
        api_base: str = "http://localhost:5001",
        data_dir: str = None,
    ):
        self.api_base = api_base
        self.data_dir = Path(data_dir or os.path.join(
            os.path.dirname(__file__), "data", "flywheel"
        ))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.generator = TrainingDataGenerator(api_base)
        self.model_path = self.data_dir / "vla_model.pt"
        self.stats_path = self.data_dir / "flywheel_stats.json"

        # 加载已有模型（如果有）
        self.model = None
        if self.model_path.exists():
            self._load_model()
            print(f"[Flywheel] Loaded existing model")

        self.cycle = 0

    def _load_model(self):
        checkpoint = torch.load(self.model_path, map_location="cpu")
        self.model = VLAEmbedding()
        self.model.load_state_dict(checkpoint["model"])
        print(f"[Flywheel] Loaded model from {self.model_path}")

    def _save_stats(self):
        with open(self.stats_path, "w", encoding="utf-8") as f:
            json.dump({
                "cycle": self.cycle,
                "total_samples": len(self.generator.samples),
                "stats": self.generator.stats,
                "model_path": str(self.model_path),
            }, f, ensure_ascii=False, indent=2)

    def run_cycle(self, n_synthetic: int = 50) -> dict:
        """
        运行一个飞轮周期

        1. 生成新训练数据
        2. 监督学习微调
        3. 评估改进
        """
        self.cycle += 1
        print(f"\n{'='*55}")
        print(f"  Flywheel Cycle #{self.cycle}")
        print(f"{'='*55}")

        # Step 1: 生成数据
        print(f"\n[1/3] Generating training data...")
        api_samples = self.generator.generate_from_api()
        if api_samples == 0:
            print("  API unavailable, generating synthetic data...")
        self.generator.generate_synthetic(n_synthetic)

        # 保存数据
        self.generator.save(str(self.data_dir / "training_samples.json"))

        # Step 2: 训练
        print(f"\n[2/3] Training VLA model...")
        samples = self.generator.samples
        random.seed(42)
        random.shuffle(samples)
        split = int(len(samples) * 0.8)
        train_samples = samples[:split]
        val_samples = samples[split:]

        history = train_vla(
            train_samples=train_samples,
            val_samples=val_samples,
            epochs=30,
            batch_size=16,
            lr=0.001,
            save_path=str(self.model_path),
        )

        # Step 3: 评估
        print(f"\n[3/3] Evaluation:")
        print(f"  Best Val Acc: {history.get('best_val_acc', 'N/A')}")
        print(f"  Best Epoch: {history.get('best_epoch', 'N/A')}")
        print(f"  Total Samples: {len(samples)}")
        print(f"  Safe Rate: {self.generator.stats['safe'] / max(self.generator.stats['generated'], 1):.1%}")

        self._save_stats()
        return {
            "cycle": self.cycle,
            "samples": len(samples),
            "history": history,
            "stats": self.generator.stats,
        }


# ─────────────────────────────────────────────
# 快速启动
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  Psi-R2 VLA Data Flywheel")
    print("=" * 55)

    flywheel = DataFlywheel()

    # 运行1个周期（生成50条合成数据+API数据，训练30轮）
    result = flywheel.run_cycle(n_synthetic=50)

    print(f"\n{'='*55}")
    print("  Flywheel Complete!")
    print(f"  Cycle: {result['cycle']}")
    print(f"  Samples: {result['samples']}")
    print(f"  Best Accuracy: {result['history'].get('best_val_acc', 'N/A')}")
    print(f"  Model: {flywheel.model_path}")
    print("=" * 55)
