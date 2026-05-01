import json, os
from pathlib import Path

with open('knowledge/RENDERING_DATABASE.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f"Total: {len(db['records'])} records")

# Test first 5 paths
ok, fail = 0, 0
for r in db['records'][:10]:
    # Fix path: file://C:/... -> C:\...
    raw = r['path']
    if raw.startswith('file://'):
        path_str = raw[7:]  # remove file://
        path_str = path_str.replace('/', '\\')  # unix sep -> windows
    else:
        path_str = raw

    exists = os.path.exists(path_str)
    status = "OK" if exists else "MISSING"
    if exists:
        ok += 1
    else:
        fail += 1

    # Print full path for debugging
    print(f"  [{status}] {path_str[:100]}")

print(f"\nResult: {ok} OK, {fail} MISSING")

# If all missing, check if the base directory exists
base = r"C:\Users\Administrator\Desktop\设计数据库"
print(f"\nBase dir exists: {os.path.exists(base)}")
subdirs = os.listdir(base) if os.path.exists(base) else []
for s in subdirs:
    sp = os.path.join(base, s)
    if os.path.isdir(sp):
        count = len(os.listdir(sp))
        print(f"  {s}: {count} items")
