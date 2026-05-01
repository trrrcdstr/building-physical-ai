"""
Harness v0 — 主运行器
把 Prompt + Context + Feedback + Guardrails + WorldModel 串成闭环
"""

import sys
import os
import json
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.harness.v0 import (
    PromptRegistry,
    ContextEngine,
    FeedbackLoop,
    Guardrails,
    WorldModel,
)
from typing import Dict, Any


class Harness:
    """
    建筑物理AI世界模型 Harness v0

    运行流程：
    1. 获取 Prompt（从注册表）
    2. 构建 Context（从记忆+知识）
    3. 执行推理（这里用规则引擎模拟，真实场景接LLM）
    4. Guardrails 检查
    5. 收集反馈 → 飞轮加速
    6. 世界模型预测
    """

    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = str(project_root)

        self.base_path = base_path

        # 初始化组件
        self.prompts = PromptRegistry(storage_path=f"{base_path}/data/harness/prompts.json")
        self.context = ContextEngine(memory_path=f"{base_path}/data/harness/memory.json")
        self.feedback = FeedbackLoop(storage_path=f"{base_path}/data/harness/feedback.json")
        self.guardrails = Guardrails()
        self.world_model = WorldModel()

        print("=" * 50)
        print("[BUILD]  Harness v0 已启动")
        print("=" * 50)
        print(f"  Prompt 种子: {len(self.prompts.prompts)} 个")
        print(f"  记忆条目: {len(self.context.short_term)} 短期 + {len(self.context.long_term)} 长期")
        print("=" * 50)

    def run(
        self,
        task_type: str,
        scene_data: dict,
        goal: str = None,
        rating: int = None,
    ) -> dict:
        """
        运行一次完整的推理流程

        参数:
            task_type: 任务类型 (scene_analysis / path_planning / grasp_planning / physics_reasoning)
            scene_data: 场景数据 {
                "scene_type": "residence",
                "room_category": "厨房",
                "dimensions": {"width": 5.2, "depth": 4.1, "height": 2.8},
                "physics_tags": ["潮湿", "狭窄通道"],
                "designer": "杭州萧山金灿装饰",
                "platform": "3d66",
                "vr_id": 123,
            }
            goal: 目标描述
            rating: 用户评分（可选）
        """
        start_time = time.time()

        # -- 1. 获取 Prompt --
        prompt_template = self.prompts.get(task_type)
        if not prompt_template:
            return {"error": f"未找到任务类型: {task_type}"}

        # -- 2. 构建 Context --
        ctx = self.context.build(task_type, scene_data)

        # -- 3. 生成完整提示词 --
        full_prompt = prompt_template.to_prompt(
            room_type=scene_data.get("room_category", ""),
            width=scene_data.get("dimensions", {}).get("width", 0),
            depth=scene_data.get("dimensions", {}).get("depth", 0),
            height=scene_data.get("dimensions", {}).get("height", 0),
            physics_tags=", ".join(scene_data.get("physics_tags", [])),
            start_position=scene_data.get("start_position", [0, 0, 0]),
            goal_position=scene_data.get("goal_position", [5, 0, 5]),
            obstacles=scene_data.get("obstacles", "无"),
            robot_capabilities=", ".join(scene_data.get("robot_capabilities", ["move", "grasp", "open"])),
            scene_description=scene_data.get("description", ""),
            trigger_event=goal or "观察",
            object_type=scene_data.get("object_type", "未知"),
            dimensions=scene_data.get("dimensions", {}),
            material=scene_data.get("material", "未知"),
            gripper_type=scene_data.get("gripper_type", "parallel"),
        )

        # -- 4. 执行推理（规则引擎模拟） --
        output = self._execute_rules(task_type, scene_data, prompt_template)

        # -- 5. Guardrails 检查 --
        guard_result = self.guardrails.check(ctx, output)
        if not guard_result.passed:
            print(f"[WARN] Guardrails 拦截: {guard_result.violations}")
            output = self.guardrails.fallback(ctx)

        # -- 6. 世界模型 --
        world_result = None
        if task_type == "scene_analysis":
            # 编码当前状态
            state = self.world_model.encode(scene_data)
            # 预测（无行动）
            predicted = self.world_model.predict(state, {"type": "observe"})
            world_result = self.world_model.decode(predicted)

        # -- 7. 记录反馈 --
        success = guard_result.passed and output.get("status") != "blocked"
        latency_ms = (time.time() - start_time) * 1000

        fb_result = self.feedback.record(
            prompt_id=prompt_template.id,
            task_type=task_type,
            context=ctx,
            output=output,
            success=success,
            rating=rating,
            latency_ms=latency_ms,
        )

        # -- 8. 更新记忆 --
        self.context.remember(ctx, output, success, rating)

        # -- 9. Prompt 进化 --
        self.prompts.evolve(prompt_template.id, {
            "success": success,
            "rating": rating,
        })

        return {
            "prompt_id": prompt_template.id,
            "prompt_name": prompt_template.name,
            "prompt_version": prompt_template.version,
            "full_prompt": full_prompt[:200] + "..." if len(full_prompt) > 200 else full_prompt,
            "output": output,
            "world_model": world_result,
            "guardrails": {
                "passed": guard_result.passed,
                "violations": guard_result.violations,
                "warning": guard_result.warning,
            },
            "feedback": fb_result,
            "latency_ms": round(latency_ms, 1),
            "stats": {
                "prompt_stats": self.prompts.stats(),
                "feedback_stats": self.feedback.get_stats(),
                "world_summary": self.world_model.get_world_summary(),
            }
        }

    def _execute_rules(self, task_type: str, scene_data: Dict, prompt: Any) -> Dict:
        """
        规则引擎执行器
        真实场景：这里接 LLM API
        现在：用规则模拟 LLM 输出
        """
        room_cat = scene_data.get("room_category", "其他")
        tags = scene_data.get("physics_tags", [])
        dims = scene_data.get("dimensions", {})

        if task_type == "scene_analysis":
            # 物理属性规则
            friction_map = {"厨房": 0.35, "卫生间": 0.25, "客厅": 0.5, "主卧": 0.45, "餐厅": 0.4, "楼梯": 0.5}
            friction = friction_map.get(room_cat, 0.4)
            fragility = 0.3 if "易碎" in tags else 0.1
            moisture = "潮湿" in tags or room_cat in ["厨房", "卫生间"]
            traversable = "狭窄" not in tags and room_cat not in ["设备间"]
            climbable = "楼梯" in room_cat or "台阶" in tags

            recommendations = []
            if moisture:
                recommendations.append("注意地面湿滑，建议先清洁干燥")
            if room_cat == "厨房":
                recommendations.append("台面高度约0.9m，注意物体放置位置")
            if "高差" in tags:
                recommendations.append("存在高度差，需要爬坡或绕行")

            return {
                "friction": friction,
                "fragility": fragility,
                "moisture_risk": moisture,
                "obstacle_risk": "障碍物" in tags,
                "traversable": traversable,
                "climbable": climbable,
                "recommendations": recommendations,
                "safety_notes": ["保持环境干燥", "注意避障"] if tags else [],
            }

        elif task_type == "path_planning":
            return {
                "path": [[0, 0, 0], [2, 0, 0], [4, 0, 0]],
                "estimated_time": 10,
                "obstacles_avoided": tags,
                "risks": ["地面湿滑"] if "潮湿" in tags else [],
            }

        elif task_type == "grasp_planning":
            return {
                "grasp_points": [[0.5, 0.2, 0.3]],
                "grip_force": "medium",
                "approach_angle": 45,
                "success_probability": 0.85,
                "alternatives": ["侧面抓取", "底部托举"],
            }

        elif task_type == "physics_reasoning":
            return {
                "prediction": f"{room_cat}场景的物理行为预测",
                "confidence": 0.8,
                "reasoning": f"基于{room_cat}的物理属性进行推理",
                "uncertainty_factors": ["物体位置不确定", "地面条件变化"],
            }

        return {"status": "unknown_task"}

    def interactive_demo(self):
        """
        交互式演示
        """
        print("\n[DEMO] Harness 交互演示")
        print("-" * 40)

        test_cases = [
            {
                "task_type": "scene_analysis",
                "scene_data": {
                    "scene_type": "residence",
                    "room_category": "厨房",
                    "dimensions": {"width": 5.2, "depth": 4.1, "height": 2.8},
                    "physics_tags": ["潮湿", "地面湿滑", "台面高度0.9m"],
                    "designer": "杭州萧山金灿装饰",
                    "platform": "3d66",
                    "vr_id": 42,
                },
                "goal": "分析厨房物理属性",
                "rating": 5,
            },
            {
                "task_type": "scene_analysis",
                "scene_data": {
                    "scene_type": "residence",
                    "room_category": "卫生间",
                    "dimensions": {"width": 3.0, "depth": 2.5, "height": 2.6},
                    "physics_tags": ["潮湿", "防水", "地面湿滑"],
                    "designer": "鸿盛设计",
                    "platform": "Justeasy",
                    "vr_id": 15,
                },
                "goal": "分析卫生间物理属性",
                "rating": 4,
            },
        ]

        for i, case in enumerate(test_cases):
            print(f"\n[{i+1}] 测试: {case['scene_data']['room_category']}")
            print(f"    任务: {case['task_type']}")
            result = self.run(**case)
            print(f"    输出: {json.dumps(result['output'], ensure_ascii=False, indent=4)[:200]}")
            print(f"    Guardrails: {'[OK] 通过' if result['guardrails']['passed'] else '❌ 拦截'}")
            print(f"    延迟: {result['latency_ms']}ms")

        # 飞轮统计
        print("\n[STATS] 飞轮统计:")
        stats = self.feedback.get_stats()
        print(f"  总反馈: {stats['total']}")
        print(f"  成功率: {stats['success_rate']:.1%}")
        print(f"  平均评分: {stats['avg_rating']}")
        print(f"  飞轮转速: {stats['flywheel_speed']}/小时")

        # Prompt进化
        print("\n[SEED] Prompt进化:")
        pstats = self.prompts.stats()
        for task, s in pstats.items():
            print(f"  {task}: {s['versions']}个版本, {s['total_runs']}次运行")

        # 世界模型
        print("\n[WORLD] 世界模型:")
        ws = self.world_model.get_world_summary()
        print(f"  状态数: {ws['total_states']}")
        print(f"  轨迹步数: {ws['trajectory_steps']}")


if __name__ == "__main__":
    harness = Harness()
    harness.interactive_demo()
