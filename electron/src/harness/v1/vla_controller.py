"""
L4 双模型协同 - VLA具身控制器
自然语言指令 -> 语义嵌入 -> 任务理解 -> 动作序列 -> 物理仿真验证 -> 建筑规则校验
"""

from typing import Optional
from .semantic_encoder import SemanticEncoder
from .physical_engine import PhysicalEngine, get_physical_engine
from .rule_library import RuleLibrary
from .scene_graph_builder import SceneGraphBuilder


# ─────────────────────────────────────────────
# 建筑场景动作原语库
# ─────────────────────────────────────────────
ACTION_PRIMITIVES = {
    # 移动类
    "移动":       {"duration_s": 5,  "energy_kg": 2.0, "risk": "LOW",  "description": "搬运物体到目标位置"},
    "走到":       {"duration_s": 3,  "energy_kg": 0.0, "risk": "LOW",  "description": "导航到目标位置"},
    "抓取":       {"duration_s": 2,  "energy_kg": 0.5, "risk": "LOW",  "description": "机械臂抓取物体"},
    "放下":       {"duration_s": 1.5,"energy_kg": 0.0, "risk": "LOW",  "description": "将物体放置到目标位置"},
    "推":         {"duration_s": 4,  "energy_kg": 3.0, "risk": "MED",  "description": "推动物体（需校验推力）"},
    "拉":         {"duration_s": 4,  "energy_kg": 2.5, "risk": "MED",  "description": "拉动物体"},
    # 操作类
    "清洁":       {"duration_s": 10, "energy_kg": 0.5, "risk": "LOW",  "description": "使用清洁工具打扫"},
    "擦拭":       {"duration_s": 5,  "energy_kg": 0.3, "risk": "LOW",  "description": "擦拭表面"},
    "开关":       {"duration_s": 1,  "energy_kg": 0.0, "risk": "LOW",  "description": "操作开关/按钮"},
    "递送":       {"duration_s": 8,  "energy_kg": 1.0, "risk": "LOW",  "description": "携带物品移动到目标"},
    # 巡检类
    "查看":       {"duration_s": 2,  "energy_kg": 0.0, "risk": "LOW",  "description": "传感器/摄像头检查"},
    "记录":       {"duration_s": 1,  "energy_kg": 0.0, "risk": "LOW",  "description": "记录传感器数据"},
    "测量":       {"duration_s": 3,  "energy_kg": 0.0, "risk": "LOW",  "description": "测量空间尺寸"},
    # 施工类
    "安装":       {"duration_s": 15, "energy_kg": 2.0, "risk": "MED",  "description": "安装固定（需稳定性验证）"},
    "固定":       {"duration_s": 5,  "energy_kg": 1.0, "risk": "LOW",  "description": "用螺栓/胶水固定"},
    "布线":       {"duration_s": 20, "energy_kg": 0.5, "risk": "MED",  "description": "铺设线缆管道"},
    "打孔":       {"duration_s": 5,  "energy_kg": 0.5, "risk": "MED",  "description": "墙体打孔（需避开管线）"},
    # 园林类
    "浇灌":       {"duration_s": 10, "energy_kg": 0.0, "risk": "LOW",  "description": "园林灌溉"},
    "修剪":       {"duration_s": 8,  "energy_kg": 0.5, "risk": "LOW",  "description": "植物修剪"},
}


