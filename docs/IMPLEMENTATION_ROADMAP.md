# CAD→4D空间智能 实现路线图

> 目标：从CAD施工图自动生成4D数字孪生，注入物理属性，支持机器人仿真

---

## 🎯 三大核心步骤

```
❌ 理解层：AI模型理解建筑语义
    ↓
❌ 仿真层：物理引擎验证机器人行为
    ↓
❌ 执行层：机器人控制接口
```

---

## Step 1: 理解层 - AI模型理解建筑语义

### 目标
从CAD图纸自动识别：
- 房间功能（卧室/客厅/厨房/卫生间/阳台）
- 空间关系（相邻、包含、连通）
- 建筑构件（墙体类型、门窗位置）
- 材质标注（从文字标注提取）

### 实现方案

#### 1.1 房间分割算法

```python
# algorithms/room_segmentation.py
import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import polygonize

def segment_rooms(walls: list[LineString]) -> list[Polygon]:
    """
    从墙体线段分割出房间多边形

    输入：墙体线段列表（从DWG提取）
    输出：房间多边形列表
    """
    # 1. 合并线段为闭合环
    merged = shapely.ops.linemerge(walls)

    # 2. 构建多边形
    rooms = list(polygonize(merged))

    return rooms
```

#### 1.2 房间功能分类模型

**方案A：规则引擎（简单快速）**
```python
# algorithms/room_classifier.py

def classify_room(room: Polygon, annotations: list) -> str:
    """
    基于规则分类房间功能
    """
    # 规则1：面积判断
    area = room.area

    # 规则2：长宽比判断
    bounds = room.bounds
    aspect_ratio = (bounds[2] - bounds[0]) / (bounds[3] - bounds[1])

    # 规则3：设备特征
    has_toilet = any('马桶' in a for a in annotations)
    has_sink = any('洗手盆' in a for a in annotations)
    has_stove = any('灶' in a for a in annotations)
    has_bed = any('床' in a for a in annotations)

    # 分类规则
    if has_toilet or has_sink:
        return '卫生间'
    elif has_stove:
        return '厨房'
    elif has_bed:
        return '卧室'
    elif area > 20 and aspect_ratio < 2:
        return '客厅'
    elif area < 10:
        return '阳台' if aspect_ratio > 3 else '储物间'
    else:
        return '卧室'  # 默认
```

**方案B：深度学习模型（更准确）**
```python
# models/room_classifier_nn.py
import torch
import torch.nn as nn

class RoomClassifier(nn.Module):
    """
    基于房间几何和设备特征的分类网络
    """
    def __init__(self):
        super().__init__()
        # 输入：[面积, 周长, 长宽比, 设备特征(10维)]
        self.fc = nn.Sequential(
            nn.Linear(13, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 6),  # 6类房间
        )

    def forward(self, x):
        return self.fc(x)

# 训练数据：从已标注的施工图生成
# 标签：客厅、卧室、厨房、卫生间、阳台、储物间
```

#### 1.3 空间拓扑关系

```python
# algorithms/spatial_topology.py
from shapely.geometry import Polygon

def build_topology(rooms: list[Polygon]) -> dict:
    """
    构建房间拓扑关系图
    """
    topology = {
        'adjacent': [],  # 相邻关系
        'connected': [],  # 连通关系（有门）
        'contains': []    # 包含关系
    }

    for i, room_a in enumerate(rooms):
        for j, room_b in enumerate(rooms):
            if i >= j:
                continue

            # 相邻：共享边界
            if room_a.touches(room_b):
                topology['adjacent'].append({
                    'rooms': [i, j],
                    'boundary': room_a.intersection(room_b)
                })

            # 包含：一个在另一个内部
            if room_a.contains(room_b):
                topology['contains'].append({
                    'outer': i,
                    'inner': j
                })

    return topology
```

#### 1.4 材质标注提取

