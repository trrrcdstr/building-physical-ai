import json

with open('data/training/robot_training_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== META ===')
print(json.dumps(data['meta'], indent=2, ensure_ascii=False))

print('\n=== SAMPLES (first 3) ===')
for i, s in enumerate(data['samples'][:3]):
    intent = s.get('intent') or s.get('task')
    cat = s.get('category') or s.get('scene_type')
    print(f'\n[{i+1}] {intent} ({cat})')
    print(f'  action_seq: {s.get("action_sequence", [])}')
    print(f'  risk: {s.get("risk_level")}, force: {s.get("required_force_n", 0)}N')
