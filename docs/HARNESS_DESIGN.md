# Harness 设计文档 v0.1
## P0 阶段：让系统"活"起来

---

## 核心理念

> **Harness 不是被设计出来的，而是像生命一样"长"出来的。**

传统AI开发：设计 → 实现 → 测试 → 修bug → 上线
Harness思维：播种 → 观察 → 适应 → 淘汰 → 进化

区别在于：**你提供生态，不提供蓝图。**

---

## 一、数据飞轮：Harness 的"心脏"

```
┌──────────────────────────────────────────────────────────┐
│                      数据飞轮                              │
│                                                          │
│    收集 ← 标注 ← 训练 ← 推理 ← 执行                        │
│      ↑                                      ↓             │
│      └────────────── 反馈循环 ← ← ← ← ← ┘               │
└──────────────────────────────────────────────────────────┘
```

### 我们的数据飞轮（P0阶段）

```
                    ┌──────────────────┐
                    │   VR数据采集      │  80个VR全景
                    │   CAD数据导入     │  17个DWG元数据
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   场景解析        │  房间提取/物理标注
                    │   自动特征提取    │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   知识库构建       │  世界模型输入
                    │   VR_KNOWLEDGE   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   3D场景生成       │  BuildingScene
                    │   世界模型推理     │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   用户交互/反馈   │  点击/选择/VR跳转
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   闭环数据        │  使用日志/偏好/错误
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   飞轮加速         │  更多VR/更准模型
                    │   (自动进化)       │
                    └──────────────────┘
```

**飞轮一旦转动，就会越来越快。** 关键是从"种子数据"开始。

---

## 二、三层架构：Harness 的"骨骼"

### L1: Prompt（最小单元）
```
Prompt = 任务描述 + 上下文 + 约束
```

```python
# 最小可用 Prompt
prompt = {
    "task": "分析这个房间的物理属性",
    "context": {
        "room_type": "客厅",
        "dimensions": [5.2, 4.1, 2.8],
        "materials": ["瓷砖", "玻璃窗"],
    },
    "constraints": ["只输出物理属性，不做其他"]
}
```

**Harness L1 的职责：**
- Prompt 注册表（防止重复/冲突）
- Prompt 版本管理
- Prompt 性能日志

### L2: Context（信息层）
```
Context = Prompt + Memory + Knowledge + Tool Output
```

```python
# L2 Context — 加入记忆和知识
context = {
    "prompt": prompt,
    "memory": {
        "recent_tasks": [...],      # 最近任务
        "user_preferences": {...},   # 用户偏好
        "session_state": {...},     # 会话状态
    },
    "knowledge": {
        "physics_rules": [...],     # 物理规则
        "building_codes": [...],    # 建筑规范
        "robot_capabilities": [...], # 机器人能力
    },
    "tool_output": {
        "vr_scan": {...},
        "cad_parse": {...},
    }
}
```

**Harness L2 的职责：**
- Memory 系统（短期/长期）
- Knowledge 检索（向量相似度）
- Tool 调用编排

### L3: Harness（完整系统）
```
Harness = L1 + L2 + Runtime + Guardrails + Feedback
```

```python
# L3 Harness — 完整闭环系统
class BuildingHarness:
    # 核心组件
    prompt_registry: PromptRegistry      # L1
    context_engine: ContextEngine         # L2
    world_model: WorldModel              # JEPA
    feedback_loop: FeedbackLoop          # 飞轮
    guardrails: Guardrails               # 安全

    def run(self, task):
        # 1. Prompt 检索
        prompt = self.prompt_registry.get(task)

        # 2. Context 构建
        ctx = self.context_engine.build(prompt)

        # 3. 世界模型推理
        world_state = self.world_model.predict(ctx)

        # 4. Guardrails 检查
        if not self.guardrails.check(ctx, world_state):
            return self.guardrails.fallback()

        # 5. 执行
        result = self.execute(ctx, world_state)

        # 6. 反馈收集（飞轮加速）
        self.feedback_loop.record(ctx, result)

        return result
```

