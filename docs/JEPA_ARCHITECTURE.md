# JEPA 世界模型架构文档
## 基于 Yann LeCun 分层联合嵌入预测架构

---

## 1. 核心思想

**JEPA（Joint Embedding Predictive Architecture）** 不是在像素空间预测未来，
而是在**抽象表示空间**中预测下一个状态。

```
传统方法（像素级预测）：
  观测 → 模型 → 逐像素重建 → 模糊/不稳定

JEPA（表示空间预测）：
  观测 → 编码器 → 潜在表示 → 预测器 → 预测表示
                                            ↓
         实际未来 → 编码器 → 目标表示 ← ← ← ←
                           ↓
                    对比损失最小化
```

---

## 2. 核心模块

### 2.1 编码器（Encoder）
```typescript
// 将高维观测压缩为抽象表示
Encoder: (高维观测) → (低维潜在向量 z)

输入：图像/传感器数据/VR场景
输出：维度 d 的潜在向量（d << 原始维度）

在建筑世界模型中：
- VR场景 → 空间编码（房间类型 + 尺寸 + 材质）
- CAD数据 → 结构编码（层高 + 跨度 + 结构类型）
- 传感器 → 状态编码（位置 + 速度 + 力）
```

### 2.2 预测器（Predictor）
```typescript
// 在表示空间中预测下一个状态
Predictor: (当前表示 z_t, 行动 a_t) → (预测表示 z_{t+1})

输入：当前状态编码 + 行动向量
输出：预测的未来状态编码

关键：只在表示空间预测，不在像素空间
优势：能处理多种可能的未来（多模态预测）
```

### 2.3 目标网络（Target Network）
```typescript
// 稳定的目标表示（避免表示崩塌）
TargetNetwork: (高维观测) → (目标表示 z*)

使用指数移动平均(EMA)更新：
  θ_t' = τ * θ_{t-1}' + (1-τ) * θ_t
```

### 2.4 对比损失（Contrastive Loss）
```typescript
// 最小化预测表示与实际表示的差异
L = || Predictor(z_t, a_t) - Target(z_{t+1}) ||²

只在表示空间计算损失，不重建像素
```

---

## 3. 具身AI世界模型架构

```
┌─────────────────────────────────────────────────────────────┐
│                    具身AI世界模型                              │
│                                                             │
│   ┌──────────┐                                              │
│   │ 传感器观测 │ ← 摄像头/触觉/声音/IMU                        │
│   └────┬─────┘                                              │
│        ↓                                                    │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │  编码器   │ → │ 预测器    │ → │ 世界模型  │             │
│   │ Encoder  │    │ Predictor│    │  World   │             │
│   │ z_t      │    │ z_{t+1}  │    │  Model   │             │
│   └──────────┘    └──────────┘    └────┬─────┘             │
│        ↑              ↑                 ↓                   │
│        │              │          ┌──────────┐             │
│        │              │          │  规划器   │             │
│        │              │          │ Planner  │             │
│        │              │          │ (MCTS/   │             │
│        │              │          │  MPC)    │             │
│        │              │          └────┬─────┘             │
│        │              │                 ↓                   │
│   ┌──────────┐        │          ┌──────────┐             │
│   │ 目标网络 │ ← ← ← ← ← ← ← ← ← │ 行动执行 │             │
│   │ Target   │                │  Action  │             │
│   └──────────┘                └──────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 在建筑物理AI中的映射

### 4.1 编码器（建筑场景）
```typescript
// VR场景编码器
interface SceneEncoder {
  // 输入：VR场景特征
  input: {
    room_type: string      // "客厅" / "餐厅" / "主卧"
    dimensions: [w,d,h]    // 尺寸
    material_tags: string[] // 物理标签
    designer: string        // 设计师
    platform: string        // 来源平台
  }

  // 输出：潜在表示向量
  output: {
    spatial_z: number[]     // 空间特征 [房间大小, 布局类型, ...]
    physics_z: number[]     // 物理特征 [摩擦, 承重, ...]
    affordance_z: number[] // 功能特征 [通行, 操作, ...]
  }
}

// CAD结构编码器
interface CADEncoder {
  // 输入：CAD施工图数据
  input: {
    discipline: string      // 建筑/电气/给排水/暖通
    floor: string          // 楼层
    elements: Element[]    // 图元（墙/柱/梁/管）
  }

  // 输出：结构表示
  output: {
    structural_z: number[]  // 结构特征
    system_z: number[]      // 系统特征（水/电/暖）
    constraint_z: number[]  // 约束特征
  }
}
```

### 4.2 预测器（状态转移）
```typescript
// 世界模型预测器
interface WorldPredictor {
  // 给定当前状态和行动，预测下一个状态
  predict(
    current_state: SceneState,  // 当前场景状态
    action: RobotAction          // 机器人行动
  ): PredictedState              // 预测状态

  // 预测类型：
  // - deterministic: 确定性好（物理模拟）
  // - stochastic: 随机性（多模态预测）
  // - hierarchical: 分层预测（长期 + 短期）
}

