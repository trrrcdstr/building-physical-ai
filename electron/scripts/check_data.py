# -*- coding: utf-8 -*-
import json, os

base = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed"

# projects.json
with open(os.path.join(base, "projects.json"), encoding="utf-8") as f:
    d = json.load(f)
print(f"projects.json: {len(d)} projects")
for i, p in enumerate(d):
    print(f"  {i+1}. [{p.get('type','?')}] {p.get('name','?')}")

# desktop_db_index
with open(os.path.join(base, "desktop_db_index.json"), encoding="utf-8") as f:
    db = json.load(f)
print(f"\ndesktop_db_index: {len(db)} entries")
for i, p in enumerate(db):
    print(f"  {i+1}. [{p.get('type','?')}] {p.get('name','?')} | {p.get('location','?')}")
