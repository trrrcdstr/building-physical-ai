# -*- coding: utf-8 -*-
import json
import re

# 读取 VR_KNOWLEDGE.json 获取 VR 列表
with open('knowledge/VR_KNOWLEDGE.json', encoding='utf-8') as f:
    vr_data = json.load(f)

# 提取 VR 场景（取有房间的 VR）
rooms = vr_data.get('rooms', {})
vr_list = []
for room_type, data in rooms.items():
    for sample in data.get('samples', [])[:3]:
        vr_list.append({
            'id': f"vr{sample['index']}-{room_type}",
            'room_type': room_type,
            'platform': sample.get('platform', 'unknown'),
            'designer': sample.get('designer', ''),
            'original_name': sample.get('original_name', '')
        })

# 读取 sceneConfig.ts
with open('web-app/src/data/sceneConfig.ts', encoding='utf-8') as f:
    config = f.read()

# 添加 VR 场景配置
vr_config = '''  // VR 场景
  vr_scene: {
    id: 'vr_scene',
    label: 'VR全景',
    description: 'VR全景场景查看',
    icon: '🎮',
    color: '#8b5cf6',
    tags: [],
  },
'''

# 插入到 SCENE_CONFIGS
if 'vr_scene' not in config:
    config = config.replace(
        '  // 建筑场景',
        vr_config + '\n  // 建筑场景'
    )

# 更新 CATEGORY_SCENES 添加 vr_scene
if "'vr_scene'" not in config:
    config = config.replace(
        'interior: [',
        'interior: ["vr_scene",'
    )

# 写回
with open('web-app/src/data/sceneConfig.ts', 'w', encoding='utf-8') as f:
    f.write(config)

print('已添加 VR 场景到 sceneConfig.ts')
print('VR 场景数量:', len(vr_list))