// 行动类型
type RobotAction =
  | { type: 'move', target: [x,y,z] }
  | { type: 'grasp', object: string }
  | { type: 'open', object: string }
  | { type: 'pour', source: string, target: string }
  | { type: 'navigate', goal: string }
```

### 4.3 规划器（任务规划）
```typescript
// 基于世界模型的规划
interface Planner {
  // 输入：目标 + 世界模型
  plan(
    goal: TaskGoal,
    world_model: WorldPredictor,
    constraints: Constraint[]
  ): ActionSequence

  // 方法：
  // - MCTS: 蒙特卡洛树搜索（高效探索）
  // - MPC: 模型预测控制（滚动优化）
  // - HL: 分层任务规划（长期任务分解）
}

// 任务示例
interface TaskGoal {
  description: "收拾餐桌并洗碗"
  objects: ["餐桌", "碗", "水槽"]
  constraints: ["不碰撞家具", "餐具轻拿轻放"]
}
```

---

## 5. JEPA 变体

### 5.1 V-JEPA（视频JEPA）
- 用于视频预测
- 时序建模 + 空间表示分离
- 在建筑中用于：VR场景漫游预测

### 5.2 A-JEPA（动作条件JEPA）
- 动作作为条件输入
- 在建筑中用于：机器人行动预测

### 5.3 MC-JEPA（多视角JEPA）
- 多模态输入（图像 + 深度 + 触觉）
- 在建筑中用于：多传感器融合

### 5.4 我们的架构：Building-JEPA
```
输入层：
  VR效果图（图像）     → 视觉编码器
  CAD施工图（元数据）  → 结构编码器
  传感器数据（实时）   → 状态编码器
           ↓ ↓ ↓
        联合潜在空间 z
           ↓
    ┌─────────────────┐
    │   预测器模块     │
    │                 │
    │ 物理预测（力学） │  ← 物理引擎
    │ 导航预测（路径） │  ← A* / RRT
    │ 操作预测（任务） │  ← 技能库
    └─────────────────┘
           ↓
    机器人执行/VR展示
```

---

## 6. 实现路线图

| 阶段 | 模块 | 技术 | 状态 |
|------|------|------|------|
| P0 | VR场景编码器 | CLIP/ViT 提取视觉特征 | 🔜 下一步 |
| P0 | 物理属性标注 | 规则引擎 + ML | ✅ 已有 |
| P1 | CAD结构编码器 | 图神经网络(GNN) | ⏳ 待数据 |
| P1 | 世界预测器 | 3D物理模拟器 | ⏳ 规划中 |
| P2 | 行动规划器 | MCTS / MPC | ⏳ 规划中 |
| P2 | 端到端训练 | JEPA + RL | ⏳ 长期目标 |

---

## 7. 关键技术细节

### 7.1 潜在空间设计
```python
# 建筑场景潜在表示
class BuildingLatentSpace:
    """
    潜在向量 z ∈ R^128
    """
    # 空间特征 (dim=32)
    spatial = {
        'room_size':      # 小/中/大
        'room_type':       # 客厅/餐厅/...
        'ceiling_height':  # 层高
        'openness':        # 开敞度
        'connectivity':    # 连通性（连接几个房间）
    }

    # 物理特征 (dim=32)
    physics = {
        'friction':       # 地面摩擦
        'mass':            # 物体质量
        'fragility':       # 易碎程度
        'temperature':     # 温度
        'moisture':        # 潮湿程度
    }

    # 功能特征 (dim=32)
    affordance = {
        'graspable':       # 可抓取
        'openable':        # 可开启
        'traversable':     # 可通行
        'climbable':       # 可攀爬
        'pourable':        # 可倾倒
    }

    # 可变形为32维
    z = concat(spatial, physics, affordance)  # 96-dim → PCA → 32-dim
```

### 7.2 多模态融合
```python
# 三种输入 → 统一表示
z_final = α * Enc_image(vr_image)
          + β * Enc_struct(cad_data)
          + γ * Enc_state(sensor)

# α,β,γ 可学习或固定权重
```

### 7.3 物理预测损失
```python
# JEPA 损失函数
def jepa_loss(predicted_z, target_z):
    # L2 距离（表示空间）
    repr_loss = ||predicted_z - target_z||²

    # 对比正则（避免崩塌）
    contrastive = cross_entropy(positive_pairs, negative_pairs)

    # 物理一致性（可选）
    physics_consistency = ||f(predicted_z) - f(target_z)||²

    return repr_loss + λ * contrastive
```

---

## 8. 参考资料

- LeCun, Y. (2022). *Joint Embedding Predictive Architecture (JEPA)*
- Bardes et al. (2022). *V-JEPA: Video Joint Embedding Predictive Architecture*
- Hafner et al. (2019). *Dreamer: World Models for Mathematical Discovery*
- Hafner et al. (2020). *DreamerV2: Mastering Atari with a World Model*
- Chen et al. (2023). *A-JEPA: Action-Conditioned JEPA*
