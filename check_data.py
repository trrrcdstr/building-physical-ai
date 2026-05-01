"""快速数据统计脚本"""
from pathlib import Path
import json

base = Path('../建筑数据库')
print('=== 建筑数据库 ===')
if base.exists():
    grand_total = 0
    grand_files = 0
    for item in sorted(base.iterdir()):
        if item.is_file():
            s = item.stat().st_size / 1024 / 1024
            print(f'  [文件] {item.name}: {s:.1f} MB')
            grand_total += s
            grand_files += 1
        elif item.is_dir():
            files = [f for f in item.rglob('*') if f.is_file()]
            s = sum(f.stat().st_size for f in files) / 1024 / 1024
            print(f'  [目录] {item.name}/: {len(files)}个, {s:.1f} MB')
            grand_total += s
            grand_files += len(files)
    print(f'  建筑数据库总计: {grand_files}个文件, {grand_total:.1f} MB')

print()
print('=== VR数据 ===')
vr = Path('data/processed/vr_links_structured.json')
if vr.exists():
    with open(vr) as f:
        data = json.load(f)
    print(f'  VR总数: {len(data)}条')
    for item in data[:3]:
        name = item.get('name', item.get('source', '?'))
        link = item.get('link', '无链接')
        print(f'  - {name}: {link[:70]}')

print()
print('=== 场景图谱 ===')
sg = Path('data/processed/cleaned/scene_graph_real.json')
if sg.exists():
    with open(sg) as f:
        data = json.load(f)
    nodes = data.get('num_nodes', len(data.get('node_features', [])))
    print(f'  节点数: {nodes}')
    print(f'  特征维度: {len(data.get("node_features", [[]])[0]) if data.get("node_features") else 0}')
    node_types = data.get('node_types', [])
    types = {}
    for t in node_types:
        types[t] = types.get(t, 0) + 1
    for t, c in sorted(types.items()):
        print(f'  - {t}: {c}')

print()
print('=== 神经网络模型 ===')
ckpt = Path('data/processed/checkpoints')
for f in sorted(ckpt.glob('*.pt')):
    print(f'  {f.name}: {f.stat().st_size/1024:.0f} KB')

print()
print('=== 原始VR渲染数据 ===')
raw_base = Path('data/raw')
for item in sorted(raw_base.iterdir()):
    files = [f for f in item.rglob('*') if f.is_file()]
    s = sum(f.stat().st_size for f in files) / 1024 / 1024
    print(f'  {item.name}: {len(files)}个文件, {s:.1f} MB')
