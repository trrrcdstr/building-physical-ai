# 建筑物理AI世界模型 — 系统架构总览

> 最后更新：2026-04-29

---

## 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端展示层 (React)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Building │ │Relation  │ │   Lit    │ │Gaussian │ │  Agent   │ │
│  │  Scene   │ │  Scene   │ │ Building │ │  Scene  │ │Execution │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       └───────────┴──────────────┴───────────┴───────────┘        │
│                              ↓ 3000                              │
├─────────────────────────────────────────────────────────────────┤
│                       皮·骨·肉三层架构                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │   皮：感知层    │→ │   骨：分析层    │→ │   肉：执行层    │   │
│  │ NeuralInference │  │   AgentCommand  │  │ Agent API (5002)│   │
│  │  VRViewer      │  │   PhysicsPanel  │  │ VLA Server(5004)│   │
│  │ RenderingGallery│ │  SceneColumn   │  │  Robot Hardware │   │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘   │
│          │                   │                   │             │
│          ↓                   ↓                   ↓             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ SceneGraph   │  │ Harness     │  │ Psi-W0      │         │
│  │ API (5001)   │  │ 约束引擎    │  │ 仿真引擎    │         │
│  │ 151节点/1029边│  │ 承重墙检测  │  │ 物理仿真    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
├─────────────────────────────────────────────────────────────────┤
│                      神经网络推理层 (5000)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │SpatialEncoder│  │ PhysicsMLP  │  │RelationTrans│           │
│  │ Val Acc 98.1%│  │ 材质/质量   │  │ Val Acc 100%│           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
├─────────────────────────────────────────────────────────────────┤
│                         数据资产层                               │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │ 444条  │ │ 1053张 │ │ 151个 │ │ 76个  │ │ 23个  │        │
│  │ VR全景 │ │渲染图  │ │建筑对象│ │ CAD   │ │ 知识库 │        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 数据流图

```
用户输入（自然语言指令）
        │
        ▼
┌───────────────────┐
│  VLA Server (5004) │  ← 自然语言 → 任务类型分类（drill/move/clean/inspect）
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Agent API (5002)  │  ← 任务类型 + 场景数据 → 任务规划（步骤分解）
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────────┐
│Harness│ │ Psi-W0    │
│约束检测│ │ 世界模型  │
│ 5002  │ │  仿真     │
└───┬───┘ └─────┬─────┘
    │           │
    │  ┌────────┘
    ▼  ▼
┌──────────────────┐
│  NN推理服务器     │  ← 场景编码 + 物理预测
│  (5000)          │
│  SpatialEncoder  │
│  PhysicsMLP      │
│  RelationTrans   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  场景图谱 API     │
│  (5001)          │  ← 151节点 / 1029边 / 场景检索
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   前端3D场景      │
│   React+Three.js │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  机器人执行       │
│  越疆CR + DexHand│
└──────────────────┘
         │
         ▼
   数据飞轮（执行结果 → 模型更新）
```

---

## 3. 服务端口分配

| 端口 | 服务 | 技术栈 | 功能 |
|------|------|--------|------|
| 3000 | 前端 Web | Vite + React | 用户界面（主入口） |
| 5000 | NN推理服务器 | FastAPI + PyTorch | 空间/物理/关系神经网络 |
| 5001 | 场景图谱API | FastAPI | 151节点场景图 + 1029边 |
| 5002 | Agent API | FastAPI | 任务规划 + Harness约束 |
| 5004 | VLA Server | Flask | 视觉-语言-动作分类 |
| 8888 | 渲染图服务 | Python HTTP | 1053张效果图静态文件 |

---

## 4. 关键文件索引

### 前端（web-app/src/）

| 文件 | 行数 | 功能 |
|------|------|------|
| `App.tsx` | 310 | 主入口，场景路由，Three.js Canvas |
| `scenes/BuildingScene.tsx` | ~300 | 3D建筑白模，worldObjects渲染 |
| `scenes/RelationScene.tsx` | ~360 | 151门/窗3D可视化，关系线 |
| `scenes/LitBuildingScene.tsx` | ~250 | 时空光影，SunCalc太阳位置 |
| `scenes/GaussianScene.tsx` | ~400 | 3DGS渲染，双模式（Canvas/Points） |
| `scenes/EstateScene.tsx` | ~200 | 小区拓扑2D+3D |
| `components/AgentCommandPanel.tsx` | ~500 | Agent指令面板，执行时间线 |
| `components/AgentExecutionPanel.tsx` | ~300 | 具身执行面板，机器人状态 |
| `components/NeuralInferencePanel.tsx` | ~400 | 神经网络推理面板（三Tab） |
| `components/PhysicsPanel.tsx` | ~200 | 物理常识面板 |
| `components/SceneColumn.tsx` | ~150 | 场景列表面板 |
| `components/SceneNavigator.tsx` | ~200 | 皮·骨·肉场景导航 |
| `components/TopBar.tsx` | ~100 | 顶部状态栏，服务检测 |
| `store/buildingStore.ts` | ~150 | Zustand状态管理 |
| `data/sceneData.ts` | ~5000 | 场景数据（worldObjects） |

