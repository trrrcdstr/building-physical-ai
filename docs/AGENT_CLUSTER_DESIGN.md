# 智能体集群架构设计

> 世界模型构建系统 - 多智能体协作框架

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    建筑物理AI世界模型系统                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 🧠 建筑认知主智能体                        │   │
│  │                    (Master Agent)                         │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ 任务规划 │ 意图理解 │ 智能体调度 │ 结果融合          │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│              ┌───────────────┼───────────────┐                   │
│              ▼               ▼               ▼                   │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │
│  │🗺️ 空间结构    │ │🖼️ 视觉语义    │ │⚖️ 物理规则    │          │
│  │   Agent       │ │   Agent       │ │   Agent       │          │
│  │               │ │               │ │               │          │
│  │ CAD解析       │ │ VR效果图      │ │ 建筑规范      │          │
│  │ Block/Road    │ │ Function/Obj  │ │ Harness层     │          │
│  └───────────────┘ └───────────────┘ └───────────────┘          │
│              │               │               │                   │
│              └───────────────┼───────────────┘                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  🌳 园林景观智能体                         │   │
│  │              (Landscape Agent)                            │   │
│  │   地形分析 │ 植物配置 │ 室外空间建模                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   世界模型数据层                           │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │   │
│  │  │ Block层 │ │ Road层  │ │Function │ │ Object层│         │   │
│  │  │ 空间骨架│ │ 路网拓扑│ │ 功能标签│ │ 物体信息│         │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 👥 智能体角色定义

### 1. 🧠 建筑认知主智能体 (Master Agent)

| 属性 | 描述 |
|------|------|
| **角色定位** | 总指挥，负责整体协调 |
| **核心职责** | 任务规划、意图理解、智能体调度、结果融合 |
| **输入** | 自然语言指令 / CAD文件 / VR数据 |
| **输出** | 可执行任务蓝图 + 协作指令 |
| **调度对象** | 空间结构/视觉语义/物理规则/园林景观 |

**核心能力:**
```python
class MasterAgent:
    def __init__(self):
        self.spatial_agent = SpatialStructureAgent()
        self.visual_agent = VisualSemanticAgent()
        self.physics_agent = PhysicsRuleAgent()
        self.landscape_agent = LandscapeAgent()
    
    def process(self, instruction: str):
        # 1. 意图理解
        intent = self.understand_intent(instruction)
        
        # 2. 任务分解
        tasks = self.decompose_tasks(intent)
        
        # 3. 智能体调度
        results = self.dispatch_agents(tasks)
        
        # 4. 结果融合
        world_model = self.merge_results(results)
        
        return world_model
```

---

### 2. 🗺️ 空间结构智能体 (Spatial Agent)

| 属性 | 描述 |
|------|------|
| **角色定位** | 测绘师，负责空间骨架构建 |
| **核心职责** | CAD解析、几何计算、Block/Road层建模 |
| **输入** | DXF/DWG文件 |
| **输出** | 空间拓扑地图 + 通行路网 |
| **依赖** | ezdxf, Shapely, NetworkX |

**核心能力:**
```python
class SpatialStructureAgent:
    def parse_cad(self, dxf_path: str) -> SpatialModel:
        """解析CAD图纸"""
        # 1. 图层识别
        layers = self.recognize_layers(dxf_path)
        
        # 2. 墙体提取
        walls = self.extract_walls(layers)
        
        # 3. Block层构建
        blocks = self.build_blocks(walls)
        
        # 4. Road层构建
        roads = self.build_roads(blocks, doors)
        
        return SpatialModel(blocks=blocks, roads=roads)
```

---

### 3. 🖼️ 视觉语义智能体 (Visual Agent)

| 属性 | 描述 |
|------|------|
| **角色定位** | 室内设计师，负责场景理解 |
| **核心职责** | VR效果图解析、语义分割、Function/Object层建模 |
| **输入** | VR全景图 / 效果图 / 3D模型 |
| **输出** | 语义地图 + 物体信息 |
| **依赖** | OpenCV, PIL, TensorFlow/PyTorch |

