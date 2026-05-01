import json, os

proj = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai"

# Check spatial_rooms
with open(f"{proj}\\data\\processed\\spatial_rooms.json", encoding="utf-8") as f:
    sr = json.load(f)
print("=== All 7 rooms ===")
for r in sr.get("rooms", []):
    name = r.get("name", "?")
    print(f"  id={r['id']} name={name} bounds={r['bounds']} doors={r['door_count']} windows={r['window_count']}")

print()
print("=== Edges (first 5) ===")
for e in sr.get("edges", [])[:5]:
    print(f"  {json.dumps(e, ensure_ascii=False)}")

print()
print("=== Room stats keys ===")
print(list(sr.get("room_stats", {}).keys()))

print()
# Check OBJECT_PHYSICS_MAP
from pathlib import Path
sys_path = Path(f"{proj}\\src\\neural_inference_server.py")
with open(sys_path, encoding="utf-8") as f:
    content = f.read()

# Find OBJECT_PHYSICS_MAP section
start = content.find("OBJECT_PHYSICS_MAP")
if start >= 0:
    # Extract just the object types (keys) from the map
    import re
    keys = re.findall(r'"([^"]+)":\s*\{', content[start:start+3000])
    print("=== Object types in OBJECT_PHYSICS_MAP ===")
    for k in keys:
        print(f"  {k}")

# Check what physics data is in building_objects_enhanced
print()
print("=== building_objects_enhanced ===")
with open(f"{proj}\\data\\processed\\building_objects_enhanced.json", encoding="utf-8") as f:
    boe = json.load(f)
print("Count:", len(boe) if isinstance(boe, list) else "dict")
if isinstance(boe, list):
    print("First item keys:", list(boe[0].keys()) if boe else [])
    for item in boe[:3]:
        mass = item.get("physics", {}).get("mass_kg", "?")
        fric = item.get("physics", {}).get("friction", "?")
        mat = item.get("physics", {}).get("material", "?")
        print(f"  {item.get('name','?')} mass={mass} fric={fric} mat={mat}")