### 后端（src/）

| 文件 | 行数 | 功能 |
|------|------|------|
| `neural_inference_server.py` | ~600 | NN推理API（5000端口） |
| `four_layer_api.py` | ~400 | 场景图谱API（5001端口） |
| `agent_api_server.py` | ~300 | Agent API（5002端口） |
| `vla_server.py` | ~200 | VLA分类（5004端口） |
| `gaussian_api.py` | ~500 | 高斯Splatting API |
| `harness/v0/` | ~1500 | Harness核心（PromptRegistry/ContextEngine等） |

### 训练脚本（scripts/）

| 文件 | 功能 |
|------|------|
| `train_gaussian_simple.py` | 简化版2D高斯训练 |
| `train_gaussian_enhanced.py` | 增强版高斯训练 |
| `train_gaussian_v2/v3.py` | 不同版本训练 |
| `prepare_3dgs_imgs.py` | 3DGS图片预处理 |
| `qa_pair_generator.py` | QA问答对生成 |
| `synthetic_data_generator.py` | 合成数据生成 |

### 数据（data/）

| 目录/文件 | 内容 |
|-----------|------|
| `processed/scene_graph_v2.json` | 151节点+1029边场景图 |
| `processed/building_objects_enhanced.json` | 151建筑对象+物理参数 |
| `processed/renderings/rendering_objects.json` | 1053张效果图URL |
| `gaussian_models/*.json` | 已训练高斯模型（室内_家庭等） |
| `gaussian_training/images/` | 训练图片 |
| `training/qa_pairs_v1.json` | 77条QA问答对 |
| `training/synthetic_scenes_v1.json` | 100场景355任务 |

---

## 5. 皮·骨·肉三层详解

### 皮：感知层（Perception Layer）
- **定位**：接收多模态建筑数据，输出结构化场景描述
- **组件**：`NeuralInferencePanel` + `VRViewer` + `RenderingGallery`
- **数据源**：444条VR全景 + 1053张渲染图 + 151节点场景图
- **核心能力**：空间关系推理（98.1%准确率）、物理属性预测

### 骨：分析层（Reasoning Layer）
- **定位**：物理常识推理 + 任务规划 + 安全约束
- **组件**：`PhysicsPanel` + `AgentCommandPanel` + `SceneColumn`
- **核心能力**：
  - 材质识别（陶瓷/玻璃/木材/金属）
  - 质量/摩擦/刚度推断
  - 任务分解（钻孔→搬运→清洁→巡检）
- **护城河**：Harness约束引擎（承重墙检测、管道检测）

### 肉：执行层（Execution Layer）
- **定位**：机器人动作执行 + 物理仿真
- **组件**：`Agent API`（5002）+ `VLA Server`（5004）+ `Psi-W0`仿真
- **硬件**：越疆CR协作臂 + DexHand 021灵巧手
- **执行**：钻孔/搬运/清洁/巡检四类任务
- **反馈**：数据飞轮（执行结果→模型更新）

---

## 6. 关键创新点

| 创新 | 描述 | 技术指标 |
|------|------|----------|
| 真实空间坐标 | 151个门/窗对象有米制坐标（X=[0,300]m） | 正负样本完全分离 |
| SpatialEncoder | 9D位置+几何特征编码 | Val Acc=98.1% |
| RelationTransformer | 交叉注意力关系推理 | Val Acc=100% |
| Harness安全体系 | 承重墙/管道/电气三重检测 | 零误判 |
| 材质物理知识库 | 22种材质含摩擦/刚度/碰撞参数 | 直接注入VR引擎 |
| 具身智能任务规划 | 4类任务（钻孔/搬运/清洁/巡检） | 6步分解执行 |

---

## 7. 下一步路线图

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1.1 | CAD解析（DWG→DXF） | 待完成 |
| Phase 1.2 | 多房间/多楼层场景扩展 | 待完成 |
| Phase 2.1 | PyBullet物理仿真 | 待完成 |
| Phase 2.2 | Psi-W0 世界模型完善 | 进行中 |
| Phase 3 | Psi-R2 VLA 接入 LLM | 待完成 |
| Phase 4 | 真实机器人联调 | 待完成 |