---

## 三、渐进式实现：让 Harness "生长"

### 🌱 P0.1: 种子 Prompt 系统
```
目标：让第一个 Prompt 跑起来
```

```python
# src/harness/v0/prompt_registry.py

from dataclasses import dataclass, field
from typing import List, Optional
import uuid
import json
from datetime import datetime

@dataclass
class PromptTemplate:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    task_type: str = ""  # "scene_analysis" | "physics_reasoning" | "robot_planning"
    template: str = ""
    version: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    performance: dict = field(default_factory=lambda: {
        "runs": 0,
        "success": 0,
        "avg_latency_ms": 0
    })

class PromptRegistry:
    """L1: Prompt 注册与版本管理"""

    def __init__(self, storage_path: str = "data/harness/prompts.json"):
        self.storage_path = storage_path
        self.prompts: List[PromptTemplate] = []
        self._load()

    def register(self, prompt: PromptTemplate) -> str:
        """注册新 Prompt"""
        self.prompts.append(prompt)
        self._save()
        return prompt.id

    def get(self, task_type: str) -> Optional[PromptTemplate]:
        """根据任务类型获取最优 Prompt"""
        candidates = [p for p in self.prompts if p.task_type == task_type]
        if not candidates:
            return None
        # 选择成功率最高的版本
        return max(candidates, key=lambda p: p.performance["success"] / max(p.performance["runs"], 1))

    def evolve(self, prompt_id: str, feedback: dict):
        """根据反馈进化 Prompt（不用重新设计，只调优）"""
        for p in self.prompts:
            if p.id == prompt_id:
                p.performance["runs"] += 1
                if feedback["success"]:
                    p.performance["success"] += 1
                # 超过阈值 → 生成新版本
                rate = p.performance["success"] / max(p.performance["runs"], 1)
                if rate < 0.7 and p.performance["runs"] > 5:
                    self._fork_version(p)
                self._save()
                break

    def _fork_version(self, prompt: PromptTemplate):
        """Prompt 失败率高时，自动分叉生成新版本"""
        new_id = str(uuid.uuid4())[:8]
        new_prompt = PromptTemplate(
            id=new_id,
            name=f"{prompt.name}_v{prompt.version + 1}",
            task_type=prompt.task_type,
            template=prompt.template,  # 初始相同，后续调优
            version=prompt.version + 1,
        )
        self.prompts.append(new_prompt)
        print(f"[Harness] Prompt {prompt.id} 进化 → 新版本 {new_id}")
```

### 🌱 P0.2: Context 引擎
```
目标：让 Prompt 知道"上下文"
```

