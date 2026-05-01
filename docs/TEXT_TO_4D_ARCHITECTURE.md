# 文本→4D动态场景生成架构

## 核心目标

**输入**: 文本描述（如"客厅里有人在沙发上喝茶"）
**输出**: 4D动态场景（3D几何 + 时间维度动画）

---

## 技术路线：三层融合

```
┌─────────────────────────────────────────────────────────────┐
│                    文本→4D 生成管线                          │
├─────────────────────────────────────────────────────────────┤
│  L1: 文本理解层                                              │
│  ├─ 文本 → 场景描述（LLM）                                   │
│  ├─ 场景描述 → 物体列表 + 关系 + 动作                        │
│  └─ 输出: {objects, relations, actions, duration}           │
├─────────────────────────────────────────────────────────────┤
│  L2: 3D几何生成层（3D Gaussian Splatting）                   │
│  ├─ 物体列表 → 检索相似VR/CAD场景                            │
│  ├─ 相似场景 → 高斯泼斯参数初始化                            │
│  ├─ CAD几何约束 → 精修高斯中心位置                           │
│  └─ 输出: {gaussians: [μ, Σ, color, opacity]}               │
├─────────────────────────────────────────────────────────────┤
│  L3: 4D动态层（时间维度）                                     │
│  ├─ 动作序列 → 物体轨迹规划                                  │
│  ├─ 轨迹 → 高斯参数时变函数 μ(t), Σ(t)                       │
│  ├─ 物理仿真 → 碰撞检测、遮挡处理                            │
│  └─ 输出: {gaussians(t) | t ∈ [0, T]}                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 数据资产映射

| 数据源 | 数量 | 在管线中的作用 |
|--------|------|----------------|
| **VR全景** | 709 | 训练高斯泼斯的视角图片源 |
| **CAD几何** | 76 | 几何约束（墙/门/窗位置） |
| **建筑体块** | 151 | 语义分割标签 |
| **渲染图** | 497 | 风格迁移参考 |
| **园林场景** | 18 | 室外场景扩展 |

---

## 核心技术模块

### 1. 3D Gaussian Splatting 训练

```python
# 高斯泼斯表示
class GaussianSplatting:
    """
    每个高斯由以下参数定义:
    - μ (position): 3D中心位置
    - Σ (covariance): 3D协方差矩阵（控制形状/方向）
    - color: RGB颜色（或球谐系数）
    - opacity: 不透明度
    """
    def __init__(self):
        self.means = None      # [N, 3]
        self.covariances = None # [N, 3, 3]
        self.colors = None      # [N, 3] or [N, K, 3] for SH
        self.opacities = None   # [N, 1]
    
    def render(self, camera_pose):
        """将3D高斯投影到2D并渲染"""
        pass
```

**训练数据来源**:
- VR全景 → 提取多视角帧（等距圆柱投影 → 透视投影）
- CAD几何 → 提供深度先验（监督训练）

### 2. 文本→场景解析

```python
def text_to_scene(text: str) -> SceneDescription:
    """
    输入: "客厅里有人在沙发上喝茶"
    输出: {
        "room": "客厅",
        "objects": [
            {"type": "person", "position": "on_sofa", "action": "drinking_tea"},
            {"type": "sofa", "position": "center"},
            {"type": "cup", "position": "hand"}
        ],
        "relations": [
            {"subject": "person", "relation": "on", "object": "sofa"},
            {"subject": "person", "relation": "holding", "object": "cup"}
        ],
        "actions": [
            {"actor": "person", "action": "drink", "duration": [0, 3]}
        ]
    }
    """
    pass
```

### 3. 场景检索与初始化

```python
def retrieve_similar_scene(scene_desc: SceneDescription) -> GaussianSplatting:
    """
    从VR/CAD数据库检索相似场景，初始化高斯参数
    """
    # 1. 向量检索相似VR
    similar_vrs = vector_search(scene_desc.room, top_k=5)
    
    # 2. 加载对应的高斯模型（预训练）
    gaussians = load_pretrained_gaussians(similar_vrs)
    
    # 3. CAD几何约束精修
    cad_constraints = load_cad_geometry(scene_desc.room)
    gaussians = refine_with_cad(gaussians, cad_constraints)
    
    return gaussians