**核心能力:**
```python
class VisualSemanticAgent:
    def analyze_vr(self, vr_image_path: str) -> SemanticModel:
        """分析VR效果图"""
        # 1. 图像预处理
        image = self.preprocess(vr_image_path)
        
        # 2. 场景分类
        scene_type = self.classify_scene(image)
        
        # 3. 物体检测
        objects = self.detect_objects(image)
        
        # 4. 功能分区
        functions = self.segment_functions(image)
        
        return SemanticModel(scene_type, objects, functions)
```

---

### 4. ⚖️ 物理规则智能体 (Physics Agent)

| 属性 | 描述 |
|------|------|
| **角色定位** | 监理工程师，负责安全约束 |
| **核心职责** | 规范解读、物理属性映射、Harness层建模 |
| **输入** | 材料表 / 建筑规范 / 操作指令 |
| **输出** | 安全边界 + 物理规则库 |
| **依赖** | MATERIAL_PROPERTIES.json, BUILDING_RULES.json |

**核心能力:**
```python
class PhysicsRuleAgent:
    def validate_operation(self, operation: Operation) -> ValidationResult:
        """验证操作安全性"""
        # 1. 检查墙体类型
        wall_check = self.check_wall_type(operation.wall_id)
        
        # 2. 检查管线位置
        pipe_check = self.check_pipe_location(operation.position)
        
        # 3. 检查物理约束
        physics_check = self.check_physics_constraints(operation)
        
        # 4. 返回结果
        return ValidationResult(
            allowed=wall_check.allowed and pipe_check.safe,
            warnings=wall_check.warnings + pipe_check.warnings
        )
```

---

### 5. 🌳 园林景观智能体 (Landscape Agent)

| 属性 | 描述 |
|------|------|
| **角色定位** | 景观设计师，负责室外环境 |
| **核心职责** | 地形分析、植物配置、室外空间建模 |
| **输入** | 园林规划图 / 景观设计 / 地形数据 |
| **输出** | 室外3D模型 + 交互规则 |
| **依赖** | 园林知识库, 高斯Splatting |

**核心能力:**
```python
class LandscapeAgent:
    def analyze_landscape(self, plan_path: str) -> LandscapeModel:
        """分析园林规划"""
        # 1. 地形提取
        terrain = self.extract_terrain(plan_path)
        
        # 2. 植被识别
        vegetation = self.identify_vegetation(plan_path)
        
        # 3. 道路网络
        paths = self.extract_paths(plan_path)
        
        # 4. 景观要素
        features = self.extract_features(plan_path)
        
        return LandscapeModel(terrain, vegetation, paths, features)
```

---

## 🔄 协作流程

### 场景1: 构建新世界模型

```
用户指令: "解析这套CAD图纸，构建世界模型"

┌──────────────────────────────────────────────────────────────┐
│ 1. Master Agent 接收指令                                      │
│    ↓ 意图理解: BUILD_WORLD_MODEL                              │
│    ↓ 任务分解: [PARSE_CAD, BUILD_ROAD, ASSIGN_FUNCTIONS]     │
├──────────────────────────────────────────────────────────────┤
│ 2. dispatch → Spatial Agent                                   │
│    输入: CAD文件路径                                          │
│    处理: 图层识别 → 墙体提取 → Block构建 → Road构建           │
│    输出: SpatialModel { blocks: 5, roads: 3 }                │
├──────────────────────────────────────────────────────────────┤
│ 3. dispatch → Visual Agent                                    │
│    输入: VR效果图 (如果有)                                    │
│    处理: 场景分类 → 物体检测 → 功能分区                       │
│    输出: SemanticModel { functions: 5, objects: 12 }         │
├──────────────────────────────────────────────────────────────┤
│ 4. dispatch → Physics Agent                                   │
│    输入: 材料表 + 建筑规范                                    │
│    处理: 属性映射 → 规则加载 → 约束生成                       │
│    输出: PhysicsModel { materials: 22, rules: 16 }           │
├──────────────────────────────────────────────────────────────┤
│ 5. Master Agent 融合结果                                      │
│    处理: 数据对齐 → 坐标统一 → 索引建立                       │
│    输出: WorldModel { 4层完整数据 }                          │
└──────────────────────────────────────────────────────────────┘
```