```python
# src/harness/v0/context_engine.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
import hashlib

@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    type: str  # "fact" | "preference" | "task" | "error"
    timestamp: str
    importance: float  # 0-1，越高越重要
    tags: List[str] = field(default_factory=list)

@dataclass
class Context:
    """L2 Context — 构建完整的推理上下文"""
    prompt_id: str
    scene_type: str           # "residence" | "mall" | ...
    vr_id: Optional[int]
    room_data: Dict[str, Any]  # 来自 VR_KNOWLEDGE
    cad_data: Optional[Dict]
    recent_tasks: List[str]   # 最近任务（短期记忆）
    learned_facts: List[str]  # 学习的物理事实（长期记忆）
    robot_state: Dict[str, Any]
    metadata: Dict[str, Any]

    def to_llm_prompt(self) -> str:
        """构建给 LLM 的完整提示词"""
        parts = []

        # 任务描述
        parts.append(f"## 任务\n分析以下建筑场景的物理属性和机器人交互策略。")

        # 场景信息
        if self.room_data:
            parts.append(f"\n## 场景数据")
            parts.append(f"- 房间类型：{self.room_data.get('room_category', '未知')}")
            parts.append(f"- 设计师：{self.room_data.get('designer', '未知')}")
            parts.append(f"- 平台：{self.room_data.get('platform', '未知')}")

            physics_tags = self.room_data.get('physics_tags', [])
            if physics_tags:
                parts.append(f"- 物理标签：{', '.join(physics_tags)}")

        # 相关记忆
        if self.learned_facts:
            parts.append(f"\n## 相关物理知识")
            for fact in self.learned_facts[-3:]:  # 最近3条
                parts.append(f"- {fact}")

        # 机器人状态
        if self.robot_state:
            parts.append(f"\n## 机器人状态")
            parts.append(f"- 当前位置：{self.robot_state.get('position', '未知')}")
            parts.append(f"- 可用能力：{self.robot_state.get('capabilities', [])}")

        return "\n".join(parts)

class ContextEngine:
    """L2: 上下文构建引擎"""

    def __init__(self, memory_path: str = "data/harness/memory.json"):
        self.memory_path = memory_path
        self.short_term: List[MemoryEntry] = []  # 最近50条
        self.long_term: List[MemoryEntry] = []    # 重要记忆
        self._load()

    def build(self, prompt_id: str, scene_data: Dict) -> Context:
        """构建完整上下文"""

        # 1. 检索相关长期记忆
        relevant_facts = self._retrieve_facts(scene_data)

        # 2. 获取近期任务（短期记忆）
        recent = [m.content for m in self.short_term[-10:]]

        # 3. 推断机器人状态
        robot_state = self._infer_robot_state(scene_data)

        return Context(
            prompt_id=prompt_id,
            scene_type=scene_data.get("scene_type", "residence"),
            vr_id=scene_data.get("vr_id"),
            room_data=scene_data.get("room_data", {}),
            cad_data=scene_data.get("cad_data"),
            recent_tasks=recent,
            learned_facts=relevant_facts,
            robot_state=robot_state,
            metadata={
                "build_at": datetime.now().isoformat(),
                "context_version": "v0.1"
            }
        )

    def _retrieve_facts(self, scene_data: Dict, top_k: int = 5) -> List[str]:
        """简单关键词匹配检索（未来升级为向量检索）"""
        room_cat = scene_data.get("room_data", {}).get("room_category", "")
        facts = []

        # 内置物理知识库
        PHYSICS_DB = {
            "客厅": ["地面摩擦系数0.4", "空间开阔适合移动", "沙发区域需要避障"],
            "厨房": ["地面潮湿需防滑", "台面高度约0.9m", "刀具需小心抓取"],
            "卫生间": ["地面湿滑风险高", "空间狭小限制移动", "防水要求"],
            "主卧": ["地毯区域摩擦力大", "衣柜门可开启", "床体不可移动"],
            "楼梯": ["有高度差", "需要攀爬能力", "扶手可辅助"],
        }

        for cat, knowledge in PHYSICS_DB.items():
            if cat in room_cat:
                facts.extend(knowledge[:2])

        return facts[:top_k]

    def _infer_robot_state(self, scene_data: Dict) -> Dict:
        """根据场景推断机器人状态"""
        return {
            "position": [0, 0, 0],
            "orientation": 0,
            "capabilities": ["move", "grasp", "open"],
            "battery_level": 0.8,
        }

    def record(self, context: Context, result: Dict, success: bool):
        """记录执行结果到记忆"""
        entry = MemoryEntry(
            id=hashlib.md5(f"{context.vr_id}{datetime.now()}".encode()).hexdigest()[:12],
            content=f"VR{context.vr_id} {context.scene_type} → {'成功' if success else '失败'}",
            type="task",
            timestamp=datetime.now().isoformat(),
            importance=0.8 if success else 1.0,  # 失败经验更重要
            tags=[context.scene_type, "success" if success else "error"]
        )

        self.short_term.append(entry)

        # 失败的经验 → 永久记忆
        if not success:
            self.long_term.append(entry)

        # 限制短期记忆长度
        if len(self.short_term) > 50:
            self.short_term = self.short_term[-50:]

        self._save()

    def _load(self):
        try:
            data = json.load(open(self.memory_path))
            self.short_term = [MemoryEntry(**e) for e in data.get("short_term", [])]
            self.long_term = [MemoryEntry(**e) for e in data.get("long_term", [])]
        except:
            pass

    def _save(self):
        import os
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        json.dump({
            "short_term": [vars(e) for e in self.short_term],
            "long_term": [vars(e) for e in self.long_term],
        }, open(self.memory_path, "w"), ensure_ascii=False)
```

