"""
L3 核心世界模型层 - 物理引擎模块
非拟合的先天物理建模：牛顿力学 + 刚体动力学 + 碰撞检测
区别于通用模型的数据拟合，直接内置物理规律，保证物理仿真的准确性
"""

import numpy as np
import torch
from typing import Optional


# ─────────────────────────────────────────────
# 建筑材料物理参数数据库
# ─────────────────────────────────────────────
MATERIAL_DB = {
    # 密度(kg/m³), 摩擦系数, 弹性模量(GPa), 承重极限(kg/m²)
    "混凝土":    {"density": 2300, "friction": 0.6,  "elasticity": 30,  "load_limit": 2500},
    "钢材":      {"density": 7850, "friction": 0.4,  "elasticity": 200, "load_limit": 10000},
    "木材":      {"density": 600,  "friction": 0.5,  "elasticity": 12,  "load_limit": 500},
    "玻璃":      {"density": 2500, "friction": 0.3,  "elasticity": 70,  "load_limit": 100},
    "瓷砖":      {"density": 2400, "friction": 0.4,  "elasticity": 50,  "load_limit": 800},
    "大理石":    {"density": 2700, "friction": 0.35, "elasticity": 55, "load_limit": 600},
    "石膏板":    {"density": 800,  "friction": 0.5,  "elasticity": 3,   "load_limit": 50},
    "铝合金":    {"density": 2700, "friction": 0.3,  "elasticity": 70, "load_limit": 2000},
    "地毯":      {"density": 200,  "friction": 0.8,  "elasticity": 0.1, "load_limit": 20},
    "实木地板":  {"density": 700,  "friction": 0.45, "elasticity": 10, "load_limit": 400},
    "地毯绒面":  {"density": 300,  "friction": 0.85, "elasticity": 0.05, "load_limit": 30},
    "强化地板":  {"density": 800,  "friction": 0.4,  "elasticity": 8,   "load_limit": 350},
    "水泥地面":  {"density": 2100, "friction": 0.55, "elasticity": 25, "load_limit": 2000},
}

# ─────────────────────────────────────────────
# 家具质量参考 (kg)
# ─────────────────────────────────────────────
FURNITURE_MASS = {
    "沙发": 45, "单人沙发": 25, "双人沙发": 55, "三人沙发": 75,
    "茶几": 15, "电视柜": 20, "餐桌": 35, "餐椅": 8,
    "书桌": 25, "办公椅": 12, "书柜": 40, "衣柜": 60,
    "床": 50, "床垫": 30, "床头柜": 8,
    "橱柜": 45, "冰箱": 60, "洗衣机": 70, "空调室内机": 12,
    "落地灯": 5, "台灯": 2, "电视": 15,
    "箱子": 20, "纸箱": 5, "行李箱": 15,
    "绿植": 8, "花盆": 3,
    "婴儿床": 25, "餐桌椅套装": 80,
}


