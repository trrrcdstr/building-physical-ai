import json
import os

# New project data
new_project = {
    "name": "产业园",
    "type": "commercial",
    "path": r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\raw\产业园",
    "cad_files": [],
    "render_images": [],
    "structure_files": [],
    "electrical_files": [],
    "landscape_files": [],
    "plumbing_files": [],
    "hvac_files": [],
    "parsed_data": [],
    "object_count": 0,
    "notes": "产业园项目 - 含食堂PALACE室内设计、平面规划图CAD文件"
}

# Load existing projects
projects_path = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed\projects.json'
with open(projects_path, 'r', encoding='utf-8') as f:
    projects = json.load(f)

# Check if already exists
existing_names = [p['name'] for p in projects]
if '产业园' in existing_names:
    print("项目已存在，跳过添加")
else:
    projects.append(new_project)
    print(f"添加新项目: {new_project['name']}")
    print(f"总项目数: {len(projects)}")

# Save
with open(projects_path, 'w', encoding='utf-8') as f:
    json.dump(projects, f, ensure_ascii=False, indent=2)

print("Done!")