```python
# algorithms/material_extraction.py
import re

def extract_materials(annotations: list[str]) -> dict:
    """
    从CAD标注提取材质信息
    """
    materials = {}

    # 地面材质
    floor_patterns = {
        '瓷砖': r'(\d+×\d+)瓷砖|地砖',
        '木地板': r'木地板|复合地板|实木地板',
        '大理石': r'大理石|石材',
        '地毯': r'地毯',
    }

    # 墙面材质
    wall_patterns = {
        '乳胶漆': r'乳胶漆|涂料',
        '墙纸': r'墙纸|壁纸',
        '木饰面': r'木饰面|护墙板',
        '瓷砖': r'墙砖|瓷片',
    }

    for text in annotations:
        for material, pattern in {**floor_patterns, **wall_patterns}.items():
            if re.search(pattern, text):
                materials[material] = text

    return materials
```

### 需要的工具/库

| 库 | 用途 | 安装命令 |
|-----|------|----------|
| **shapely** | 几何运算 | `pip install shapely` |
| **networkx** | 拓扑图 | `pip install networkx` |
| **torch** | 深度学习 | `pip install torch` |
| **ezdxf** | DWG解析 | `pip install ezdxf` |

### 输出数据结构

```json
{
  "rooms": [
    {
      "id": "room-001",
      "type": "客厅",
      "geometry": {
        "polygon": [[x1,y1], [x2,y2], ...],
        "area": 25.5,
        "perimeter": 20.3,
        "centroid": [5.2, 3.1]
      },
      "materials": {
        "floor": "800×800瓷砖",
        "wall": "乳胶漆",
        "ceiling": "石膏板吊顶"
      },
      "adjacent_to": ["room-002", "room-003"],
      "doors": ["door-001"],
      "windows": ["window-001", "window-002"]
    }
  ],
  "topology": {
    "adjacent": [["room-001", "room-002"], ...],
    "connected": [["room-001", "room-002", "door-001"], ...]
  }
}
```

---

## Step 2: 仿真层 - 物理引擎验证

### 目标
在虚拟环境中验证机器人行为：
- 抓取力是否足够
- 搬运路径是否可行
- 安装精度是否达标
- 碰撞是否会发生

### 实现方案

#### 2.1 选择仿真引擎

| 引擎 | 优势 | 适用场景 |
|------|------|----------|
| **MuJoCo** | 快速、精确、免费 | 抓取、搬运仿真 |
| **Isaac Sim** | NVIDIA支持、逼真渲染 | 大规模仿真 |
| **PyBullet** | 开源、易用 | 快速原型验证 |
| **Gazebo** | ROS集成 | 机器人开发 |

**推荐：MuJoCo（快速精确）+ Isaac Sim（逼真渲染）**

#### 2.2 MuJoCo建筑模型

```xml
<!-- models/building.xml -->
<mujoco model="apartment">
  <option gravity="0 0 -9.81"/>

  <asset>
    <!-- 地面 -->
    <texture name="floor_tex" type="2d" file="floor.png"/>
    <material name="floor_mat" texture="floor_tex"/>

    <!-- 墙体材质 -->
    <material name="wall_mat" rgba="0.9 0.9 0.9 1"/>
  </asset>

  <worldbody>
    <!-- 地面 -->
    <geom name="floor" type="plane" size="10 10 0.1" material="floor_mat">
      <friction>0.5 0.5 0.5</friction>
    </geom>

    <!-- 墙体 -->
    <body name="wall_001" pos="0 0 1.5">
      <geom type="box" size="0.12 3 1.5" mass="2160">
        <friction>0.6 0.6 0.6</friction>
      </geom>
    </body>

    <!-- 瓷砖（可抓取对象） -->
    <body name="tile_001" pos="2 2 0.006">
      <joint name="tile_joint" type="free"/>
      <geom type="box" size="0.4 0.4 0.006" mass="17.7">
        <friction>0.4 0.4 0.4</friction>
      </geom>
    </body>

    <!-- 机器人 -->
    <body name="robot" pos="1 1 0">
      <joint name="robot_x" type="slide" axis="1 0 0"/>
      <joint name="robot_y" type="slide" axis="0 1 0"/>
      <joint name="robot_z" type="slide" axis="0 0 1"/>

      <!-- 机械臂 -->
      <body name="arm">
        <joint name="arm_pitch" type="hinge" axis="0 1 0"/>
        <geom type="capsule" size="0.05 0.3" mass="5"/>
      </body>

      <!-- 吸盘 -->
      <body name="gripper" pos="0 0 0.5">
        <geom name="suction" type="sphere" size="0.05" mass="0.5"/>
      </body>
    </body>
  </worldbody>

  <actuator>
    <motor name="robot_x_motor" joint="robot_x" gear="100"/>
    <motor name="robot_y_motor" joint="robot_y" gear="100"/>
    <motor name="robot_z_motor" joint="robot_z" gear="100"/>
    <motor name="arm_motor" joint="arm_pitch" gear="50"/>
  </actuator>
</mujoco>
```