### 🌱 P0.3: 反馈循环（飞轮）
```
目标：让系统从错误中学习
```

```python
# src/harness/v0/feedback_loop.py

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

@dataclass
class Feedback:
    """用户/系统反馈"""
    context_id: str
    task_type: str
    input_data: Dict
    output_data: Dict
    expected: Optional[Dict]
    success: bool
    user_rating: Optional[int]  # 1-5
    error_message: Optional[str]
    timestamp: str

class FeedbackLoop:
    """
    反馈循环引擎
    核心思想：每一次交互都是学习机会
    """

    def __init__(self, storage_path: str = "data/harness/feedback.json"):
        self.storage_path = storage_path
        self.feedbacks: List[Feedback] = []
        self._load()

        # 自动触发规则
        self.auto_rules = [
            {"condition": lambda f: f.success and f.user_rating and f.user_rating >= 4,
             "action": "evolve_prompt"},
            {"condition": lambda f: not f.success,
             "action": "flag_for_review"},
            {"condition": lambda f: f.user_rating and f.user_rating <= 2,
             "action": "rollback_prompt"},
        ]

    def record(self, context_id: str, task_type: str, input_data: Dict,
               output_data: Dict, expected: Optional[Dict] = None,
               user_rating: Optional[int] = None,
               error_message: Optional[str] = None):

        success = error_message is None and (expected is None or self._check_match(output_data, expected))

        fb = Feedback(
            context_id=context_id,
            task_type=task_type,
            input_data=input_data,
            output_data=output_data,
            expected=expected,
            success=success,
            user_rating=user_rating,
            error_message=error_message,
            timestamp=datetime.now().isoformat(),
        )

        self.feedbacks.append(fb)
        self._trigger_rules(fb)
        self._save()

    def _trigger_rules(self, fb: Feedback):
        """自动触发反馈规则"""
        for rule in self.auto_rules:
            if rule["condition"](fb):
                self._execute_action(rule["action"], fb)

    def _execute_action(self, action: str, fb: Feedback):
        """执行动作"""
        if action == "evolve_prompt":
            # 好的反馈 → Prompt 变强
            print(f"[FeedbackLoop] ⬆️ 提升 Prompt {fb.task_type} (评分: {fb.user_rating})")
            # 通知 PromptRegistry
            # self.prompt_registry.evolve(...)

        elif action == "flag_for_review":
            # 失败 → 标记待审查
            print(f"[FeedbackLoop] ⚠️ 标记 {fb.task_type} 待审查")
            self._write_alert(fb)

        elif action == "rollback_prompt":
            # 差评 → 回滚到上一版本
            print(f"[FeedbackLoop] ⬇️ 回滚 Prompt {fb.task_type} (评分: {fb.user_rating})")

    def _check_match(self, output: Dict, expected: Dict) -> bool:
        """简单匹配检查"""
        for key in expected:
            if key not in output:
                return False
            if output[key] != expected[key]:
                return False
        return True

    def get_stats(self) -> Dict:
        """统计反馈数据"""
        if not self.feedbacks:
            return {"total": 0, "success_rate": 0, "avg_rating": 0}

        total = len(self.feedbacks)
        success = sum(1 for f in self.feedbacks if f.success)
        ratings = [f.user_rating for f in self.feedbacks if f.user_rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        return {
            "total": total,
            "success_rate": success / total,
            "avg_rating": round(avg_rating, 2),
            "by_task_type": self._by_task_type(),
        }

    def _by_task_type(self) -> Dict:
        result = {}
        for fb in self.feedbacks:
            if fb.task_type not in result:
                result[fb.task_type] = {"total": 0, "success": 0}
            result[fb.task_type]["total"] += 1
            if fb.success:
                result[fb.task_type]["success"] += 1
        return result

    def _write_alert(self, fb: Feedback):
        """写入告警日志"""
        alert_path = self.storage_path.replace("feedback.json", "alerts.jsonl")
        with open(alert_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(vars(fb), ensure_ascii=False) + "\n")

    def _load(self):
        try:
            self.feedbacks = [Feedback(**f) for f in json.load(open(self.storage_path))]
        except:
            pass

    def _save(self):
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        json.dump([vars(f) for f in self.feedbacks[-1000:]],  # 保留最近1000条
                  open(self.storage_path, "w"), ensure_ascii=False, indent=2)
```

