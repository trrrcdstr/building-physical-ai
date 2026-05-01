"""
L1: Prompt 注册表
像种子一样：埋下去，让它自己生长
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
import uuid
import json
import os
from datetime import datetime


@dataclass
class PromptTemplate:
    """Prompt 模板"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    task_type: str = ""       # "scene_analysis" | "physics_reasoning" | "robot_planning"
    template: str = ""         # Prompt 模板内容
    variables: List[str] = field(default_factory=list)  # 占位变量
    version: int = 1
    parent_id: Optional[str] = None  # 父版本（进化树）
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    performance: Dict = field(default_factory=lambda: {
        "runs": 0,
        "success": 0,
        "errors": 0,
        "avg_latency_ms": 0,
        "ratings": [],  # [1,2,3,4,5]
    })

    def success_rate(self) -> float:
        if self.performance["runs"] == 0:
            return 0.0
        return self.performance["success"] / self.performance["runs"]

    def avg_rating(self) -> float:
        ratings = self.performance.get("ratings", [])
        if not ratings:
            return 0.0
        return sum(ratings) / len(ratings)

    def to_prompt(self, **kwargs) -> str:
        """用变量填充模板"""
        result = self.template
        for key in self.variables:
            value = kwargs.get(key, f"{{{key}}}")
            result = result.replace(f"{{{key}}}", str(value))
        return result