#### 2.3 仿真控制代码

```python
# simulation/mujoco_sim.py
import mujoco
import numpy as np

class BuildingSimulator:
    def __init__(self, model_path: str):
        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)

    def reset(self):
        """重置仿真"""
        mujoco.mj_resetData(self.model, self.data)

    def step(self, action: np.ndarray):
        """执行一步仿真"""
        self.data.ctrl[:] = action
        mujoco.mj_step(self.model, self.data)
        return self.get_observation()

    def get_observation(self) -> dict:
        """获取观测"""
        return {
            'robot_pos': self.data.qpos[:3].copy(),
            'robot_vel': self.data.qvel[:3].copy(),
            'tile_pos': self.data.qpos[6:9].copy(),
            'gripper_force': self.get_contact_force('suction', 'tile_001')
        }

    def get_contact_force(self, geom1: str, geom2: str) -> np.ndarray:
        """获取接触力"""
        for contact in self.data.contact:
            if contact.geom1 == self.model.geom(geom1).id and \
               contact.geom2 == self.model.geom(geom2).id:
                return contact.force
        return np.zeros(3)

    def check_grasp_success(self) -> bool:
        """检查抓取是否成功"""
        tile_z = self.data.qpos[8]  # 瓷砖z坐标
        return tile_z > 0.1  # 抬起10cm以上

    def run_episode(self, policy, max_steps=1000):
        """运行一个回合"""
        self.reset()
        for step in range(max_steps):
            obs = self.get_observation()
            action = policy(obs)
            self.step(action)

            if self.check_grasp_success():
                return {'success': True, 'steps': step}

        return {'success': False, 'steps': max_steps}
```

#### 2.4 抓取策略验证

```python
# simulation/grasp_validation.py

def validate_grasp_force(material: str, mass: float) -> dict:
    """
    验证抓取力是否足够
    """
    # 摩擦系数表
    friction_map = {
        '瓷砖': 0.4,
        '木地板': 0.5,
        '大理石': 0.4,
        '玻璃': 0.2
    }

    mu = friction_map.get(material, 0.4)
    g = 9.8

    # 最小抓取力
    F_min = mass * g / (2 * mu)

    # 安全抓取力（2倍安全系数）
    F_safe = F_min * 2

    # 灵巧手最大指尖力
    F_max_finger = 20  # N

    return {
        'material': material,
        'mass_kg': mass,
        'friction_coefficient': mu,
        'min_grasp_force_N': F_min,
        'safe_grasp_force_N': F_safe,
        'feasible_with_dexterous_hand': F_safe <= F_max_finger,
        'recommended_method': '吸盘' if F_safe > F_max_finger else '灵巧手'
    }

# 示例
result = validate_grasp_force('瓷砖', 17.7)
# 输出：
# {
#   'material': '瓷砖',
#   'mass_kg': 17.7,
#   'friction_coefficient': 0.4,
#   'min_grasp_force_N': 216.8,
#   'safe_grasp_force_N': 433.6,
#   'feasible_with_dexterous_hand': False,
#   'recommended_method': '吸盘'
# }
```

