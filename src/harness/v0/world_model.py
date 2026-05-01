"""
World Model — JEPA 具身AI世界模型集成
把"编码器+预测器"接入 Harness 的推理闭环
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import json
import numpy as np
from datetime import datetime


# -------------------------------------------------
# JEPA 核心组件
# -------------------------------------------------

@dataclass
class LatentState:
    """潜在状态向量"""
    z_spatial: np.ndarray   # 空间特征 [dim=32]
    z_physics: np.ndarray    # 物理特征 [dim=32]
    z_affordance: np.ndarray # 功能特征 [dim=32]
    confidence: float = 1.0   # 置信度

    def to_vector(self) -> np.ndarray:
        return np.concatenate([self.z_spatial, self.z_physics, self.z_affordance])

    @classmethod
    def from_room_data(cls, room_data: Dict) -> 'LatentState':
        """从房间数据生成潜在状态"""
        cat = room_data.get("room_category", "其他")

        # 空间特征编码（基于房间类型）
        spatial = cls._encode_spatial(cat, room_data.get("dimensions", {}))

        # 物理特征编码（基于物理标签）
        physics = cls._encode_physics(cat, room_data.get("physics_tags", []))

        # 功能特征编码（基于房间用途）
        affordance = cls._encode_affordance(cat)

        return cls(z_spatial=spatial, z_physics=physics, z_affordance=affordance)

    @staticmethod
    def _encode_spatial(cat: str, dims: Dict) -> np.ndarray:
        """空间特征编码"""
        dim = 32
        vec = np.zeros(dim)

        # 房间大小编码
        w = dims.get("width", 4) / 10.0
        d = dims.get("depth", 4) / 10.0
        vec[0] = min(w, 1.0)
        vec[1] = min(d, 1.0)
        vec[2] = min(dims.get("height", 2.8) / 4.0, 1.0)

        # 房间类型编码（哈希到向量）
        cat_hash = sum(ord(c) * (i + 1) for i, c in enumerate(cat))
        for i in range(3, dim):
            vec[i] = ((cat_hash >> (i % 8)) & 1) * 0.5

        return vec

    @staticmethod
    def _encode_physics(cat: str, tags: List[str]) -> np.ndarray:
        """物理特征编码"""
        dim = 32
        vec = np.zeros(dim)

        PHYSICS_MAP = {
            "客厅": {"friction": 0.5, "moisture": 0.0, "fragile": 0.1},
            "厨房": {"friction": 0.35, "moisture": 0.6, "fragile": 0.3},
            "卫生间": {"friction": 0.25, "moisture": 0.9, "fragile": 0.2},
            "主卧": {"friction": 0.45, "moisture": 0.1, "fragile": 0.2},
            "餐厅": {"friction": 0.4, "moisture": 0.0, "fragile": 0.4},
            "楼梯": {"friction": 0.5, "moisture": 0.3, "fragile": 0.0},
            "其他": {"friction": 0.4, "moisture": 0.2, "fragile": 0.2},
        }

        props = PHYSICS_MAP.get(cat, PHYSICS_MAP["其他"])
        vec[0] = props["friction"]
        vec[1] = props["moisture"]
        vec[2] = props["fragile"]

        # 物理标签编码
        for i, tag in enumerate(tags[:8]):
            vec[3 + i] = 0.5 + hash(tag) % 50 / 100

        return vec

    @staticmethod
    def _encode_affordance(cat: str) -> np.ndarray:
        """功能特征编码"""
        dim = 32
        vec = np.zeros(dim)

        AFFORDANCE_MAP = {
            "客厅": {"traversable": 1.0, "graspable": 0.1, "openable": 0.0},
            "厨房": {"traversable": 0.6, "graspable": 0.5, "openable": 0.8},
            "卫生间": {"traversable": 0.5, "graspable": 0.2, "openable": 0.7},
            "主卧": {"traversable": 0.9, "graspable": 0.3, "openable": 0.6},
            "餐厅": {"traversable": 0.8, "graspable": 0.6, "openable": 0.2},
            "楼梯": {"traversable": 0.3, "climbable": 1.0, "openable": 0.0},
        }

        props = AFFORDANCE_MAP.get(cat, {})
        vec[0] = props.get("traversable", 0.5)
        vec[1] = props.get("graspable", 0.2)
        vec[2] = props.get("openable", 0.3)
        vec[3] = props.get("climbable", 0.0)

        return vec


# -------------------------------------------------
# JEPA 预测器
# -------------------------------------------------

class JEPAPredictor:
    """
    JEPA 预测器

    给定当前状态 z_t 和行动 a_t，
    预测下一个状态 z_{t+1}
    """

    def __init__(self, latent_dim: int = 96):
        self.latent_dim = latent_dim

        # 简单的线性预测器（未来升级为神经网络）
        # z_{t+1} = z_t + f(z_t, a_t)
        # 这里用简单的状态转移矩阵
        self.transition_weights = np.random.randn(latent_dim, latent_dim) * 0.01

    def predict(self, current_state: LatentState, action: Dict) -> LatentState:
        """
        预测下一个状态

        action 格式：
        {
            "type": "move" | "grasp" | "open" | "pour" | "navigate",
            "target": [x, y, z],
            "object": "物体名称",
            ...
        }
        """
        # 编码行动向量
        action_vec = self._encode_action(action)

        # 状态转移
        current_z = current_state.to_vector()
        delta_z = np.tanh(
            self.transition_weights @ (current_z + action_vec * 0.3)
        ) * 0.1

        # 预测下一步
        predicted_z = current_z + delta_z

        # 解码预测状态
        z_spatial = predicted_z[:32]
        z_physics = predicted_z[32:64]
        z_affordance = predicted_z[64:]

        return LatentState(
            z_spatial=z_spatial,
            z_physics=z_physics,
            z_affordance=z_affordance,
            confidence=current_state.confidence * 0.9,  # 预测置信度衰减
        )

    def _encode_action(self, action: Dict) -> np.ndarray:
        """行动编码"""
        vec = np.zeros(self.latent_dim)

        ACTION_TYPES = {"move": 0, "grasp": 1, "open": 2, "pour": 3, "navigate": 4}
        action_type = action.get("type", "move")
        if action_type in ACTION_TYPES:
            vec[ACTION_TYPES[action_type]] = 1.0

        # 目标位置编码
        target = action.get("target", [0, 0, 0])
        vec[10:13] = np.array(target) / 10.0

        return vec


# -------------------------------------------------
# 世界模型
# -------------------------------------------------

class WorldModel:
    """
    世界模型 — JEPA 架构的具身AI实现

    组件：
    1. 编码器（Encoder）: 观测 → 潜在表示
    2. 预测器（Predictor）: 当前状态 + 行动 → 预测状态
    3. 规划器（Planner）: 目标 → 行动序列
    """

    def __init__(self):
        self.encoder = {}          # 各类型编码器
        self.predictor = JEPAPredictor()
        self.state_history: List[LatentState] = []
        self.trajectory: List[Dict] = []

    def encode(self, room_data: Dict) -> LatentState:
        """
        编码器：将房间数据编码为潜在状态
        """
        state = LatentState.from_room_data(room_data)
        self.state_history.append(state)
        return state

    def predict(self, current_state: LatentState, action: Dict) -> LatentState:
        """
        预测器：预测下一个状态
        """
        predicted = self.predictor.predict(current_state, action)
        self.state_history.append(predicted)
        return predicted

    def plan(
        self,
        start_state: LatentState,
        goal_description: str,
        robot_capabilities: List[str],
    ) -> List[Dict]:
        """
        规划器：为机器人规划行动序列

        简化版：基于规则的规划
        进阶版：MCTS / MPC（待实现）
        """
        actions = []

        # 解析目标
        if "到达" in goal_description or "navigate" in goal_description.lower():
            actions.append({"type": "move", "description": "移动到目标位置"})
        if "抓取" in goal_description or "grasp" in goal_description.lower():
            actions.append({"type": "grasp", "description": "抓取目标物体"})
        if "打开" in goal_description or "open" in goal_description.lower():
            actions.append({"type": "open", "description": "打开门/抽屉/柜门"})

        # 填充行动序列
        return actions if actions else [{"type": "move", "description": "原地等待"}]

    def decode(self, state: LatentState) -> Dict:
        """
        解码器：将潜在状态解码为可解释的属性
        """
        z_p = state.z_physics

        return {
            "predicted_friction": float(z_p[0]),
            "predicted_moisture": float(z_p[1]),
            "predicted_fragility": float(z_p[2]),
            "confidence": state.confidence,
        }

    def simulate_trajectory(
        self,
        start_state: LatentState,
        actions: List[Dict],
        max_steps: int = 10,
    ) -> List[Dict]:
        """
        模拟行动轨迹，返回每一步的状态预测
        """
        trajectory = []
        current = start_state

        for i, action in enumerate(actions[:max_steps]):
            predicted = self.predict(current, action)
            decoded = self.decode(predicted)
            trajectory.append({
                "step": i + 1,
                "action": action.get("type", "unknown"),
                "state": decoded,
                "confidence": predicted.confidence,
            })
            current = predicted

        self.trajectory = trajectory
        return trajectory

    def get_world_summary(self) -> Dict:
        """获取世界模型当前状态"""
        return {
            "total_states": len(self.state_history),
            "trajectory_steps": len(self.trajectory),
            "last_state_confidence": (
                self.state_history[-1].confidence
                if self.state_history else 0
            ),
        }


# -------------------------------------------------
# 与 Harness 集成
# -------------------------------------------------

def create_world_model_pipeline():
    """
    创建世界模型流水线（与 Harness 集成）
    """
    world_model = WorldModel()

    def run(vr_room_data: Dict, goal: str = "分析物理属性") -> Dict:
        # 1. 编码
        state = world_model.encode(vr_room_data)

        # 2. 规划
        actions = world_model.plan(state, goal, ["move", "grasp", "open"])

        # 3. 模拟
        trajectory = world_model.simulate_trajectory(state, actions)

        # 4. 解码
        decoded = world_model.decode(state)

        return {
            "latent_state": {
                "spatial_dim": len(state.z_spatial),
                "physics_dim": len(state.z_physics),
                "affordance_dim": len(state.z_affordance),
            },
            "planned_actions": actions,
            "trajectory": trajectory,
            "decoded_properties": decoded,
            "world_summary": world_model.get_world_summary(),
        }

    return run, world_model
