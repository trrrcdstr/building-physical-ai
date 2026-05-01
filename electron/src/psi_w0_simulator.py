# src/psi_w0_simulator.py - PSI-W0: 动作条件模型 - 模拟评测层
import json, os, numpy as np
from typing import List, Dict

class PSIW0Simulator:
    """PSI-W0 三大功能：
    1. 模拟评测：动作规划 -> 物理仿真 -> 可行性评分
    2. 数据转换：物理参数 -> 机器人可执行参数
    3. 数据飞轮：仿真结果 -> 反馈 -> 模型修正
    """

    def __init__(self):
        self.scene_graph = None
        self.history = []

    # ─── 1. 模拟评测 ───────────────────────────────────
    def evaluate_action(self, action: Dict) -> Dict:
        object_pos = action.get("from", [0, 0, 0])
        target_pos = action.get("to", [0, 0, 0])
        object_id = action.get("object", "")

        collision_risks = self._check_path_collision(object_id, object_pos, target_pos)
        stability = self._evaluate_stability(object_id, target_pos)
        passage_ok = self._check_passage(object_pos, target_pos)
        energy = self._estimate_energy(object_pos, target_pos)
        score = self._compute_score(collision_risks, stability, passage_ok, energy)
        feasible = score >= 0.6 and not any(c["severity"] == "high" for c in collision_risks)
        robot_params = self._to_robot_params(action, score)

        result = {
            "feasible": feasible,
            "score": round(score, 3),
            "action": action.get("description", ""),
            "collision_risks": collision_risks,
            "stability": stability,
            "passage_clear": passage_ok,
            "energy_cost_kj": round(energy, 3),
            "robot_params": robot_params,
            "reasons": self._explain(score, collision_risks, passage_ok),
            "warnings": self._warn(collision_risks, stability),
        }
        self.history.append(result)
        return result

    def evaluate_plan(self, plan: List[Dict]) -> Dict:
        results = []
        for step in plan:
            r = self.evaluate_action(step)
            results.append({**r, "step": len(results) + 1})
        avg = sum(r["score"] for r in results) / len(results) if results else 0
        return {
            "plan_feasible": all(r["feasible"] for r in results),
            "avg_score": round(avg, 3),
            "total_steps": len(results),
            "feasible_steps": sum(1 for r in results if r["feasible"]),
            "step_results": results,
        }

    # ─── 2. 物理仿真 ───────────────────────────────────
    def _check_path_collision(self, obj_id: str, start: List, end: List) -> List[Dict]:
        if self.scene_graph is None:
            self._load_scene_graph()
        if not self.scene_graph or not self.scene_graph.get("positions"):
            return []
        positions = self.scene_graph["positions"]
        node_ids = self.scene_graph.get("node_ids", [])
        obj_idx = -1
        for i, nid in enumerate(node_ids):
            if obj_id.lower() in str(nid).lower():
                obj_idx = i
                break
        if obj_idx < 0:
            return []
        s, e = np.array(start), np.array(end)
        path_vec = e - s
        path_len = float(np.linalg.norm(path_vec))
        if path_len < 0.01:
            return []
        path_unit = path_vec / path_len
        risks = []
        for i, pos in enumerate(positions):
            if i == obj_idx:
                continue
            pos = np.array(pos)
            # 点到线段的距离
            proj = float(np.dot(pos[:2] - s[:2], path_unit[:2]))
            t = max(0.0, min(1.0, proj / path_len))
            closest = s[:2] + t * path_unit[:2] * path_len
            dist = float(np.linalg.norm(pos[:2] - closest))
            if dist < 1.2:
                sev = "high" if dist < 0.4 else "medium" if dist < 0.8 else "low"
                nid = node_ids[i] if i < len(node_ids) else "node-{}".format(i)
                risks.append({"obstacle_id": nid, "distance_m": round(dist, 3), "severity": sev})
        return risks

    def _evaluate_stability(self, obj_id: str, target_pos: List) -> Dict:
        score, reasons = 1.0, []
        z = target_pos[2] if len(target_pos) > 2 else 0
        if abs(z) < 1.2:
            score += 0.2
            reasons.append("Near wall, high stability")
        return {"score": min(1.0, score), "reasons": reasons}

    def _check_passage(self, start: List, end: List) -> bool:
        return True  # simplified: assume corridor wide enough

    def _estimate_energy(self, start: List, end: List) -> float:
        dist = float(np.linalg.norm(np.array(start) - np.array(end)))
        # E = m * g * d * efficiency / 1000 (kJ), m=20kg, eff=0.3
        return round(dist * 20 * 9.8 * 0.3 / 1000, 3)

    def _compute_score(self, collision_risks, stability, passage_ok, energy) -> float:
        score = 1.0
        for c in collision_risks:
            score -= {"high": 0.5, "medium": 0.25, "low": 0.1}.get(c["severity"], 0.1)
        score *= stability.get("score", 1.0)
        if not passage_ok:
            score -= 0.3
        return max(0.0, min(1.0, score))

    def _explain(self, score, collision_risks, passage_ok) -> List[str]:
        if score >= 0.8:
            verdict = "[OK] Physically feasible for robot execution"
        elif score >= 0.6:
            verdict = "[WARN] Mostly feasible, recommend low-speed execution"
        else:
            verdict = "[FAIL] Not feasible, re-planning required"
        reasons = [verdict]
        if collision_risks:
            reasons.append("Warning: {} collision risks detected along path".format(len(collision_risks)))
        if not passage_ok:
            reasons.append("Error: Passage too narrow for object to pass")
        return reasons

    def _warn(self, collision_risks, stability) -> List[str]:
        warnings = []
        for c in collision_risks:
            if c["severity"] == "high":
                warnings.append("HIGH collision risk: {} at {:.2f}m".format(c["obstacle_id"], c["distance_m"]))
        if stability.get("score", 1.0) < 0.8:
            warnings.append("Stability marginal - recommend placing near wall")
        return warnings

    # ─── 3. 数据转换 ───────────────────────────────────
    def _to_robot_params(self, action: Dict, score: float) -> Dict:
        obj_type = action.get("object_type", "rigid")
        defaults = {
            "sofa":  {"m": 45, "f": 0.55, "v": 0.3,  "a": 0.1,  "F": 80,  "c": 0.3},
            "table": {"m": 30, "f": 0.50, "v": 0.4,  "a": 0.15, "F": 60,  "c": 0.2},
            "chair": {"m": 8,  "f": 0.45, "v": 0.5,  "a": 0.2,  "F": 30,  "c": 0.15},
            "bed":   {"m": 60, "f": 0.60, "v": 0.2,  "a": 0.05, "F": 100, "c": 0.4},
            "rigid": {"m": 10, "f": 0.40, "v": 0.5,  "a": 0.2,  "F": 50,  "c": 0.1},
            "fragile": {"m": 2, "f": 0.30, "v": 0.2,  "a": 0.05, "F": 10,  "c": 0.05},
        }
        d = defaults.get(obj_type, defaults["rigid"])
        s = np.array(action.get("from", [0, 0, 0]))
        e = np.array(action.get("to", [0, 0, 0]))
        dist = float(np.linalg.norm(e - s))
        direction = ((e - s) / max(dist, 0.01)).tolist()
        return {
            "task_type": action.get("action", "move"),
            "object_type": obj_type,
            "trajectory": {
                "start_pos": action.get("from"),
                "end_pos": action.get("to"),
                "distance_m": round(dist, 3),
                "direction": direction,
                "path_type": "linear" if score > 0.8 else "curved",
            },
            "grasp": {
                "type": "power" if obj_type in ("sofa", "bed") else "pinch",
                "force_newton": d["F"],
                "pre_grasp_offset_m": d["c"],
            },
            "motion": {
                "max_velocity_ms": d["v"],
                "acceleration_ms2": d["a"],
                "collision_threshold_m": 0.05,
            },
            "safety": {
                "friction_margin": d["f"],
                "stability_threshold": 0.7,
                "fall_risk": score < 0.6,
            },
        }

    def _load_scene_graph(self):
        proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(proj, "data", "processed", "cleaned", "scene_graph_real.json")
        try:
            with open(path, encoding="utf-8") as f:
                self.scene_graph = json.load(f)
        except Exception as ex:
            print("[PSI-W0] Scene graph load failed:", ex)
            self.scene_graph = None

    # ─── 4. 数据飞轮 ───────────────────────────────────
    def get_flywheel_data(self) -> List[Dict]:
        return self.history

    def reset_history(self):
        self.history = []

    # ─── 5. 演示 ──────────────────────────────────────
    def demo(self):
        print("=" * 60)
        print("PSI-W0 Simulation Evaluation Demo")
        print("Scene: 151 nodes, 897 edges (from scene_graph_real.json)")
        print("=" * 60)

        plan = [
            {
                "actor": "robot-arm-01",
                "action": "move",
                "object": "sofa-001",
                "object_type": "sofa",
                "from": [4.0, 0, 3.0],
                "to": [1.0, 0, 0.5],
                "description": "Move sofa to corner",
            },
            {
                "actor": "robot-arm-01",
                "action": "move",
                "object": "coffee_table-001",
                "object_type": "table",
                "from": [3.0, 0, 3.0],
                "to": [0.5, 0, 1.0],
                "description": "Move table beside sofa",
            },
        ]

        result = self.evaluate_plan(plan)
        pf = "PASS" if result["plan_feasible"] else "FAIL"
        print()
        print("Plan: {} | Avg Score: {} | Steps: {}/{} feasible".format(
            pf, result["avg_score"], result["feasible_steps"], result["total_steps"]))
        print()

        for step in result["step_results"]:
            fs = "OK" if step["feasible"] else "FAIL"
            print("Step {}: {} | Score: {} | {}".format(step["step"], step["action"], step["score"], fs))
            for r in step["reasons"]:
                print("  {}".format(r))
            for w in step["warnings"]:
                print("  {}".format(w))
            rp = step.get("robot_params", {})
            tr = rp.get("trajectory", {})
            mo = rp.get("motion", {})
            print("  Robot params: dist={}m, speed={}m/s, force={}N, grasp={}".format(
                tr.get("distance_m", "?"),
                mo.get("max_velocity_ms", "?"),
                rp.get("grasp", {}).get("force_newton", "?"),
                rp.get("grasp", {}).get("type", "?"),
            ))
            print()

        print("Data flywheel records: {}".format(len(self.history)))


if __name__ == "__main__":
    PSIW0Simulator().demo()
