"""
机器人 Python Client - 连接世界模型 API
用法:
    from robot_client import RobotClient
    robot = RobotClient("http://localhost:5001")
    plan = robot.plan("帮我把沙发移到窗户旁边", target_object="沙发")
    print(plan.actions)  # ['移动']
    print(plan.risk)     # 'HIGH'
"""

import urllib.request
import urllib.error
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class PlanResult:
    """执行计划结果"""
    instruction: str
    target_object: str
    actions: list
    risk: str
    duration: float
    similar_tasks: list
    physics_checks: list
    execution_ready: bool
    
    @property
    def is_safe(self) -> bool:
        return self.risk in ["LOW", "MEDIUM"] and self.execution_ready


class RobotClient:
    """机器人 API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:5001", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        # 验证连接
        try:
            req = urllib.request.Request(f"{self.base_url}/api/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                health = json.loads(resp.read())
            print(f"[RobotClient] Connected to {base_url}")
            print(f"  Version: {health.get('version')}")
            print(f"  Scene: {health.get('scene_graph', {}).get('total_nodes', 0)} nodes")
            print(f"  GPU: {health.get('gpu', 'N/A')}")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to {base_url}: {e}")
    
    def _post(self, endpoint: str, payload: dict) -> dict:
        """通用 POST 请求"""
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{endpoint}",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())
    
    def _get(self, endpoint: str) -> dict:
        """通用 GET 请求"""
        req = urllib.request.Request(f"{self.base_url}{endpoint}")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read())
    
    def plan(self, instruction: str, target_object: str = None,
             target_x: float = None, target_z: float = None,
             surface_width: float = 1.5, surface_depth: float = 1.0,
             material: str = "木材") -> PlanResult:
        """
        获取执行计划
        
        Args:
            instruction: 自然语言指令，如"帮我把沙发移到窗户旁边"
            target_object: 目标物体名称，如"沙发"
            target_x: 目标位置X坐标（可选）
            target_z: 目标位置Z坐标（可选）
            surface_width: 物体宽度（米）
            surface_depth: 物体深度（米）
            material: 材质类型
        
        Returns:
            PlanResult: 执行计划
        """
        payload = {
            "instruction": instruction,
            "target_object": target_object,
            "surface_width": surface_width,
            "surface_depth": surface_depth,
            "material": material,
        }
        if target_x is not None:
            payload["target_x"] = target_x
        if target_z is not None:
            payload["target_z"] = target_z
        
        resp = self._post("/api/vla/instruction", payload)
        
        plan = resp["plan"]
        return PlanResult(
            instruction=instruction,
            target_object=target_object,
            actions=[a["primitive"] for a in plan["action_sequence"]],
            risk=plan["risk_level"],
            duration=plan["estimated_duration_s"],
            similar_tasks=[t["task"] for t in plan["similar_tasks"]],
            physics_checks=plan["physics_checks"],
            execution_ready=plan["execution_ready"],
        )
    
    def infer(self, instruction: str, target_object: str = None) -> dict:
        """
        端到端推理（更简洁的接口）
        """
        payload = {"instruction": instruction}
        if target_object:
            payload["target_object"] = target_object
        
        return self._post("/api/infer", payload)
    
    def can_push(self, object_type: str, mass: float, surface_material: str = "木材") -> bool:
        """检查能否推动某物体"""
        resp = self._post("/api/physics/can_push", {
            "object_type": object_type,
            "surface_material": surface_material
        })
        return resp["can_move"]
    
    def check_rule(self, rule_name: str, value: float) -> dict:
        """检查是否符合建筑规范"""
        return self._post("/api/rules/check", {"rule_name": rule_name, "value": value})
    
    def get_scene_stats(self) -> dict:
        """获取场景统计"""
        return self._get("/api/scene/stats")
    
    def close(self):
        pass  # 无需关闭 urllib


# ─────────────────────────────────────────────
# 示例用法
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    
    # 连接机器人 API
    robot = RobotClient("http://localhost:5001")
    
    # 示例 1: 移动沙发
    print("\n" + "=" * 50)
    print("Example 1: 移动沙发")
    print("=" * 50)
    plan = robot.plan("帮我把沙发移到窗户旁边", target_object="沙发")
    print(f"指令: {plan.instruction}")
    print(f"目标: {plan.target_object}")
    print(f"动作序列: {plan.actions}")
    print(f"风险等级: {plan.risk}")
    print(f"预计耗时: {plan.duration}s")
    print(f"可执行: {plan.execution_ready}")
    print(f"物理检查: {plan.physics_checks}")
    print(f"相似任务: {plan.similar_tasks[:3]}")
    
    # 示例 2: 清洁地面
    print("\n" + "=" * 50)
    print("Example 2: 清洁客厅地板")
    print("=" * 50)
    plan2 = robot.plan("清洁客厅地板", target_object="地板")
    print(f"动作序列: {plan2.actions}")
    print(f"风险等级: {plan2.risk}")
    print(f"可执行: {plan2.is_safe}")
    
    # 示例 3: 推送能力检查
    print("\n" + "=" * 50)
    print("Example 3: 物理检查")
    print("=" * 50)
    print(f"能否推动 45kg 沙发: {robot.can_push('沙发', 45.0, '实木地板')}")
    print(f"能否推动 80kg 床: {robot.can_push('床', 80.0, '瓷砖')}")
    
    # 示例 4: 规则检查
    print("\n" + "=" * 50)
    print("Example 4: 规则检查")
    print("=" * 50)
    r = robot.check_rule("无障碍通道宽度", 1.5)
    print(f"1.5m 无障碍通道: {r['status']}")
    r = robot.check_rule("疏散走道宽度", 1.2)
    print(f"1.2m 疏散走道: {r['status']}")
    
    robot.close()
    print("\n[Done]")
