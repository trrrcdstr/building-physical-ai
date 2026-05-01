"""Test integration between Agent API (5002) and Neural Spatial Engine (5000)"""
import urllib.request
import json
import time

proj = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai"

# ── Step 1: Load spatial room data ──────────────────────────────────────
with open(f"{proj}\\data\\processed\\spatial_rooms.json", encoding="utf-8") as f:
    spatial_rooms = json.load(f)
rooms = {r["id"]: r for r in spatial_rooms.get("rooms", [])}
print(f"Loaded {len(rooms)} rooms from spatial_rooms.json")
for rid, r in list(rooms.items())[:3]:
    print(f"  {rid}: bounds={r['bounds']}")

# ── Step 2: Test Agent API drill (current = hardcoded) ───────────────────
print("\n=== Agent API Current Drill Response ===")
req = urllib.request.Request(
    "http://localhost:5002/api/agent/process",
    data=json.dumps({"command": "在东墙钻一个孔"}).encode(),
    headers={"Content-Type": "application/json"}
)
try:
    r = urllib.request.urlopen(req, timeout=5)
    result = json.loads(r.read())
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"ERROR: {e}")

# ── Step 3: Test Neural Server physics query ──────────────────────────────
print("\n=== Neural Server physics_query ===")
# Try with wall_brick (non-load-bearing wall material)
physics_req = urllib.request.Request(
    "http://localhost:5000/api/physics/query",
    data=json.dumps({
        "position": [10, 1.05, -3],
        "object_type": "wall_brick",
        "scene": "室内_家庭"
    }).encode(),
    headers={"Content-Type": "application/json"}
)
try:
    r = urllib.request.urlopen(physics_req, timeout=5)
    print(json.dumps(json.loads(r.read()), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"physics_query error: {e}")

# Try with wall_load_bearing (north wall = forbidden)
print("\n=== Neural Server - load-bearing wall ===")
physics_req2 = urllib.request.Request(
    "http://localhost:5000/api/physics/query",
    data=json.dumps({
        "position": [0, 1.05, -1.5],
        "object_type": "wall_load_bearing",
        "scene": "室内_家庭"
    }).encode(),
    headers={"Content-Type": "application/json"}
)
try:
    r = urllib.request.urlopen(physics_req2, timeout=5)
    print(json.dumps(json.loads(r.read()), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"physics_query load-bearing error: {e}")

# ── Step 4: Test scene API ────────────────────────────────────────────────
print("\n=== Neural Server scene API ===")
scene_req = urllib.request.Request("http://localhost:5000/api/scene")
try:
    r = urllib.request.urlopen(scene_req, timeout=5)
    scene = json.loads(r.read())
    print(f"nodes={scene['num_nodes']}, edges={scene['num_edges']}")
    # Show first few nodes with positions
    positions = scene.get("positions", [])
    labels = scene.get("labels", [])
    if positions:
        print(f"First 3 nodes: pos={positions[0]}, label={labels[0] if labels else '?'}")
        print(f"Next 3 nodes: pos={positions[1]}, label={labels[1] if labels else '?'}")
except Exception as e:
    print(f"scene API error: {e}")

print("\n=== Integration Analysis ===")
print("Gap: Agent API (5002) doesn't call Neural Server (5000)")
print("Action: Modify agent_api_simple.py to call 5000 physics query")
print("Result: Drill response will include real spatial position + physics data")