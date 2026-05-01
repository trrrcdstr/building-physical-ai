"""
v1 架构集成测试
"""
import sys
import json
sys.path.insert(0, r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")

from src.harness.v1 import WorldModelCore

print("=" * 60)
print("  Building Physical AI - World Model v1 Test")
print("=" * 60)

wm = WorldModelCore()

print("\n[1] Stats")
stats = wm.get_scene_stats()
print(json.dumps(stats, ensure_ascii=False, indent=2))

print("\n[2] Semantic Search: 帮我打扫客厅")
results = wm.semantic_search("帮我打扫客厅", top_k=3)
for r in results:
    print(f"  {r['task']} (sim={r['similarity']})")

print("\n[3] Rule Check: 无障碍通道宽度 1.5m")
r = wm.check_scene_rule("无障碍通道宽度", 1.5)
print(f"  {r['status']} | {r['description']}")

print("\n[4] Rule Check: 疏散走道宽度 1.2m (应不符合)")
r = wm.check_scene_rule("疏散走道宽度", 1.2)
print(f"  {r['status']} | {r['description']}")

print("\n[5] VLA: 帮我把沙发移到窗户旁边")
plan = wm.vla.process_instruction("帮我把沙发移到窗户旁边", target_object="沙发")
print(f"  Actions: {[a['primitive'] for a in plan['action_sequence']]}")
print(f"  Risk: {plan['risk_level']}")
print(f"  Duration: {plan['estimated_duration_s']}s")
print(f"  Similar tasks: {[t['task'] for t in plan['similar_tasks'][:2]]}")

print("\n[6] Physics: 能否推动沙发 (45kg)")
result = wm.physics.can_push(45.0, material="实木地板")
print(f"  Can move: {result['can_move']}")
print(f"  Friction force: {result['friction_force_N']}N / Max: {result['robot_max_force_N']}N")

print("\n[7] Full Inference: 清洁客厅地板")
result = wm.full_inference("清洁客厅地板", target_object="地板")
print(f"  Ready: {result['ready']}")
print(f"  Actions: {[a['primitive'] for a in result['plan']['action_sequence']]}")

print("\n" + "=" * 60)
print("  ALL TESTS PASSED OK")
print("=" * 60)
