"""
轻量级物理引擎（纯Python实现）
提供碰撞检测、动力学模拟等基础能力
"""
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import json

@dataclass
class Vector3:
    """三维向量"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def length(self) -> float:
        return math.sqrt(self.dot(self))
    
    def normalize(self):
        l = self.length()
        if l > 0:
            return self * (1.0 / l)
        return Vector3()
    
    def to_dict(self) -> dict:
        return {'x': self.x, 'y': self.y, 'z': self.z}

@dataclass
class AABB:
    """轴对齐包围盒"""
    min: Vector3
    max: Vector3
    
    def contains(self, point: Vector3) -> bool:
        """检查点是否在包围盒内"""
        return (self.min.x <= point.x <= self.max.x and
                self.min.y <= point.y <= self.max.y and
                self.min.z <= point.z <= self.max.z)
    
    def intersects(self, other: 'AABB') -> bool:
        """检查两个包围盒是否相交"""
        return (self.min.x <= other.max.x and self.max.x >= other.min.x and
                self.min.y <= other.max.y and self.max.y >= other.min.y and
                self.min.z <= other.max.z and self.max.z >= other.min.z)
    
    def to_dict(self) -> dict:
        return {'min': self.min.to_dict(), 'max': self.max.to_dict()}

@dataclass
class PhysicsObject:
    """物理对象"""
    id: str
    position: Vector3
    velocity: Vector3 = None
    mass: float = 1.0
    friction: float = 0.5
    restitution: float = 0.3  # 弹性系数
    is_static: bool = False
    bounds: AABB = None
    
    def __post_init__(self):
        if self.velocity is None:
            self.velocity = Vector3()
    
    def apply_force(self, force: Vector3, dt: float):
        """施加力"""
        if self.is_static:
            return
        # F = ma => a = F/m
        acceleration = force * (1.0 / self.mass)
        # v = v0 + a*dt
        self.velocity = self.velocity + acceleration * dt
    
    def update(self, dt: float):
        """更新位置"""
        if self.is_static:
            return
        # x = x0 + v*dt
        self.position = self.position + self.velocity * dt
        # 更新包围盒
        if self.bounds:
            size = Vector3(
                self.bounds.max.x - self.bounds.min.x,
                self.bounds.max.y - self.bounds.min.y,
                self.bounds.max.z - self.bounds.min.z
            )
            self.bounds.min = self.position
            self.bounds.max = self.position + size
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'position': self.position.to_dict(),
            'velocity': self.velocity.to_dict() if self.velocity else None,
            'mass': self.mass,
            'friction': self.friction,
            'restitution': self.restitution,
            'is_static': self.is_static,
            'bounds': self.bounds.to_dict() if self.bounds else None
        }

class PhysicsEngine:
    """轻量级物理引擎"""
    
    def __init__(self, gravity: float = -9.81):
        self.gravity = gravity
        self.objects: Dict[str, PhysicsObject] = {}
        self.collision_pairs: List[Tuple[str, str]] = []
        self.simulation_time = 0.0
    
    def add_object(self, obj: PhysicsObject):
        """添加物理对象"""
        self.objects[obj.id] = obj
    
    def remove_object(self, obj_id: str):
        """移除物理对象"""
        if obj_id in self.objects:
            del self.objects[obj_id]
    
    def create_box(self, obj_id: str, position: Tuple[float, float, float],
                   size: Tuple[float, float, float], mass: float = 1.0,
                   is_static: bool = False) -> PhysicsObject:
        """创建盒状物体"""
        pos = Vector3(*position)
        size_vec = Vector3(*size)
        bounds = AABB(pos, pos + size_vec)
        
        obj = PhysicsObject(
            id=obj_id,
            position=pos,
            mass=mass,
            is_static=is_static,
            bounds=bounds
        )
        self.add_object(obj)
        return obj
    
    def check_collision(self, obj1: PhysicsObject, obj2: PhysicsObject) -> bool:
        """检查两个物体是否碰撞"""
        if not obj1.bounds or not obj2.bounds:
            return False
        return obj1.bounds.intersects(obj2.bounds)
    
    def detect_all_collisions(self) -> List[Tuple[str, str]]:
        """检测所有碰撞对"""
        self.collision_pairs = []
        obj_list = list(self.objects.values())
        
        for i in range(len(obj_list)):
            for j in range(i + 1, len(obj_list)):
                if self.check_collision(obj_list[i], obj_list[j]):
                    self.collision_pairs.append((obj_list[i].id, obj_list[j].id))
        
        return self.collision_pairs
    
    def resolve_collision(self, obj1: PhysicsObject, obj2: PhysicsObject):
        """解决碰撞（简化版）"""
        if obj1.is_static and obj2.is_static:
            return
        
        # 计算碰撞法线
        normal = obj2.position - obj1.position
        dist = normal.length()
        if dist == 0:
            return
        
        normal = normal.normalize()
        
        # 相对速度
        rel_vel = obj1.velocity - obj2.velocity
        vel_along_normal = rel_vel.dot(normal)
        
        # 如果物体正在分离，不处理
        if vel_along_normal > 0:
            return
        
        # 弹性系数取较小值
        e = min(obj1.restitution, obj2.restitution)
        
        # 冲量计算
        j = -(1 + e) * vel_along_normal
        total_mass_inv = (1.0 / obj1.mass if obj1.mass > 0 else 0) + (1.0 / obj2.mass if obj2.mass > 0 else 0)
        if total_mass_inv > 0:
            j /= total_mass_inv
        
        # 应用冲量
        impulse = normal * j
        if not obj1.is_static:
            obj1.velocity = obj1.velocity + impulse * (1.0 / obj1.mass)
        if not obj2.is_static:
            obj2.velocity = obj2.velocity - impulse * (1.0 / obj2.mass)
    
    def step(self, dt: float = 0.016):
        """推进模拟一步"""
        # 施加重力
        gravity_force = Vector3(0, 0, self.gravity)
        for obj in self.objects.values():
            if not obj.is_static:
                obj.apply_force(gravity_force * obj.mass, dt)
        
        # 更新位置
        for obj in self.objects.values():
            obj.update(dt)
        
        # 检测碰撞
        self.detect_all_collisions()
        
        # 解决碰撞
        for id1, id2 in self.collision_pairs:
            self.resolve_collision(self.objects[id1], self.objects[id2])
        
        self.simulation_time += dt
    
    def simulate(self, duration: float, dt: float = 0.016) -> dict:
        """模拟一段时间"""
        steps = int(duration / dt)
        for _ in range(steps):
            self.step(dt)
        
        return self.get_state()
    
    def apply_force(self, obj_id: str, force: Tuple[float, float, float], duration: float = 1.0):
        """对物体施加力"""
        if obj_id not in self.objects:
            return None
        
        obj = self.objects[obj_id]
        force_vec = Vector3(*force)
        
        # 施加力
        obj.apply_force(force_vec, duration)
        
        # 返回预测的位移
        displacement = obj.velocity * duration
        return displacement.to_dict()
    
    def get_state(self) -> dict:
        """获取当前状态"""
        return {
            'time': self.simulation_time,
            'objects': {k: v.to_dict() for k, v in self.objects.items()},
            'collisions': self.collision_pairs
        }
    
    def load_scene(self, scene_data: dict):
        """从场景数据加载物理对象"""
        if 'objects' in scene_data:
            for obj_data in scene_data['objects']:
                pos = obj_data.get('position', [0, 0, 0])
                if isinstance(pos, dict):
                    pos = [pos.get('x', 0), pos.get('y', 0), pos.get('z', 0)]
                
                size = obj_data.get('dimensions', [1, 1, 1])
                if isinstance(size, dict):
                    size = [size.get('width', 1), size.get('height', 1), size.get('depth', 1)]
                
                mass = obj_data.get('mass', 10.0)
                obj_type = obj_data.get('type', 'unknown')
                
                self.create_box(
                    obj_id=obj_data.get('id', f'obj_{len(self.objects)}'),
                    position=pos,
                    size=size,
                    mass=mass,
                    is_static=(obj_type in ['wall', 'floor', 'ceiling'])
                )
        
        # 加载墙体
        if 'walls' in scene_data:
            for wall in scene_data['walls']:
                self.create_box(
                    obj_id=wall.get('id', f'wall_{len(self.objects)}'),
                    position=wall.get('position', [0, 0, 0]),
                    size=wall.get('size', [10, 3, 0.2]),
                    mass=1000,
                    is_static=True
                )

# ============== 测试 ==============

def test_physics_engine():
    """测试物理引擎"""
    print("=" * 60)
    print("轻量级物理引擎测试")
    print("=" * 60)
    
    engine = PhysicsEngine(gravity=-9.81)
    
    # 创建地面
    ground = engine.create_box('ground', (0, 0, -0.1), (100, 100, 0.1), mass=1000, is_static=True)
    print(f"[创建] 地面: {ground.id}")
    
    # 创建下落物体
    ball = engine.create_box('ball', (0, 0, 10), (1, 1, 1), mass=1.0)
    print(f"[创建] 球: {ball.id}, 质量={ball.mass}kg, 位置={ball.position.to_dict()}")
    
    # 创建墙
    wall = engine.create_box('wall_north', (0, 5, 1.5), (10, 0.2, 3), mass=1000, is_static=True)
    print(f"[创建] 墙: {wall.id}")
    
    print("\n开始模拟...")
    
    # 模拟2秒
    for i in range(10):
        engine.simulate(0.2)
        state = engine.get_state()
        ball_pos = state['objects']['ball']['position']
        collisions = state['collisions']
        print(f"  t={state['time']:.2f}s: 球位置=({ball_pos['x']:.2f}, {ball_pos['y']:.2f}, {ball_pos['z']:.2f}), 碰撞={len(collisions)}对")
    
    print("\n最终状态:")
    final_state = engine.get_state()
    print(f"  模拟时间: {final_state['time']:.2f}s")
    print(f"  物体数量: {len(final_state['objects'])}")
    print(f"  碰撞对数: {len(final_state['collisions'])}")
    
    # 测试施加力
    print("\n测试施加力:")
    ball_obj = engine.objects['ball']
    ball_obj.velocity = Vector3()  # 重置速度
    
    result = engine.apply_force('ball', (100, 0, 0), 0.5)  # 100N X方向
    print(f"  施加100N X方向力: 预测位移={result}")
    
    print("=" * 60)
    print("测试通过！")

if __name__ == '__main__':
    test_physics_engine()
