# Psi-R2 VLA 交接文档（另一个 QClaw 请从这里开始）

## 目录
1. [已完成的工作](#已完成的工作)
2. [Psi-R2 VLA 接口说明](#psi-r2-vla-接口说明)
3. [接入 Psi-W0](#接入-psi-w0)
4. [下一步任务](#下一步任务)
5. [已知问题](#已知问题)

---

## 已完成的工作

### 1. 数据修复 ✅
- `scene_graph_real.json`: 151节点 + 897边（同房间299 / 跨房间598）
- `buildingStore.ts`: 添加 `'renderings'` 到 `SceneType`
- `sceneConfig.ts`: 添加 `SCENE_KEY_NAMES` 和 `SCENE_CATEGORY_MAP`
- `rendering_objects.json`: 1027张效果图（file:// URL），移除 `original_path` 敏感字段
- 推理服务器: 5000端口，`/api/scene` 返回 151节点+897边

### 2. Psi-R2 VLA ✅
- `src/psi_r2_vla.py`: 完整实现（19821字节）
- 演示跑通：4条指令 → 动作序列 → W0仿真 PASS
- **架构**: SceneEncoder + LanguageEncoder + ActionPlanner → Psi-W0

### 3. 安全架构 ✅
- `original_path` 字段已移除（桌面路径不再暴露）
- `path` 使用 `file://` URL 格式
- 效果图数据仅含 category/scene/name，无客户/项目/公司信息

---

## Psi-R2 VLA 接口说明

### 核心文件
```
src/psi_r2_vla.py          # VLA 主模块（20KB）
src/psi_w0_simulator.py    # W0 仿真器（12KB）
src/neural_inference_server.py  # 推理服务器
```

### 使用方法

```python
from src.psi_r2_vla import PsiR2VLA, run_vla_with_simulation

# 方法1：单独使用 VLA
vla = PsiR2VLA()
vla.load_scene(objects, edges)
result = vla.query("把客厅的沙发往左边移动")

# 方法2：VLA + W0 仿真（完整流程）
result = run_vla_with_simulation("把客厅的沙发往左边移动", objects)
```

### 返回格式
```python
{
  "instruction": "把客厅的沙发往左边移动",
  "scene_summary": {"total_objects": 3, "object_types": {...}, "edge_count": 0},
  "related_objects": [
    {"id": "sofa-001", "type": "sofa", "position": [4.0, 0, 3.0], "relevance_score": 0.515}
  ],
  "parsed_instruction": {
    "action": "move", "object_type": "sofa", "direction": "left", "constraints": []
  },
  "actions": [
    {
      "step": 1, "actor": "robot-arm-01", "action": "move",
      "object_id": "sofa-001", "object_type": "sofa",
      "from": [4.0, 0, 3.0], "to": [2.0, 0, 3.0],
      "distance_m": 2.0,
      "physics": {
        "mass_kg": 45, "friction": 0.55,
        "grasp_force_newton": 242.6, "grasp_type": "power",
        "fragile": False, "max_velocity_ms": 0.5,
        "energy_kj": 0.032, "collision_risk": "low"
      },
      "feasible": True
    }
  ],
  "simulation": {  # 如果接入了 W0
    "plan_feasible": True,
    "avg_score": 1.0,
    "feasible_steps": 3, "total_steps": 3
  },
  "vla_model": "Psi-R2",
  "confidence": 0.515
}
```

### 与推理服务器集成
```python
# 从推理服务器获取场景
import requests
resp = requests.get("http://localhost:5000/api/scene")
data = resp.json()
objects = [{"id": f"node-{i}", "type": "door",
            "position": data["positions"][i]} for i in range(data["num_nodes"])]
edges = [{"source": e[0], "target": e[1]} for e in data["edges"]]

# 接入 VLA
result = run_vla_with_simulation("移动卧室的书桌", objects)
```

---

## 接入 Psi-W0

Psi-W0 已实现：
```python
from src.psi_w0_simulator import PSIW0Simulator
w0 = PSIW0Simulator()
result = w0.evaluate_plan([{"from": [1,0,0], "to": [3,0,0],
                             "object": "sofa", "object_type": "sofa",
                             "action": "move"}])
# result["plan_feasible"], result["avg_score"]
```

---

## 下一步任务

### 高优先级
1. **加载 151节点真实场景**: `src/psi_r2_vla.py` demo 里 scene_graph_real.json 找不到，改用内嵌小场景。需要让 demo 能自动从 `data/processed/cleaned/scene_graph_real.json` 加载真实数据。

2. **接入 LLM**: 当前 LanguageEncoder 用关键词匹配，精度有限。替换为真实 LLM embedding：
   - 方案A: OpenAI API (embedding model)
   - 方案B: 本地 embedding (sentence-transformers)

3. **扩展对象类型**: 当前 VOCAB 只覆盖家具/家电。需要从 `rendering_objects.json`（1027张效果图）提取更多场景对象类型。

4. **前端集成**: 把 Psi-R2 VLA 做成 React 组件，在 `http://localhost:3000` 的控制面板里加一个"VLA指令输入框"。

### 中优先级
5. **RL 策略优化**: Psi-W0 的数据飞轮 → 收集真实执行反馈 → 强化学习修正策略参数。

6. **碰撞检测升级**: 当前碰撞检测用简化几何 → 改用 RelationTransformer 的边预测概率。

7. **多机器人协作**: 支持多臂同时规划。

---

## 已知问题

| 问题 | 原因 | 修复方案 |
|------|------|----------|
| W0 `distance_m` 字段缺失 | W0 返回格式不含 `distance_m` | 已修复输出显示，W0 数据流正常 |
| scene_graph_real.json demo 找不到 | 路径问题 | 检查 `PROJ` 路径设置 |
| 中文终端乱码 | GBK vs UTF-8 编码 | 所有核心数据已是 UTF-8，仅终端显示问题 |

---

## 文件清单

```
src/
  psi_r2_vla.py              # Psi-R2 VLA（本次完成）
  psi_w0_simulator.py        # Psi-W0 仿真（之前完成）
  neural_inference_server.py # 推理服务器（5000端口）

data/processed/cleaned/
  scene_graph_real.json     # 151节点 + 897边
  building_objects.json      # 151个建筑对象

web-app/
  src/store/buildingStore.ts  # ✅ 已修复 SceneType 含 renderings
  src/data/sceneConfig.ts    # ✅ 已添加 SCENE_KEY_NAMES
  public/data/
    rendering_objects.json   # ✅ 1027张效果图，无隐私数据
```