### 需要的工具/库

| 库 | 用途 | 安装命令 |
|-----|------|----------|
| **mujoco** | 物理仿真 | `pip install mujoco` |
| **isaacsim** | 高保真仿真 | 从NVIDIA下载 |
| **pybullet** | 快速原型 | `pip install pybullet` |

---

## Step 3: 执行层 - 机器人控制接口

### 目标
实现机器人控制接口：
- 感知：获取环境信息
- 决策：规划动作
- 执行：控制机器人

### 实现方案

#### 3.1 ROS2控制架构

```python
# control/ros2_interface.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, Twist
from sensor_msgs.msg import Image, PointCloud2
from std_msgs.msg import Float32

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')

        # 发布器
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.gripper_pub = self.create_publisher(Float32, '/gripper_force', 10)

        # 订阅器
        self.pose_sub = self.create_subscription(
            Pose, '/robot_pose', self.pose_callback, 10)
        self.image_sub = self.create_subscription(
            Image, '/camera/image', self.image_callback, 10)
        self.pointcloud_sub = self.create_subscription(
            PointCloud2, '/camera/pointcloud', self.pointcloud_callback, 10)

        # 状态
        self.current_pose = None
        self.current_image = None
        self.current_pointcloud = None

    def pose_callback(self, msg: Pose):
        self.current_pose = msg

    def image_callback(self, msg: Image):
        self.current_image = msg

    def pointcloud_callback(self, msg: PointCloud2):
        self.current_pointcloud = msg

    def move_to(self, target_pose: Pose):
        """移动到目标位置"""
        # TODO: 实现路径规划
        pass

    def grasp(self, force: float):
        """执行抓取"""
        msg = Float32()
        msg.data = force
        self.gripper_pub.publish(msg)
```

#### 3.2 感知模块

```python
# perception/object_detection.py
import torch
from transformers import AutoModelForObjectDetection

class ObjectDetector:
    def __init__(self, model_name='facebook/detr-resnet-50'):
        self.model = AutoModelForObjectDetection.from_pretrained(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def detect(self, image: np.ndarray) -> list[dict]:
        """
        检测图像中的建筑对象

        返回：[
            {'label': '瓷砖', 'bbox': [x1,y1,x2,y2], 'score': 0.95},
            {'label': '木地板', 'bbox': [x1,y1,x2,y2], 'score': 0.89},
            ...
        ]
        """
        # 预处理
        inputs = self.preprocessor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # 推理
        outputs = self.model(**inputs)

        # 后处理
        results = self.postprocess(outputs, image.shape)
        return results
```

#### 3.3 路径规划

```python
# planning/path_planner.py
import numpy as np
from scipy.spatial import KDTree

class PathPlanner:
    def __init__(self, obstacles: list[np.ndarray]):
        """
        obstacles: 障碍物点云列表
        """
        self.obstacles = np.vstack(obstacles)
        self.kdtree = KDTree(self.obstacles)

    def plan(self, start: np.ndarray, goal: np.ndarray,
             safe_distance: float = 0.5) -> list[np.ndarray]:
        """
        规划从start到goal的无碰撞路径

        使用RRT*算法
        """
        path = [start]
        current = start.copy()

        while np.linalg.norm(current - goal) > 0.1:
            # 采样随机点
            if np.random.random() < 0.1:
                target = goal  # 偏向目标
            else:
                target = self.sample_random_point()

            # 找最近节点
            nearest = self.find_nearest(path, target)

            # 扩展
            new_point = self.steer(nearest, target, step_size=0.5)

            # 碰撞检测
            if self.is_collision_free(nearest, new_point, safe_distance):
                path.append(new_point)
                current = new_point

        path.append(goal)
        return self.smooth_path(path)

    def is_collision_free(self, p1: np.ndarray, p2: np.ndarray,
                          safe_distance: float) -> bool:
        """检查路径是否无碰撞"""
        # 在p1-p2连线上采样
        for t in np.linspace(0, 1, 20):
            point = p1 + t * (p2 - p1)
            dist, _ = self.kdtree.query(point)
            if dist < safe_distance:
                return False
        return True
```

