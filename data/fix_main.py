"""Fix encoding issue in rl_training_data.py"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\rl_training_data.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the main block
old_block = '''if __name__ == "__main__":
    print("="*60)
    print("强化学习训练数据集")
    print("="*60)
    print()
    print("项目统计:")
    for p in DATASET_STATS["projects"]:
        print(f"  - {p['id']}: {p['type']}")
    print()
    print("RL场景:")
    for category, scenarios in RL_SCENARIOS.items():
        print(f"  {category}: {len(scenarios)}个场景")
    print()
    print("物理属性:")
    print(f"  地面材质: {DATASET_STATS['physics_params']['flooring_types']}种")
    print(f"  家具类型: {DATASET_STATS['physics_params']['furniture_types']}种")
    print(f"  可抓取物体: {DATASET_STATS['physics_params']['graspable_objects']}种")
    print()
    print("动作空间大小:", DATASET_STATS["action_space_size"])
    print()
    print("✅ 训练数据集就绪")'''

new_block = '''if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("="*60)
    print("RL Training Dataset - Building World Model")
    print("="*60)
    print()
    print("Projects:")
    for p in DATASET_STATS["projects"]:
        print("  - {}: {}".format(p["id"], p["type"]))
    print()
    print("RL Scenarios:")
    for cat, scenes in RL_SCENARIOS.items():
        print("  {}: {} scenarios".format(cat, len(scenes)))
    print()
    print("Physics Properties:")
    print("  Flooring: {} types".format(DATASET_STATS["physics_params"]["flooring_types"]))
    print("  Furniture: {} types".format(DATASET_STATS["physics_params"]["furniture_types"]))
    print("  Graspable: {} types".format(DATASET_STATS["physics_params"]["graspable_objects"]))
    print()
    print("Action Space Size:", DATASET_STATS["action_space_size"])
    print()
    print("[OK] Dataset ready for robot RL training")'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed!')
else:
    print('Old block not found')