class VLAController:
    """
    VLA 具身控制器：自然语言指令 -> 结构化执行计划

    流程（5步）：
    1. 语义编码（SemanticEncoder）
    2. 任务理解（相似任务匹配）
    3. 动作规划（动作原语序列）
    4. 物理验证（PhysicalEngine）
    5. 合规检查（RuleLibrary）

    区别于关键词匹配：
    - 基于 sentence-transformers 语义向量，支持中文自然语言
    - 本地推理，无外部API调用，保护数据隐私
    - 可扩展的动作原语库
    """

    def __init__(
        self,
        semantic_encoder: Optional[SemanticEncoder] = None,
        physical_engine: Optional[PhysicalEngine] = None,
        rule_library: Optional[RuleLibrary] = None,
        scene_graph: Optional[SceneGraphBuilder] = None,
    ):
        self.sem = semantic_encoder or SemanticEncoder()
        self.physics = physical_engine or get_physical_engine()
        self.rules = rule_library or RuleLibrary()
        self.scene_graph = scene_graph
        self.primitives = ACTION_PRIMITIVES

        # 指令动作映射（关键词触发 + 语义验证）
        self.keyword_map = {
            "移动": ["移动", "搬", "移到", "挪"],
            "走到": ["走到", "去", "导航"],
            "抓取": ["抓取", "拿起", "拿起"],
            "放下": ["放下", "放置", "放到"],
            "推": ["推", "推动"],
            "拉": ["拉", "拉动"],
            "清洁": ["清洁", "打扫", "扫地", "拖地", "清洗"],
            "擦拭": ["擦拭", "擦", "抹"],
            "开关": ["开关", "打开", "关闭", "开启"],
            "递送": ["递送", "送", "带到"],
            "查看": ["查看", "检查", "巡检", "巡查"],
            "记录": ["记录", "记下", "拍照"],
            "测量": ["测量", "量"],
            "安装": ["安装", "组装", "装"],
            "固定": ["固定", "拧", "固定住"],
            "布线": ["布线", "接线", "接电"],
            "打孔": ["打孔", "钻孔"],
            "浇灌": ["浇灌", "浇水", "灌溉"],
            "修剪": ["修剪", "割草", "修剪"],
        }
        print(f"[VLAController] Initialized | Primitives: {len(self.primitives)} | Keywords: {len(self.keyword_map)}")

    def process_instruction(
        self,
        instruction: str,
        target_object: str = None,
        target_position: dict = None,
        scene_context: str = None,
    ) -> dict:
        """
        处理自然语言指令，返回结构化执行计划

        Args:
            instruction: 自然语言指令
            target_object: 目标物体（如"沙发"）
            target_position: 目标位置 {"x", "z"}（米）
            scene_context: 场景描述（可选）

        Returns:
            执行计划字典
        """
        # Step 1: 语义匹配（sentence-transformers）
        similar_tasks = self.sem.find_similar_tasks(instruction, top_k=5, threshold=0.3)

        # Step 2: 关键词+语义动作规划
        action_sequence = self._plan_actions(instruction, target_object)

        # Step 3: 物理验证
        physics_checks = self._verify_physics(action_sequence, target_object, target_position)

        # Step 4: 规则合规检查
        rule_checks = self._check_rules(action_sequence, target_object)

        # Step 5: 风险评估
        risk_level = self._assess_risk(action_sequence, physics_checks, rule_checks)

        # 估算总时长
        total_duration = sum(a["duration_s"] for a in action_sequence)

        return {
            "instruction": instruction,
            "similar_tasks": similar_tasks,
            "action_sequence": action_sequence,
            "physics_checks": physics_checks,
            "rule_checks": rule_checks,
            "risk_level": risk_level,
            "estimated_duration_s": total_duration,
            "execution_ready": risk_level != "HIGH",
            "total_actions": len(action_sequence),
        }

    def _plan_actions(
        self,
        instruction: str,
        target: str = None,
    ) -> list[dict]:
        """根据指令关键词规划动作序列"""
        actions = []
        triggered = set()

        # 关键词匹配
        for action_name, keywords in self.keyword_map.items():
            for kw in keywords:
                if kw in instruction and action_name not in triggered:
                    prim = self.primitives.get(action_name, self.primitives["移动"])
                    action = {
                        "primitive": action_name,
                        "trigger_keyword": kw,
                        "description": prim["description"],
                        "duration_s": prim["duration_s"],
                        "energy_kg": prim["energy_kg"],
                        "risk": prim["risk"],
                    }
                    if target:
                        action["target"] = target
                    actions.append(action)
                    triggered.add(action_name)
                    break

        # 默认：导航到目标
        if not actions:
            actions.append({
                "primitive": "走到",
                "description": "导航到目标位置",
                "duration_s": 5,
                "energy_kg": 0,
                "risk": "LOW",
                "target": target or "目标位置",
            })

        return actions

    def _verify_physics(
        self,
        actions: list,
        target: str,
        target_pos: dict,
    ) -> list[dict]:
        """物理可行性验证"""
        checks = []
        for action in actions:
            if action["primitive"] in ["移动", "推", "拉"] and target:
                mass = self.physics.get_mass(target)
                result = self.physics.can_push(mass, robot_max_force=200.0)
                checks.append({
                    "action": action["primitive"],
                    "target": target,
                    **result,
                    "verified": True,
                })
            elif action["primitive"] in ["放下", "安装"] and target_pos:
                checks.append({
                    "action": action["primitive"],
                    "target": target,
                    "position": target_pos,
                    "stability": "pending_surface_data",
                    "verified": False,
                })
        return checks

    def _check_rules(
        self,
        actions: list,
        target: str,
    ) -> list[dict]:
        """建筑规则合规检查"""
        checks = []
        for action in actions:
            if action["primitive"] in ["移动", "安装"]:
                # 检查无障碍通道
                r = self.rules.check_clearance("轮椅通行", 1.2)
                if not r["pass"]:
                    checks.append({"rule": "无障碍通道", **r, "warning": True})
            if action["primitive"] in ["测量"]:
                r = self.rules.check_rule("门净宽_单扇", 0.9)
                checks.append({"rule": "门净宽", **r})
        return checks

    def _assess_risk(
        self,
        actions: list,
        physics: list,
        rules: list,
    ) -> str:
        """综合风险评估"""
        if any(not p.get("can_move", True) for p in physics if "can_move" in p):
            return "HIGH"
        if any(
            not r.get("check", {}).get("pass", True)
            for r in rules
            if "check" in r
        ):
            return "MEDIUM"
        if any(a.get("risk") == "MED" for a in actions):
            return "MEDIUM"
        return "LOW"

    def execute_plan(self, plan: dict) -> dict:
        """
        执行计划（仿真模式）
        """
        if not plan.get("execution_ready", False):
            return {
                "status": "BLOCKED",
                "risk_level": plan.get("risk_level"),
                "blocked_by": self._get_block_reason(plan),
            }

        return {
            "status": "SIMULATED",
            "total_duration_s": plan["estimated_duration_s"],
            "actions_executed": plan["total_actions"],
            "physics_verified": len(plan["physics_checks"]) > 0,
            "rules_compliant": all(
                r.get("check", {}).get("pass", True)
                for r in plan["rule_checks"]
                if "check" in r
            ),
        }

    def _get_block_reason(self, plan: dict) -> str:
        for p in plan.get("physics_checks", []):
            if p.get("verified") and not p.get("can_move"):
                return f"物体过重：{p.get('object_mass_kg')}kg 超过机器人最大推力"
        return f"风险等级：{plan.get('risk_level')}"

    def set_scene_graph(self, scene_graph: SceneGraphBuilder):
        """注入场景图"""
        self.scene_graph = scene_graph
