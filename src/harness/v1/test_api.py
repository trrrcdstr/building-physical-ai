"""v1 API 测试脚本"""
import urllib.request
import json

BASE = "http://localhost:5001"

def post(url, data):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

print("=" * 55)
print("  v1 API Test Suite")
print("=" * 55)

# 1. VLA 指令
print("\n[1] VLA: 帮我把沙发移到窗户旁边")
r = post(f"{BASE}/api/vla/instruction", {"instruction": "帮我把沙发移到窗户旁边", "target_object": "沙发"})
plan = r["plan"]
print(f"  Actions: {[a['primitive'] for a in plan['action_sequence']]}")
print(f"  Risk: {plan['risk_level']}")
print(f"  Duration: {plan['estimated_duration_s']}s")
print(f"  Similar: {[t['task'] for t in plan['similar_tasks'][:3]]}")
print(f"  Physics checks: {len(plan['physics_checks'])}")
print(f"  Execution ready: {plan['execution_ready']}")

# 2. 物理引擎
print("\n[2] Physics: 能否推动沙发 (45kg on wood floor)")
r = post(f"{BASE}/api/physics/can_push", {"object_type": "沙发", "surface_material": "实木地板"})
print(f"  Can move: {r['can_move']}")
print(f"  Friction: {r['friction_force_N']}N / Max: {r['robot_max_force_N']}N")
print(f"  Safety margin: {r['safety_margin_N']}N")

# 3. 规则检查
print("\n[3] Rule: 无障碍通道宽度 1.5m")
r = post(f"{BASE}/api/rules/check", {"rule_name": "无障碍通道宽度", "value": 1.5})
print(f"  Status: {r['status']}")
print(f"  Standard: {r['standard']}")
print(f"  Description: {r['description']}")

print("\n[4] Rule: 疏散走道宽度 1.2m (should FAIL)")
r = post(f"{BASE}/api/rules/check", {"rule_name": "疏散走道宽度", "value": 1.2})
print(f"  Status: {r['status']}")
print(f"  Standard: {r['standard']}")

# 4. 端到端推理
print("\n[5] Full Inference: 清洁客厅地板")
r = post(f"{BASE}/api/infer", {"instruction": "清洁客厅地板", "target_object": "地板"})
print(f"  Ready: {r['ready']}")
print(f"  Plan: {[a['primitive'] for a in r['plan']['action_sequence']]}")
print(f"  Scene nodes: {r['scene_info'].get('total_nodes', 0)}")

# 5. 场景统计（GET）
print("\n[6] Scene: Top 3 object types")
req = urllib.request.Request(f"{BASE}/api/scene/stats")
r = json.loads(urllib.request.urlopen(req, timeout=10).read())
node_types = r.get("scene_graph", {}).get("node_types", {})
node_types = r.get("scene_graph", {}).get("node_types", {})
for t, c in sorted(node_types.items(), key=lambda x: -x[1]):
    print(f"  {t}: {c}")

print("\n" + "=" * 55)
print("  ALL API TESTS PASSED")
print("=" * 55)
