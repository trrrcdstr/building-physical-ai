"""
L2: Context 引擎
让 Prompt 知道"上下文"——记忆+知识+场景
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json
import os
import hashlib
from datetime import datetime


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str = ""
    content: str = ""
    type: str = "fact"    # "fact" | "preference" | "task" | "error" | "insight"
    timestamp: str = ""
    importance: float = 0.5   # 0-1，越高越重要
    tags: List[str] = field(default_factory=list)
    source: str = "system"     # "system" | "user" | "feedback" | "observation"

    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(f"{self.content}{self.timestamp}".encode()).hexdigest()[:12]
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Context:
    """L2 Context — 完整的推理上下文"""
    prompt_id: str
    task_type: str

    # 场景数据
    scene_type: str = ""        # "residence" | "mall" | ...
    vr_id: Optional[int] = None
    room_name: str = ""
    room_category: str = ""
    dimensions: Dict[str, float] = field(default_factory=lambda: {"width": 0, "depth": 0, "height": 0})
    physics_tags: List[str] = field(default_factory=list)
    designer: str = ""
    platform: str = ""

    # 记忆
    recent_tasks: List[str] = field(default_factory=list)     # 短期记忆
    learned_facts: List[Dict] = field(default_factory=list)   # 长期记忆
    error_history: List[str] = field(default_factory=list)     # 错误历史

    # 机器人状态
    robot_capabilities: List[str] = field(default_factory=lambda: ["move", "grasp", "open", "push"])
    robot_position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_llm_prompt(self) -> str:
        """构建给 LLM 的完整提示词"""
        parts = []

        parts.append("## 任务")
        parts.append(f"分析以下{self.scene_type}场景的物理属性和机器人交互策略。")

        parts.append("\n## 场景信息")
        parts.append(f"- 房间类型：{self.room_category}")
        parts.append(f"- 尺寸：{self.dimensions['width']}m × {self.dimensions['depth']}m × {self.dimensions['height']}m")
        if self.designer:
            parts.append(f"- 设计师：{self.designer}")
        if self.physics_tags:
            parts.append(f"- 物理标签：{', '.join(self.physics_tags)}")

        if self.learned_facts:
            parts.append("\n## 相关物理知识")
            for fact in self.learned_facts[:4]:
                parts.append(f"- [{fact.get('type', 'fact')}] {fact.get('content', '')}")

        if self.error_history:
            parts.append(f"\n[WARN] 历史错误：{self.error_history[-1]}")

        parts.append("\n## 机器人能力")
        parts.append(f"- 可用能力：{', '.join(self.robot_capabilities)}")
        parts.append(f"- 当前位置：{self.robot_position}")

        parts.append("\n## 输出要求")
        parts.append("仅输出JSON，不要有其他文字。")

        return "\n".join(parts)


# -------------------------------------------------
# 内置物理知识库（可扩展）
# -------------------------------------------------
PHYSICS_KNOWLEDGE = {
    "厨房": {
        "friction": 0.35,
        "moisture_risk": True,
        "obstacle_risk": True,
        "notes": ["地面潮湿需防滑", "台面高度约0.9m", "刀具需小心抓取", "热源需远离"],
        "safe_actions": ["move_carefully", "avoid_wet_areas"],
    },
    "卫生间": {
        "friction": 0.25,
        "moisture_risk": True,
        "obstacle_risk": False,
        "notes": ["地面湿滑风险高", "空间狭小限制移动", "防水要求严格"],
        "safe_actions": ["dry_mop_first", "move_slowly"],
    },
    "客厅": {
        "friction": 0.5,
        "moisture_risk": False,
        "obstacle_risk": True,
        "notes": ["地面摩擦适中", "空间开阔适合移动", "沙发区域需要避障"],
        "safe_actions": ["navigate_around_furniture"],
    },
    "主卧": {
        "friction": 0.45,
        "moisture_risk": False,
        "obstacle_risk": True,
        "notes": ["地毯区域摩擦力大", "衣柜门可开启", "床体不可移动"],
        "safe_actions": ["avoid_soft_floor_rushing"],
    },
    "餐厅": {
        "friction": 0.4,
        "moisture_risk": False,
        "obstacle_risk": True,
        "notes": ["餐桌可移动", "餐椅需轻推", "餐具需小心抓取"],
        "safe_actions": ["grasp_cutlery_carefully"],
    },
    "楼梯": {
        "friction": 0.5,
        "moisture_risk": True,
        "obstacle_risk": True,
        "notes": ["有高度差", "需要攀爬能力", "扶手可辅助"],
        "safe_actions": ["use_handrail", "watch_steps"],
    },
}


class ContextEngine:
    """
    L2: 上下文构建引擎

    设计哲学：
    - 不是把"所有数据"都塞给 LLM，而是只给"最相关的"
    - 记忆是分层的：最近任务 vs 重要经验 vs 物理知识
    - 知识是结构化的：不是黑盒，是可追溯的规则库
    """

    def __init__(self, memory_path: str = "data/harness/memory.json"):
        self.memory_path = memory_path
        self.short_term: List[MemoryEntry] = []   # 最近50条
        self.long_term: List[MemoryEntry] = []    # 重要记忆
        self._load()

    def build(self, task_type: str, scene_data: Dict) -> Context:
        """
        构建完整上下文

        scene_data 格式:
        {
            "scene_type": "residence",
            "vr_id": 123,
            "room_category": "厨房",
            "dimensions": {"width": 5.2, "depth": 4.1, "height": 2.8},
            "physics_tags": ["潮湿", "狭窄通道"],
            ...
        }
        """
        # 1. 检索相关记忆
        room_cat = scene_data.get("room_category", "")
        relevant = self._retrieve(room_cat, top_k=5)

        # 2. 获取近期任务
        recent = [m.content for m in self.short_term[-8:]]

        # 3. 获取错误历史
        errors = [m.content for m in self.long_term if m.type == "error"][-3:]

        # 4. 构建上下文
        ctx = Context(
            prompt_id=scene_data.get("prompt_id", "seed_01"),
            task_type=task_type,
            scene_type=scene_data.get("scene_type", "residence"),
            vr_id=scene_data.get("vr_id"),
            room_name=scene_data.get("room_name", ""),
            room_category=room_cat,
            dimensions=scene_data.get("dimensions", {"width": 0, "depth": 0, "height": 0}),
            physics_tags=scene_data.get("physics_tags", []),
            designer=scene_data.get("designer", ""),
            platform=scene_data.get("platform", ""),
            recent_tasks=recent,
            learned_facts=relevant,
            error_history=errors,
            metadata={
                "build_at": datetime.now().isoformat(),
                "version": "v0.1",
            }
        )

        return ctx

    def _retrieve(self, keyword: str, top_k: int = 5) -> List[Dict]:
        """
        检索相关知识（简单关键词匹配）

        升级路径：
        - v0.1: 关键词匹配（现在）
        - v0.2: 语义向量检索（用 embedding 模型）
        - v0.3: 知识图谱推理
        """
        results = []

        # 知识库检索
        for cat, knowledge in PHYSICS_KNOWLEDGE.items():
            if keyword in cat or cat in keyword:
                results.append({
                    "type": "physics_knowledge",
                    "category": cat,
                    "content": knowledge["notes"][0] if knowledge["notes"] else "",
                    "data": {k: v for k, v in knowledge.items() if k != "notes"},
                })

        # 长期记忆检索
        for m in self.long_term:
            if any(tag in m.tags for tag in [keyword, "physics", "error"]):
                results.append({
                    "type": m.type,
                    "category": m.tags[0] if m.tags else "general",
                    "content": m.content,
                })

        return results[:top_k]

    def remember(self, context: Context, result: Dict, success: bool, rating: Optional[int] = None):
        """
        记录执行结果到记忆

        核心原则：
        - 成功的经验 → 积累到"learned_facts"
        - 失败的经验 → 永久记忆，下次必查
        - 用户评分低 → 强化记忆
        """
        # 生成记忆内容
        entry_content = f"VR{context.vr_id} {context.room_category} → {'成功' if success else '失败'}"
        if rating:
            entry_content += f" (评分: {rating})"

        entry = MemoryEntry(
            content=entry_content,
            type="error" if not success else "task",
            importance=1.0 if not success else 0.6,
            tags=[context.room_category, context.scene_type, "success" if success else "error"],
            source="feedback",
        )

        # 短期记忆
        self.short_term.append(entry)

        # 失败 → 永久记忆
        if not success:
            # 提取失败原因
            if result.get("error"):
                error_entry = MemoryEntry(
                    content=f"失败原因: {result.get('error', '未知')}",
                    type="error",
                    importance=1.0,
                    tags=[context.room_category, "error"],
                    source="observation",
                )
                self.long_term.append(error_entry)

        # 高评分 → 重要经验
        if rating and rating >= 4:
            insight_entry = MemoryEntry(
                content=f"高评分({rating}): {context.room_category}场景表现优秀",
                type="insight",
                importance=0.8,
                tags=[context.room_category, "good_practice"],
                source="feedback",
            )
            self.long_term.append(insight_entry)

        # 限制记忆长度
        if len(self.short_term) > 50:
            self.short_term = self.short_term[-50:]

        # 长期记忆去重
        seen = set()
        unique_long_term = []
        for m in reversed(self.long_term):
            key = m.content[:50]
            if key not in seen:
                seen.add(key)
                unique_long_term.append(m)
        self.long_term = unique_long_term[-100:]

        self._save()

    def get_insights(self) -> List[str]:
        """获取系统学到的洞察"""
        insights = []
        for m in self.long_term:
            if m.type in ["insight", "error"]:
                insights.append(f"[{m.type}] {m.content}")
        return insights[-10:]

    def _load(self):
        if not os.path.exists(self.memory_path):
            return
        try:
            data = json.load(open(self.memory_path, encoding="utf-8"))
            self.short_term = [MemoryEntry(**e) for e in data.get("short_term", [])]
            self.long_term = [MemoryEntry(**e) for e in data.get("long_term", [])]
        except Exception as e:
            print(f"[ContextEngine] 加载失败: {e}")

    def _save(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        json.dump({
            "short_term": [asdict(e) for e in self.short_term],
            "long_term": [asdict(e) for e in self.long_term],
            "updated_at": datetime.now().isoformat(),
        }, open(self.memory_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
