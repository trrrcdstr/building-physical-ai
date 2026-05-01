"""
物理仿真模块

为4D动态场景提供物理仿真支持
"""

import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class PhysicsState:
    """物理状态"""
    position: np.ndarray   # [3] 位置
    velocity: np.ndarray   # [3] 速度
    acceleration: np.ndarray  # [3] 加速度
    mass: float            # 质量
    friction: float        # 摩擦系数


class PhysicsSimulator:
    """
    物理仿真器
    
    提供碰撞检测、轨迹规划等物理仿真功能
    """
    
    def __init__(self, dt: float = 0.01):
        """
        初始化仿真器
        
        Args:
            dt: 时间步长（秒）
        """
        self.dt = dt
        self.gravity = np.array([0, -9.8, 0])
        self.objects: List[PhysicsState] = []
    
    def add_object(
        self,
        position: np.ndarray,
        velocity: np.ndarray = None,
        mass: float = 1.0,
        friction: float = 0.5
    ):
        """添加物体"""
        self.objects.append(PhysicsState(
            position=position,
            velocity=velocity or np.zeros(3),
            acceleration=np.zeros(3),
            mass=mass,
            friction=friction
        ))
    
    def step(self):
        """执行一步仿真"""
        for obj in self.objects:
            # 更新加速度（重力 + 摩擦）
            obj.acceleration = self.gravity - obj.friction * obj.velocity
            
            # 更新速度
            obj.velocity += obj.acceleration * self.dt
            
            # 更新位置
            obj.position += obj.velocity * self.dt
            
            # 地面碰撞
            if obj.position[1] < 0:
                obj.position[1] = 0
                obj.velocity[1] = -obj.velocity[1] * 0.5  # 反弹
    
    def simulate(self, duration: float) -> List[List[np.ndarray]]:
        """
        运行仿真
        
        Args:
            duration: 仿真时长（秒）
            
        Returns:
            每个物体在每个时间步的位置轨迹
        """
        num_steps = int(duration / self.dt)
        trajectories = [[] for _ in self.objects]
        
        for _ in range(num_steps):
            self.step()
            for i, obj in enumerate(self.objects):
                trajectories[i].append(obj.position.copy())
        
        return trajectories
    
    def check_collision(
        self,
        pos1: np.ndarray,
        pos2: np.ndarray,
        radius1: float,
        radius2: float
    ) -> bool:
        """检查两个球体是否碰撞"""
        distance = np.linalg.norm(pos1 - pos2)
        return distance < (radius1 + radius2)
    
    def resolve_collision(
        self,
        obj1: PhysicsState,
        obj2: PhysicsState,
        radius1: float,
        radius2: float
    ):
        """解决碰撞"""
        # 计算碰撞法向量
        normal = obj2.position - obj1.position
        normal = normal / np.linalg.norm(normal)
        
        # 计算相对速度
        rel_vel = obj1.velocity - obj2.velocity
        vel_normal = np.dot(rel_vel, normal)
        
        # 如果物体正在分离，不处理
        if vel_normal > 0:
            return
        
        # 计算冲量
        e = 0.8  # 恢复系数
        j = -(1 + e) * vel_normal
        j /= 1 / obj1.mass + 1 / obj2.mass
        
        # 应用冲量
        obj1.velocity += j / obj1.mass * normal
        obj2.velocity -= j / obj2.mass * normal
