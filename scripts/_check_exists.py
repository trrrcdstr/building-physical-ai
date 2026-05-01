import json, os
from pathlib import Path

with open('knowledge/RENDERING_DATABASE.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Test actual file existence with proper encoding
ok, fail = 0, 0
missing_examples = []

for r in db['records']:
    path_str = r['path'][7:]  # remove file://
    path_str = path_str.replace('/', '\\')
    if os.path.exists(path_str):
        ok += 1
    else:
        fail += 1
        if len(missing_examples) < 3:
            missing_examples.append(path_str)

print(f"Total: {len(db['records'])}")
print(f"Exists: {ok}, Missing: {fail}")
if missing_examples:
    print("\nMissing examples (first 3):")
    for p in missing_examples:
        print(f"  {p}")
    # Try to find the real path
    print("\nSearching for real paths...")
    base = r"C:\Users\Administrator\Desktop"
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith('.jpg') and not any(c in f for c in '家庭_工装_酒店_餐饮_地产_'):
                pass  # just list
    print(f"Files in Desktop: {len(os.listdir(r'C:\Users\Administrator\Desktop'))}")
    for item in os.listdir(r'C:\Users\Administrator\Desktop'):
        print(f"  {item}")