---

## 四、P0 实现路线

```
P0.1 ─── Prompt 注册表（种子）
        ↓
P0.2 ─── Context 引擎（记忆+知识）
        ↓
P0.3 ─── 反馈循环（飞轮加速）
        ↓
P0.4 ─── Guardrails（安全边界）
        ↓
P0.5 ─── World Model 集成（JEPA）
        ↓
P1 ───── 自主进化（无需人工干预）
```

### P0.1 ~ P0.3 文件结构
```
building-physical-ai/
├── src/
│   └── harness/
│       ├── __init__.py
│       ├── v0/
│       │   ├── __init__.py
│       │   ├── prompt_registry.py   # L1: Prompt管理
│       │   ├── context_engine.py    # L2: 上下文构建
│       │   ├── feedback_loop.py      # 飞轮
│       │   ├── guardrails.py         # 安全边界
│       │   └── world_model.py        # JEPA集成（待实现）
│       └── prompts/                  # Prompt模板
│           ├── scene_analysis.md
│           ├── physics_reasoning.md
│           └── robot_planning.md
├── data/
│   └── harness/
│       ├── prompts.json
│       ├── memory.json
│       ├── feedback.json
│       └── alerts.jsonl
└── web-app/
    └── src/
        └── hooks/
            └── useHarness.ts         # 前端调用Harness
```

---

## 五、"生长"哲学

### 为什么 Harness 是"长"出来的？

```
传统开发（瀑布模型）：
  需求 → 设计 → 实现 → 测试 → 上线 → 完成

Harness生长（演化模型）：
  种子 → 运行 → 反馈 → 适应 → 变异 → 筛选 → 进化
                                        ↓
                                   新种子（更优）
                                        ↓
                              持续循环，永不"完成"
```

**关键区别：**
- 不是"设计好了再实现"，而是"先跑起来再优化"
- 不是"消灭所有bug"，而是"让系统学会从错误中学习"
- 不是"一次性完美"，而是"持续迭代进化"

### 在我们系统中的体现

| 传统方式 | Harness 方式 |
|----------|-------------|
| 手动设计 Prompt | 从种子 Prompt 出发，自动进化 |
| 固定物理规则 | 从交互数据中学习物理规律 |
| 人工标注数据 | 从反馈中自动生成训练数据 |
| 一次性上线 | 持续部署，永不"完成" |

---

## 六、Prompt 种子（马上可以跑）

```markdown
# Prompt 种子 #1: 场景物理分析

## 任务
分析给定建筑场景的物理属性，输出机器人交互建议。

## 输入
- 房间类型：{room_type}
- 尺寸：{width}m × {depth}m × {height}m
- 物理标签：{physics_tags}

## 输出（JSON）
{
  "physical_properties": {
    "friction": 0.0-1.0,
    "fragility": 0.0-1.0,
    "moisture_risk": true/false,
    "obstacle_risk": true/false
  },
  "robot_recommendations": [
    "行动建议1",
    "行动建议2"
  ],
  "safety_notes": [
    "安全注意事项"
  ]
}

## 约束
- 只输出JSON，不输出其他内容
- 基于物理标签推断属性
- 机器人能力：move/grasp/open/push/climb
```

这是第一个"种子"。把它种下去，让它自己生长。

---

_文档版本：v0.1 — 2026-04-10_
_核心理念：Harness不是被设计出来的，而是像生命一样"长"出来的。_
