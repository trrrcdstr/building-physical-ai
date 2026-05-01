import json

with open(r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\projects.json', 'r', encoding='utf-8') as f:
    projects = json.load(f)

print(f'Total projects: {len(projects)}')
for p in projects:
    print(f'  - {p["name"]} ({p["type"]})')