class PromptRegistry:
    """
    L1: Prompt 注册与进化系统

    设计哲学：
    - 不预设"最优Prompt"，而是让多个版本竞争
    - 成功率高的版本获得更多使用机会
    - 持续失败的版本自动分叉生成新版本
    """

    def __init__(self, storage_path: str = "data/harness/prompts.json"):
        self.storage_path = storage_path
        self.prompts: List[PromptTemplate] = []
        self._load()
        self._seed_if_empty()

    def _seed_if_empty(self):
        """如果为空，种下第一批种子"""
        if self.prompts:
            return

        seeds = [
            # 种子1：场景物理分析
            PromptTemplate(
                id="seed_01",
                name="场景物理分析",
                task_type="scene_analysis",
                template="""## 任务
分析以下建筑场景的物理属性，输出机器人交互建议。

## 输入
- 房间类型：{room_type}
- 尺寸：{width}m × {depth}m × {height}m
- 物理标签：{physics_tags}

## 输出要求
仅输出JSON，格式如下：
```json
{{
  "friction": 0.0到1.0的数字,
  "fragility": 0.0到1.0的数字,
  "moisture_risk": true或false,
  "obstacle_risk": true或false,
  "traversable": true或false,
  "climbable": true或false,
  "recommendations": ["行动建议1", "行动建议2"],
  "safety_notes": ["安全注意1"]
}}
```""",
                variables=["room_type", "width", "depth", "height", "physics_tags"],
                version=1,
            ),

            # 种子2：机器人路径规划
            PromptTemplate(
                id="seed_02",
                name="路径规划",
                task_type="path_planning",
                template="""## 任务
为机器人生成从起点到终点的安全路径。

## 输入
- 起点：{start_position}
- 终点：{goal_position}
- 房间类型：{room_type}
- 障碍物：{obstacles}
- 机器人能力：{robot_capabilities}

## 输出
输出JSON格式：
```json
{{
  "path": [[x,y,z], [x,y,z], ...],
  "estimated_time": 秒数,
  "obstacles_avoided": ["障碍物列表"],
  "risks": ["风险提示"]
}}
```""",
                variables=["start_position", "goal_position", "room_type", "obstacles", "robot_capabilities"],
                version=1,
            ),

            # 种子3：物体抓取策略
            PromptTemplate(
                id="seed_03",
                name="抓取策略",
                task_type="grasp_planning",
                template="""## 任务
分析目标物体的最佳抓取策略。

## 输入
- 物体类型：{object_type}
- 物体尺寸：{dimensions}
- 物体材质：{material}
- 机器人手类型：{gripper_type}

## 输出
```json
{{
  "grasp_points": [[x,y,z], ...],
  "grip_force": "light/medium/heavy",
  "approach_angle": 角度值,
  "success_probability": 0.0到1.0,
  "alternatives": ["备选方案"]
}}
```""",
                variables=["object_type", "dimensions", "material", "gripper_type"],
                version=1,
            ),

            # 种子4：物理常识推理
            PromptTemplate(
                id="seed_04",
                name="物理推理",
                task_type="physics_reasoning",
                template="""## 任务
基于物理规律推理以下场景中会发生什么。

## 场景描述
{scene_description}

## 触发事件
{trigger_event}

## 输出
```json
{{
  "prediction": "预测结果",
  "confidence": 0.0到1.0,
  "reasoning": "推理过程",
  "uncertainty_factors": ["不确定因素"]
}}
```""",
                variables=["scene_description", "trigger_event"],
                version=1,
            ),
        ]

        for seed in seeds:
            self.prompts.append(seed)
        self._save()
        print(f"[PromptRegistry] [SEED] 种下 {len(seeds)} 颗 Prompt 种子")

    def register(self, prompt: PromptTemplate) -> str:
        """注册新 Prompt"""
        self.prompts.append(prompt)
        self._save()
        return prompt.id

    def get(self, task_type: str) -> Optional[PromptTemplate]:
        """
        根据任务类型获取最优 Prompt
        选择策略：Thompson Sampling（汤普森采样）
        —— 不总是选成功率最高的，而是按概率分布采样
        """
        candidates = [p for p in self.prompts if p.task_type == task_type]
        if not candidates:
            return None

        # 简单版本：优先选择成功率高的
        # 进阶版本：Thompson Sampling（带探索）
        import random
        weights = []
        for p in candidates:
            # Beta分布采样：成功率越高，被选中的概率越大
            from math import sqrt
            alpha = max(p.performance["success"], 0.1)
            beta = max(p.performance["errors"], 0.1)
            # Beta采样
            import numpy as np
            try:
                sample = np.random.beta(alpha, beta)
            except Exception:
                sample = alpha / (alpha + beta)
            weights.append(sample)

        # 加权随机选择
        total = sum(weights)
        r = random.random() * total
        cumsum = 0
        for i, w in enumerate(weights):
            cumsum += w
            if cumsum >= r:
                return candidates[i]
        return candidates[0]

    def get_all(self, task_type: str) -> List[PromptTemplate]:
        """获取某类型的所有 Prompt 版本"""
        return [p for p in self.prompts if p.task_type == task_type]

    def evolve(self, prompt_id: str, feedback: Dict):
        """
        根据反馈进化 Prompt

        进化规则：
        - 成功率 > 80% → 保持
        - 成功率 50-80% → 轻微调优
        - 成功率 < 50% 且样本 > 5 → 自动分叉
        """
        for p in self.prompts:
            if p.id != prompt_id:
                continue

            p.performance["runs"] += 1
            if feedback.get("success"):
                p.performance["success"] += 1
            if feedback.get("rating"):
                p.performance["ratings"].append(feedback["rating"])
            if feedback.get("error"):
                p.performance["errors"] += 1

            rate = p.success_rate()
            runs = p.performance["runs"]

            # 进化条件
            if rate < 0.5 and runs >= 5:
                # 自动分叉：成功率低 → 生成新版本
                new_id = self._fork_version(p)
                print(f"[PromptRegistry] [FORK] Prompt {p.id} 分叉 → {new_id} (成功率: {rate:.1%})")
            elif rate < 0.7 and runs >= 3:
                # 轻微调整提示词
                print(f"[PromptRegistry] [TUNE] Prompt {p.id} 待调优 (成功率: {rate:.1%})")

            self._save()
            break

    def _fork_version(self, prompt: PromptTemplate) -> str:
        """分叉生成新版本"""
        new_id = f"fork_{str(uuid.uuid4())[:8]}"
        new_prompt = PromptTemplate(
            id=new_id,
            name=f"{prompt.name}_v{prompt.version + 1}",
            task_type=prompt.task_type,
            template=prompt.template,  # 初始相同
            variables=prompt.variables.copy(),
            version=prompt.version + 1,
            parent_id=prompt.id,
            performance={"runs": 0, "success": 0, "errors": 0, "avg_latency_ms": 0, "ratings": []},
        )
        self.prompts.append(new_prompt)
        return new_id

    def stats(self) -> Dict:
        """统计所有 Prompt 的表现"""
        result = {}
        for p in self.prompts:
            if p.task_type not in result:
                result[p.task_type] = {"versions": 0, "total_runs": 0, "avg_success": 0}
            result[p.task_type]["versions"] += 1
            result[p.task_type]["total_runs"] += p.performance["runs"]
            result[p.task_type]["avg_success"] += p.success_rate()

        for t in result:
            if result[t]["versions"] > 0:
                result[t]["avg_success"] /= result[t]["versions"]

        return result

    def _load(self):
        if not os.path.exists(self.storage_path):
            return
        try:
            data = json.load(open(self.storage_path, encoding="utf-8"))
            self.prompts = [PromptTemplate(**p) for p in data.get("prompts", [])]
        except Exception as e:
            print(f"[PromptRegistry] 加载失败: {e}")

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        json.dump({
            "prompts": [asdict(p) for p in self.prompts],
            "updated_at": datetime.now().isoformat(),
        }, open(self.storage_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