#### 3.4 任务编排

```python
# control/task_orchestrator.py
from enum import Enum
from typing import Callable

class TaskState(Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'

class Task:
    def __init__(self, name: str, action: Callable, dependencies: list['Task'] = None):
        self.name = name
        self.action = action
        self.dependencies = dependencies or []
        self.state = TaskState.PENDING

class TaskOrchestrator:
    def __init__(self):
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def run(self):
        """执行所有任务"""
        while True:
            # 找可执行任务
            ready_tasks = [
                t for t in self.tasks
                if t.state == TaskState.PENDING
                and all(d.state == TaskState.SUCCESS for d in t.dependencies)
            ]

            if not ready_tasks:
                if all(t.state in [TaskState.SUCCESS, TaskState.FAILED] for t in self.tasks):
                    break  # 全部完成
                continue

            # 执行任务
            for task in ready_tasks:
                task.state = TaskState.RUNNING
                try:
                    task.action()
                    task.state = TaskState.SUCCESS
                except Exception as e:
                    task.state = TaskState.FAILED
                    print(f"Task {task.name} failed: {e}")

# 使用示例
orchestrator = TaskOrchestrator()

# 定义任务
scan_task = Task('scan_room', lambda: robot.scan())
detect_task = Task('detect_objects', lambda: robot.detect(), [scan_task])
plan_task = Task('plan_path', lambda: robot.plan(), [detect_task])
grasp_task = Task('grasp_tile', lambda: robot.grasp(), [plan_task])
place_task = Task('place_tile', lambda: robot.place(), [grasp_task])

orchestrator.add_task(scan_task)
orchestrator.add_task(detect_task)
orchestrator.add_task(plan_task)
orchestrator.add_task(grasp_task)
orchestrator.add_task(place_task)

orchestrator.run()
```

### 需要的工具/库

| 库 | 用途 | 安装命令 |
|-----|------|----------|
| **rclpy** | ROS2 Python | 随ROS2安装 |
| **transformers** | 目标检测 | `pip install transformers` |
| **scipy** | 路径规划 | `pip install scipy` |

---

## 📋 实施计划

### Phase 1: 理解层（3周）

| 周 | 任务 | 产出 |
|----|------|------|
| W1 | DWG解析 + 房间分割 | 几何数据提取 |
| W2 | 房间分类 + 拓扑关系 | 语义地图 |
| W3 | 材质提取 + 数据整合 | L2语义层完成 |

### Phase 2: 仿真层（4周）

| 周 | 任务 | 产出 |
|----|------|------|
| W4 | MuJoCo环境搭建 | 基硎仿真环境 |
| W5 | 建筑模型导入 | 虚拟建筑 |
| W6 | 机器人模型 + 抓取仿真 | 抓取验证 |
| W7 | Isaac Sim集成（可选） | 高保真仿真 |

### Phase 3: 执行层（4周）

| 周 | 任务 | 产出 |
|----|------|------|
| W8 | ROS2接口 + 感知模块 | 机器人感知 |
| W9 | 路径规划 + 运动控制 | 机器人控制 |
| W10 | 任务编排 + 异常处理 | 自动化流程 |
| W11 | 系统集成 + 测试 | 完整系统 |

---

## 🚀 快速启动

### 立即可做的

```bash
# 1. 安装依赖
pip install ezdxf shapely networkx mujoco scipy

# 2. 测试DWG解析
python -c "import ezdxf; print('ezdxf OK')"

# 3. 测试MuJoCo
python -c "import mujoco; print('mujoco OK')"
```

### 第一周任务

1. **DWG解析脚本**
2. **房间分割算法**
3. **几何数据输出**

---

_创建时间：2026-04-10_
_预计完成：11周_
