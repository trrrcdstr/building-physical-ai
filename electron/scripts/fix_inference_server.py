# -*- coding: utf-8 -*-
"""修复 inference_server.py 的 /api/scene 响应，添加边数据"""
import re

path = 'inference_server.py'

with open(path, encoding='utf-8') as f:
    content = f.read()

# 找到旧的 api/scene 响应模式
# 在 'elif parsed.path == /api/scene:' 之后
old_pattern = r"(elif parsed\.path == '/api/scene':.*?self\.send_json\(\{)[^}]+\}\))"
# 简单替换
old = """elif parsed.path == '/api/scene':
            # 返回场景图谱概要
            self.send_json({
                'num_nodes': scene_data.get('num_nodes', 0),
                'node_types': scene_data.get('node_types', []),
                'node_names': scene_data.get('node_names', []),
                'positions': scene_data.get('node_positions', []),
                'features_dim': scene_data.get('num_features', 0),
            })"""

new = """elif parsed.path == '/api/scene':
            # 返回场景图谱完整数据
            self.send_json({
                'num_nodes': scene_data.get('num_nodes', 0),
                'num_edges': scene_data.get('num_edges', 0),
                'node_types': scene_data.get('node_types', []),
                'node_names': scene_data.get('node_names', []),
                'positions': scene_data.get('node_positions', []),
                'features_dim': len(scene_data.get('useful_dims', [])) or scene_data.get('num_features', 9),
                'edges': scene_data.get('edge_index', []),
                'labels': scene_data.get('labels', []),
                'mean': scene_data.get('mean', []),
                'std': scene_data.get('std', []),
            })"""

if old in content:
    content = content.replace(old, new)
    print('✅ 替换成功')
else:
    print('❌ 未找到目标字符串，检查文件...')
    # 尝试模糊匹配
    idx = content.find("elif parsed.path == '/api/scene':")
    if idx >= 0:
        print(f'找到位置: {idx}')
        print(repr(content[idx:idx+500]))

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# 验证
with open(path, encoding='utf-8') as f:
    c2 = f.read()
if "'num_edges'" in c2:
    print('✅ 验证通过：num_edges 已添加')
else:
    print('❌ 验证失败')