```

### 4. 4D动态生成

```python
def add_temporal_dimension(
    gaussians: GaussianSplatting,
    actions: List[Action]
) -> GaussianSplatting4D:
    """
    为静态场景添加时间维度
    """
    # 1. 轨迹规划
    trajectories = plan_trajectories(actions, gaussians)
    
    # 2. 物理仿真
    physics_sim = PhysicsSimulator(gaussians)
    
    # 3. 时变高斯参数
    def gaussian_at_time(t):
        g = gaussians.copy()
        for traj in trajectories:
            # 更新位置
            g.means[traj.object_id] = traj.position_at(t)
            # 更新协方差（形变）
            g.covariances[traj.object_id] = traj.deformation_at(t)
        return g
    
    return GaussianSplatting4D(gaussian_at_time)
```

---

## 实施路线图

### Phase 1: 数据准备（2周）

| 任务 | 输入 | 输出 |
|------|------|------|
| VR全景帧提取 | 709个VR链接 | ~100K张视角图片 |
| 相机位姿估计 | 视角图片 | COLMAP模型 |
| CAD几何解析 | 76个DWG | 精确几何约束 |
| 语义标注 | 建筑体块 | 物体类别标签 |

### Phase 2: 3D高斯训练（3周）

| 任务 | 方法 |
|------|------|
| 单场景训练 | 3DGS + CAD深度监督 |
| 跨场景泛化 | 潜在空间插值 |
| 模型压缩 | 剪枝 + 量化 |

### Phase 3: 文本接口（2周）

| 任务 | 方法 |
|------|------|
| 场景理解 | LLM (GPT-4/Claude) |
| 向量检索 | CLIP embedding |
| 场景生成 | 检索 + 插值 + 精修 |

### Phase 4: 4D动态（3周）

| 任务 | 方法 |
|------|------|
| 动作库构建 | 动捕数据 / 视频提取 |
| 轨迹规划 | RRT* + CAD约束 |
| 物理仿真 | MuJoCo / PhysX |
| 渲染优化 | 实时高斯渲染 |

---

## 关键创新点

### 1. CAD几何约束的高斯泼斯

传统3DGS只用图片监督，我们加入CAD几何约束：

```
Loss = L_image + λ₁ * L_depth + λ₂ * L_semantic

L_depth = ||D_pred - D_cad||²  # CAD深度监督
L_semantic = CrossEntropy(S_pred, S_cad)  # CAD语义监督
```

### 2. 建筑体块语义先验

利用151个门/窗/墙的精确位置，作为高斯中心的硬约束：

```python
# 门/窗高斯中心必须落在CAD定义的平面上
for obj in building_objects:
    if obj.type in ['door', 'window']:
        gaussians.means[obj.gaussian_id] = project_to_plane(
            gaussians.means[obj.gaussian_id],
            obj.plane_equation
        )
```

### 3. 4D物理一致性

动态场景必须满足物理约束：

```python
# 碰撞检测
for t in timeline:
    if check_collision(gaussians_at(t)):
        resolve_collision(gaussians_at(t))

# 质量守恒（流体/烟雾）
if has_fluid:
    enforce_mass_conservation(gaussians_at(t))
```

---

## 技术栈

| 模块 | 工具 |
|------|------|
| 3D高斯泼斯 | [GaussianSplatting](https://github.com/graphdeco-inria/gaussian-splatting) |
| 相机估计 | COLMAP |
| 深度估计 | Depth-Anything / MiDaS |
| 文本理解 | GPT-4 / Claude |
| 向量检索 | FAISS / Milvus |
| 物理仿真 | MuJoCo / PhysX |
| 渲染 | CUDA高斯渲染器 |

---

## 预期成果

1. **文本→3D静态场景**: 输入"现代简约客厅"，输出可渲染的3D高斯模型
2. **文本→4D动态场景**: 输入"人在客厅喝茶"，输出带动画的4D场景
3. **CAD精确约束**: 生成的门/窗/墙位置与施工图一致
4. **实时渲染**: 30+ FPS 实时渲染4D场景

---

## 商业价值

| 应用场景 | 价值 |
|----------|------|
| 装修设计预览 | 客户输入需求→实时生成效果图 |
| 施工模拟 | 4D施工过程可视化 |
| 智能家居 | AI理解空间→生成交互场景 |
| 游戏/元宇宙 | 文本生成游戏场景 |
| 机器人训练 | 生成多样化训练场景 |

---

_创建时间: 2026-04-16_