class PhysicalEngine:
    """
    物理引擎：非拟合的先天物理建模

    功能：
    1. 牛顿力学计算（重力/速度/加速度）
    2. 碰撞检测（AABB 2D）
    3. 摩擦/弹性响应
    4. 稳定性判断（重心投影）
    5. 承重校验
    6. 轨迹预测（抛物线）
    """

    def __init__(self, gravity: float = 9.81, device: str = "cpu"):
        self.g = gravity
        self.device = device
        print(f"[PhysicalEngine] Gravity: {gravity} m/s^2 | Device: {device}")

    def check_collision_2d(self, box1: dict, box2: dict) -> bool:
        """
        AABB 2D 碰撞检测（俯视图）
        box: {"x": float, "z": float, "width": float, "depth": float}
        """
        l1 = box1["x"] - box1["width"] / 2
        r1 = box1["x"] + box1["width"] / 2
        l2 = box2["x"] - box2["width"] / 2
        r2 = box2["x"] + box2["width"] / 2
        no_overlap_x = r1 < l2 or r2 < l1

        t1 = box1["z"] - box1["depth"] / 2
        b1 = box1["z"] + box1["depth"] / 2
        t2 = box2["z"] - box2["depth"] / 2
        b2 = box2["z"] + box2["depth"] / 2
        no_overlap_z = b1 < t2 or b2 < t1

        return not (no_overlap_x or no_overlap_z)

    def stability_check(self, obj: dict, surface: dict) -> dict:
        """
        稳定性判断：重心是否在支撑面投影内
        obj: {"x", "z", "mass", "width", "depth"}
        surface: {"x", "z", "width", "depth", "material"}
        """
        cx, cz = obj["x"], obj["z"]
        sx, sz = surface["x"], surface["z"]
        sw, sd = surface["width"], surface["depth"]

        # 重心投影检查（留10%安全余量）
        margin = 0.9
        in_x = abs(cx - sx) <= (obj["width"] / 2 + sw / 2) * margin
        in_z = abs(cz - sz) <= (obj["depth"] / 2 + sd / 2) * margin

        # 承重校验
        mat_props = MATERIAL_DB.get(surface.get("material", "木材"), MATERIAL_DB["木材"])
        load_limit = mat_props["load_limit"]
        area = obj["width"] * obj["depth"] / 10000  # cm² -> m²
        pressure = obj["mass"] / max(area, 0.0001)  # kg/m²

        is_stable = in_x and in_z and (pressure <= load_limit)

        return {
            "stable": is_stable,
            "pressure_kg_m2": round(pressure, 1),
            "load_limit_kg_m2": load_limit,
            "safety_factor": round(load_limit / max(pressure, 0.1), 2),
            "in_x": in_x,
            "in_z": in_z,
            "material": surface.get("material", "未知"),
            "check_pass": is_stable,
        }

    def simulate_drop(
        self,
        start_height: float,
        mass: float,
        time: float = 1.0,
    ) -> dict:
        """
        模拟自由落体
        Returns: 位置、速度、动能
        """
        h = max(0, start_height - 0.5 * self.g * time ** 2)
        v = self.g * time
        ke = 0.5 * mass * v ** 2
        return {
            "height_m": round(h, 3),
            "velocity_m_s": round(v, 2),
            "kinetic_energy_J": round(ke, 1),
            "impact_force_N": round(mass * self.g * 2, 1),
        }

    def trajectory_prediction(
        self,
        start: dict,
        velocity: float,
        angle_deg: float,
        steps: int = 10,
    ) -> list[dict]:
        """
        轨迹预测（抛物线）
        start: {"x", "y", "z"}
        """
        angle = np.radians(angle_deg)
        vx = velocity * np.cos(angle)
        vy = velocity * np.sin(angle)
        vz = velocity * 0.1  # 侧向初速度

        points = []
        for t in np.linspace(0, 2 * vy / self.g, steps):
            x = start["x"] + vx * t
            y = max(0, start["y"] + vy * t - 0.5 * self.g * t ** 2)
            z = start["z"] + vz * t
            points.append({"t": round(float(t), 2), "x": round(float(x), 3),
                           "y": round(float(y), 3), "z": round(float(z), 3)})
        return points

    def get_mass(self, object_type: str) -> float:
        """获取物体质量（kg）"""
        for key, mass in FURNITURE_MASS.items():
            if key in object_type:
                return mass
        return 10.0  # 默认10kg

    def material_properties(self, material: str) -> dict:
        """获取材料物理属性"""
        return MATERIAL_DB.get(material, MATERIAL_DB["木材"])

    def friction_force(self, normal_force: float, material: str = "木材") -> float:
        """计算摩擦力（N）"""
        mu = MATERIAL_DB.get(material, MATERIAL_DB["木材"])["friction"]
        return mu * normal_force

    def can_push(self, obj_mass: float, robot_max_force: float = 200.0,
                 material: str = "木材") -> dict:
        """判断机器人能否推动物体"""
        mu = MATERIAL_DB.get(material, MATERIAL_DB["木材"])["friction"]
        fn = obj_mass * self.g
        ff = self.friction_force(fn, material)
        can_move = ff <= robot_max_force

        return {
            "can_move": can_move,
            "object_mass_kg": obj_mass,
            "friction_force_N": round(ff, 1),
            "robot_max_force_N": robot_max_force,
            "required_force_N": round(ff, 1),
            "material": material,
            "safety_margin_N": round(robot_max_force - ff, 1),
        }


# ─────────────────────────────────────────────
# 全局单例
# ─────────────────────────────────────────────
_engine: Optional[PhysicalEngine] = None


def get_physical_engine(device: str = "cpu") -> PhysicalEngine:
    global _engine
    if _engine is None:
        _engine = PhysicalEngine(device=device)
    return _engine