### 场景2: 执行机器人操作

```
用户指令: "在东墙钻一个8mm的孔"

┌──────────────────────────────────────────────────────────────┐
│ 1. Master Agent 接收指令                                      │
│    ↓ 意图理解: DRILL_OPERATION                                │
│    ↓ 任务分解: [CHECK_WALL, CHECK_PIPES, PLAN_PATH]          │
├──────────────────────────────────────────────────────────────┤
│ 2. dispatch → Spatial Agent                                   │
│    查询: "东墙在哪里？"                                        │
│    输出: { wall_id: "east_wall", position: (5000, 3000) }    │
├──────────────────────────────────────────────────────────────┤
│ 3. dispatch → Physics Agent                                   │
│    查询: "能钻孔吗？"                                          │
│    输出: { allowed: true, warnings: ["注意管线"] }           │
├──────────────────────────────────────────────────────────────┤
│ 4. dispatch → Visual Agent                                    │
│    查询: "附近有什么物体？"                                    │
│    输出: { objects: ["沙发", "茶几"], distance: [2.5, 3.1] } │
├──────────────────────────────────────────────────────────────┤
│ 5. Master Agent 生成执行方案                                  │
│    输出: {                                                    │
│      "steps": [                                               │
│        "1. 移动到东墙位置 (5000, 3000)",                       │
│        "2. 使用探测仪确认管线位置",                            │
│        "3. 安装8mm钻头",                                       │
│        "4. 钻孔深度≤80mm",                                     │
│        "5. 清理碎屑"                                           │
│      ],                                                       │
│      "risk_level": "low",                                     │
│      "estimated_time": "3分钟"                                │
│    }                                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 智能体能力矩阵

| 能力 | Master | Spatial | Visual | Physics | Landscape |
|------|:------:|:-------:|:------:|:-------:|:---------:|
| 意图理解 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 任务规划 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 智能体调度 | ✅ | ❌ | ❌ | ❌ | ❌ |
| CAD解析 | ❌ | ✅ | ❌ | ❌ | ✅ |
| 几何计算 | ❌ | ✅ | ❌ | ❌ | ✅ |
| 图像理解 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 语义分割 | ❌ | ❌ | ✅ | ❌ | ❌ |
| 规则推理 | ❌ | ❌ | ❌ | ✅ | ❌ |
| 物理仿真 | ❌ | ❌ | ❌ | ✅ | ❌ |
| 地形分析 | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🔧 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 智能体框架 | LangChain / 自研 | 多智能体协作 |
| CAD解析 | ezdxf, Shapely | DXF解析, 几何计算 |
| 图像处理 | OpenCV, PIL | 图像预处理 |
| 深度学习 | PyTorch, TensorFlow | 物体检测, 语义分割 |
| 图数据库 | NetworkX | 路网拓扑 |
| API框架 | FastAPI | RESTful接口 |
| 3D渲染 | Three.js, Gaussian Splatting | 可视化 |

---

## 📅 分阶段落地路线图

### Phase 1: 基础框架 (Week 1-2)

| 任务 | 交付物 |
|------|--------|
| Master Agent核心逻辑 | 任务规划 + 调度框架 |
| Spatial Agent CAD解析 | DXF → 四层模型 |
| 智能体通信协议 | JSON-RPC / HTTP |

### Phase 2: 核心能力 (Week 3-4)

| 任务 | 交付物 |
|------|--------|
| Physics Agent规则库 | 材料属性 + 建筑规范 |
| Visual Agent基础 | 场景分类 + 物体检测 |
| 协作流程验证 | 端到端测试 |

### Phase 3: 能力增强 (Week 5-6)

| 任务 | 交付物 |
|------|--------|
| Landscape Agent | 园林场景支持 |
| 多模态融合 | CAD + VR 对齐 |
| 性能优化 | 并行处理 + 缓存 |

### Phase 4: 生产部署 (Week 7-8)

| 任务 | 交付物 |
|------|--------|
| API网关 | 统一入口 + 负载均衡 |
| 监控告警 | 性能指标 + 异常检测 |
| 文档完善 | API文档 + 部署指南 |

---

_创建时间: 2026-04-21_
_版本: v1.0_
