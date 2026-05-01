"""
合成数据生成器 - 机器人操作场景
基于真实数据规则，自动生成大量模拟的机器人操作场景

功能：
1. 生成随机房间布局
2. 生成随机物体位置
3. 生成机器人任务（钻孔/搬运/清洁等）
4. 生成正负样本（成功/失败案例）
5. 输出为训练数据格式

输出格式：
{
  "scene_id": "synthetic_001",
  "scene_type": "living_room",
  "objects": [...],
  "walls": {...},
  "tasks": [...]
}
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

# ============== 数据结构 ==============

class WallType(Enum):
    LOAD_BEARING = "load_bearing"
    NON_LOAD_BEARING = "non_load_bearing"
    PARTITION = "partition"

class TaskType(Enum):
    DRILL = "drill"
    MOVE = "move"
    CLEAN = "clean"
    INSPECT = "inspect"

class TaskResult(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"

@dataclass
class Vector3:
    x: float
    y: float
    z: float
    
    def to_dict(self):
        return {"x": self.x, "y": self.y, "z": self.z}

@dataclass
class Pipe:
    type: str  # electrical, water, gas
    depth_cm: float
    from_floor_cm: float
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Wall:
    wall_id: str
    wall_type: str
    thickness_cm: float
    material: str
    pipes: List[Pipe] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "wall_id": self.wall_id,
            "type": self.wall_type,
            "thickness_cm": self.thickness_cm,
            "material": self.material,
            "pipes": [p.to_dict() for p in self.pipes]
        }

@dataclass
class SceneObject:
    name: str
    position: Vector3
    weight_kg: float
    size: str  # small, medium, large
    movable: bool
    
    def to_dict(self):
        return {
            "name": self.name,
            "position": self.position.to_dict(),
            "weight_kg": self.weight_kg,
            "size": self.size,
            "movable": self.movable
        }

@dataclass
class Task:
    task_id: str
    task_type: str
    instruction: str
    expected_result: str
    constraints: List[str]
    steps: List[str]
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "instruction": self.instruction,
            "expected_result": self.expected_result,
            "constraints": self.constraints,
            "steps": self.steps
        }

@dataclass
class SyntheticScene:
    scene_id: str
    scene_type: str
    room_area_m2: float
    objects: List[SceneObject]
    walls: Dict[str, Wall]
    tasks: List[Task]
    metadata: Dict[str, Any]
    
    def to_dict(self):
        return {
            "scene_id": self.scene_id,
            "scene_type": self.scene_type,
            "room_area_m2": self.room_area_m2,
            "objects": [o.to_dict() for o in self.objects],
            "walls": {k: v.to_dict() for k, v in self.walls.items()},
            "tasks": [t.to_dict() for t in self.tasks],
            "metadata": self.metadata
        }

# ============== 配置参数 ==============

SCENE_TYPES = [
    "living_room", "bedroom", "study", "kitchen", 
    "bathroom", "dining_room", "office", "hotel_room"
]

WALL_MATERIALS = {
    "load_bearing": ["concrete", "reinforced_concrete"],
    "non_load_bearing": ["brick", "aerated_concrete"],
    "partition": ["gypsum", "glass", "wood"]
}

OBJECT_TEMPLATES = {
    "living_room": [
        {"name": "沙发", "weight_range": (30, 80), "size": "large", "movable": True},
        {"name": "茶几", "weight_range": (10, 20), "size": "medium", "movable": True},
        {"name": "电视", "weight_range": (10, 20), "size": "medium", "movable": True},
        {"name": "电视柜", "weight_range": (20, 40), "size": "medium", "movable": True},
        {"name": "地毯", "weight_range": (5, 10), "size": "large", "movable": True}
    ],
    "bedroom": [
        {"name": "床", "weight_range": (60, 100), "size": "large", "movable": False},
        {"name": "衣柜", "weight_range": (80, 150), "size": "large", "movable": False},
        {"name": "床头柜", "weight_range": (10, 20), "size": "small", "movable": True},
        {"name": "梳妆台", "weight_range": (20, 40), "size": "medium", "movable": True}
    ],
    "study": [
        {"name": "书桌", "weight_range": (20, 40), "size": "medium", "movable": True},
        {"name": "书架", "weight_range": (50, 100), "size": "large", "movable": False},
        {"name": "椅子", "weight_range": (5, 15), "size": "small", "movable": True},
        {"name": "电脑", "weight_range": (5, 10), "size": "small", "movable": True}
    ],
    "kitchen": [
        {"name": "冰箱", "weight_range": (50, 80), "size": "large", "movable": True},
        {"name": "微波炉", "weight_range": (10, 20), "size": "small", "movable": True},
        {"name": "餐桌", "weight_range": (20, 40), "size": "medium", "movable": True},
        {"name": "橱柜", "weight_range": (50, 100), "size": "large", "movable": False}
    ]
}

DRILL_INSTRUCTIONS = [
    "在{wall}钻一个{diameter}mm的孔",
    "能不能在{wall}钻孔",
    "{wall}可以打孔吗",
    "我想在{wall}挂画，需要打孔",
    "在{wall}钻个孔装架子"
]

MOVE_INSTRUCTIONS = [
    "把{object}搬到{target}",
    "移动{object}到{target}",
    "将{object}挪到{target}",
    "帮我搬一下{object}到{target}"
]

CLEAN_INSTRUCTIONS = [
    "清理{room}的地板",
    "打扫{room}",
    "擦拭{object}"
]

# ============== 生成器 ==============

class SyntheticDataGenerator:
    """合成数据生成器"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
        self.scene_counter = 0
        self.task_counter = 0
    
    def _generate_scene_id(self) -> str:
        self.scene_counter += 1
        return f"synthetic_{self.scene_counter:04d}"
    
    def _generate_task_id(self) -> str:
        self.task_counter += 1
        return f"task_{self.task_counter:04d}"
    
    # ============== 墙体生成 ==============
    
    def _generate_walls(self) -> Dict[str, Wall]:
        """生成墙体配置"""
        walls = {}
        wall_ids = ["north", "south", "east", "west"]
        
        # 随机决定哪面墙是承重墙（至少1面，最多2面）
        num_load_bearing = random.randint(1, 2)
        load_bearing_walls = random.sample(wall_ids, num_load_bearing)
        
        for wall_id in wall_ids:
            if wall_id in load_bearing_walls:
                wall_type = "load_bearing"
                thickness = random.randint(20, 30)
                material = random.choice(WALL_MATERIALS["load_bearing"])
                # 承重墙通常有管线
                pipes = self._generate_pipes()
            else:
                # 非承重墙或隔墙
                if random.random() < 0.3:
                    wall_type = "partition"
                    thickness = random.randint(8, 12)
                    material = random.choice(WALL_MATERIALS["partition"])
                    pipes = []  # 隔墙通常无管线
                else:
                    wall_type = "non_load_bearing"
                    thickness = random.randint(12, 18)
                    material = random.choice(WALL_MATERIALS["non_load_bearing"])
                    pipes = self._generate_pipes() if random.random() < 0.5 else []
            
            walls[wall_id] = Wall(
                wall_id=wall_id,
                wall_type=wall_type,
                thickness_cm=thickness,
                material=material,
                pipes=pipes
            )
        
        return walls
    
    def _generate_pipes(self) -> List[Pipe]:
        """生成管线"""
        pipes = []
        pipe_types = ["electrical", "water", "gas"]
        
        # 随机选择1-2种管线
        selected = random.sample(pipe_types, random.randint(1, 2))
        
        for pipe_type in selected:
            depth = random.randint(5, 20)
            from_floor = random.randint(20, 150)
            pipes.append(Pipe(type=pipe_type, depth_cm=depth, from_floor_cm=from_floor))
        
        return pipes
    
    # ============== 物体生成 ==============
    
    def _generate_objects(self, scene_type: str, room_area: float) -> List[SceneObject]:
        """生成物体"""
        objects = []
        
        templates = OBJECT_TEMPLATES.get(scene_type, OBJECT_TEMPLATES["living_room"])
        
        # 随机选择3-6个物体
        num_objects = random.randint(3, min(6, len(templates)))
        selected = random.sample(templates, num_objects)
        
        for template in selected:
            # 随机位置（在房间范围内）
            x = random.uniform(0.5, room_area ** 0.5 - 0.5)
            y = random.uniform(0.5, room_area ** 0.5 - 0.5)
            z = 0.0
            
            # 随机重量
            weight = random.uniform(*template["weight_range"])
            
            # 可移动性（根据重量调整）
            movable = template["movable"] and weight < 60
            
            objects.append(SceneObject(
                name=template["name"],
                position=Vector3(x, y, z),
                weight_kg=round(weight, 1),
                size=template["size"],
                movable=movable
            ))
        
        return objects
    
    # ============== 任务生成 ==============
    
    def _generate_drill_task(self, walls: Dict[str, Wall]) -> Task:
        """生成钻孔任务"""
        wall_names = {"north": "北墙", "south": "南墙", "east": "东墙", "west": "西墙"}
        
        # 随机选择一面墙
        wall_id = random.choice(list(walls.keys()))
        wall = walls[wall_id]
        wall_name = wall_names[wall_id]
        
        # 生成指令
        diameter = random.choice([6, 8, 10, 12, 15])
        instruction = random.choice(DRILL_INSTRUCTIONS).format(
            wall=wall_name, diameter=diameter
        )
        
        # 判断结果
        if wall.wall_type == "load_bearing":
            expected_result = "failure"
            constraints = [
                f"{wall_name}是承重墙",
                f"厚度{wall.thickness_cm}cm",
                "禁止钻孔"
            ]
            steps = [
                "检测到承重墙",
                "操作被拒绝",
                "建议选择非承重墙"
            ]
        elif wall.pipes:
            expected_result = "warning"
            constraints = [
                f"{wall_name}内有管线",
                f"厚度{wall.thickness_cm}cm"
            ]
            steps = [
                "使用探测仪定位管线",
                "避开管线位置",
                "执行钻孔"
            ]
        else:
            expected_result = "success"
            constraints = [
                f"{wall_name}是{'非承重墙' if wall.wall_type == 'non_load_bearing' else '隔墙'}",
                f"厚度{wall.thickness_cm}cm"
            ]
            steps = [
                "确认墙体类型",
                "标记钻孔位置",
                "执行钻孔"
            ]
        
        return Task(
            task_id=self._generate_task_id(),
            task_type="drill",
            instruction=instruction,
            expected_result=expected_result,
            constraints=constraints,
            steps=steps
        )
    
    def _generate_move_task(self, objects: List[SceneObject]) -> Task:
        """生成搬运任务"""
        if not objects:
            return None
        
        # 选择一个可移动的物体
        movable_objects = [o for o in objects if o.movable]
        if not movable_objects:
            movable_objects = objects
        
        obj = random.choice(movable_objects)
        
        # 目标位置
        targets = ["卧室", "客厅", "书房", "阳台", "储物间"]
        target = random.choice(targets)
        
        # 生成指令
        instruction = random.choice(MOVE_INSTRUCTIONS).format(
            object=obj.name, target=target
        )
        
        # 判断结果
        if obj.weight_kg > 50:
            expected_result = "warning"
            constraints = [
                f"{obj.name}重量{obj.weight_kg}kg",
                "需要多人搬运或使用工具"
            ]
            steps = [
                "准备搬运工具",
                "清空物体内容物",
                "2人协作搬运",
                "放置到目标位置"
            ]
        else:
            expected_result = "success"
            constraints = [
                f"{obj.name}重量{obj.weight_kg}kg",
                "单人可搬运"
            ]
            steps = [
                "抬起物体",
                "搬运到目标位置",
                "放置"
            ]
        
        return Task(
            task_id=self._generate_task_id(),
            task_type="move",
            instruction=instruction,
            expected_result=expected_result,
            constraints=constraints,
            steps=steps
        )
    
    def _generate_clean_task(self, scene_type: str) -> Task:
        """生成清洁任务"""
        room_names = {
            "living_room": "客厅",
            "bedroom": "卧室",
            "study": "书房",
            "kitchen": "厨房",
            "bathroom": "卫生间"
        }
        room_name = room_names.get(scene_type, "房间")
        
        instruction = random.choice(CLEAN_INSTRUCTIONS).format(room=room_name, object="地板")
        
        return Task(
            task_id=self._generate_task_id(),
            task_type="clean",
            instruction=instruction,
            expected_result="success",
            constraints=["无特殊约束"],
            steps=[
                "准备清洁工具",
                "清扫/拖地",
                "检查清洁效果"
            ]
        )
    
    # ============== 场景生成 ==============
    
    def generate_scene(self) -> SyntheticScene:
        """生成单个场景"""
        scene_type = random.choice(SCENE_TYPES)
        room_area = random.uniform(10, 30)
        
        # 生成墙体
        walls = self._generate_walls()
        
        # 生成物体
        objects = self._generate_objects(scene_type, room_area)
        
        # 生成任务（混合类型）
        tasks = []
        
        # 1-2个钻孔任务
        for _ in range(random.randint(1, 2)):
            tasks.append(self._generate_drill_task(walls))
        
        # 1个搬运任务
        move_task = self._generate_move_task(objects)
        if move_task:
            tasks.append(move_task)
        
        # 1个清洁任务
        tasks.append(self._generate_clean_task(scene_type))
        
        return SyntheticScene(
            scene_id=self._generate_scene_id(),
            scene_type=scene_type,
            room_area_m2=round(room_area, 1),
            objects=objects,
            walls=walls,
            tasks=tasks,
            metadata={
                "generator": "synthetic_v1",
                "timestamp": "2026-04-21"
            }
        )
    
    def generate_batch(self, count: int) -> List[SyntheticScene]:
        """批量生成场景"""
        scenes = []
        for i in range(count):
            scenes.append(self.generate_scene())
            if (i + 1) % 10 == 0:
                print(f"  已生成 {i + 1}/{count} 个场景")
        return scenes
    
    def save_to_json(self, scenes: List[SyntheticScene], output_path: str):
        """保存为JSON"""
        data = {
            "metadata": {
                "total_scenes": len(scenes),
                "total_tasks": sum(len(s.tasks) for s in scenes),
                "scene_types": list(set(s.scene_type for s in scenes))
            },
            "scenes": [s.to_dict() for s in scenes]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[合成生成器] 已保存到: {output_path}")

# ============== 主函数 ==============

if __name__ == "__main__":
    print("=" * 60)
    print("合成数据生成器 - 机器人操作场景")
    print("=" * 60)
    
    generator = SyntheticDataGenerator(seed=42)  # 固定种子保证可复现
    
    # 生成100个场景
    print("\n[生成器] 开始生成场景...")
    scenes = generator.generate_batch(100)
    
    # 统计
    print("\n[统计]")
    print(f"  场景数: {len(scenes)}")
    print(f"  任务数: {sum(len(s.tasks) for s in scenes)}")
    
    # 任务类型分布
    task_types = {}
    for scene in scenes:
        for task in scene.tasks:
            task_types[task.task_type] = task_types.get(task.task_type, 0) + 1
    print(f"  任务类型: {task_types}")
    
    # 结果分布
    results = {}
    for scene in scenes:
        for task in scene.tasks:
            results[task.expected_result] = results.get(task.expected_result, 0) + 1
    print(f"  结果分布: {results}")
    
    # 保存
    output_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\training")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "synthetic_scenes_v1.json"
    generator.save_to_json(scenes, str(output_path))
    
    # 打印示例
    print("\n" + "=" * 60)
    print("示例场景:")
    print("=" * 60)
    
    sample = scenes[0]
    print(f"\n场景ID: {sample.scene_id}")
    print(f"场景类型: {sample.scene_type}")
    print(f"房间面积: {sample.room_area_m2} m²")
    print(f"物体数: {len(sample.objects)}")
    print(f"任务数: {len(sample.tasks)}")
    
    print("\n任务示例:")
    for task in sample.tasks[:2]:
        print(f"\n  [{task.task_type}] {task.instruction}")
        print(f"  预期结果: {task.expected_result}")
        print(f"  约束: {', '.join(task.constraints)}")
