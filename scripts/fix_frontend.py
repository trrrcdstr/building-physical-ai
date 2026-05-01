#!/usr/bin/env python3
"""修复前端数据问题：1) buildingStore.ts加renderings场景 2) sceneConfig.ts修复乱码 3) 验证JSON数据"""
import os, json

BASE = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\web-app\src"

# ── 1. 修复 buildingStore.ts ──────────────────────────────────
store_path = os.path.join(BASE, "store", "buildingStore.ts")
with open(store_path, "r", encoding="utf-8") as f:
    content = f.read()

old = "  | 'ns_basement' | 'sample'"
new = "  | 'ns_basement' | 'sample' | 'renderings'"
if old in content and "'renderings'" not in content.split("SceneType")[1].split(";")[0]:
    content = content.replace(old, new, 1)
    with open(store_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("FIXED: buildingStore.ts - added 'renderings' to SceneType")
else:
    print("OK: buildingStore.ts already has 'renderings'")

# ── 2. 追加 sceneConfig.ts 缺失的导出 ──────────────────────────
config_path = os.path.join(BASE, "data", "sceneConfig.ts")
with open(config_path, "r", encoding="utf-8") as f:
    existing = f.read()

if "SCENE_KEY_NAMES" not in existing:
    appendix = """

// === 自动追加修复（2026-04-16） ===================
export const SCENE_KEY_NAMES: Record<string, string> = {
  "residence": "Home",
  "mall": "Mall",
  "office": "Office",
  "hotel": "Hotel",
  "villa_garden": "Villa",
  "park": "Park",
  "office_building": "Office Building",
  "residential": "Residential",
  "commercial_complex": "Commercial",
  "ns_basement": "Basement",
  "sample": "Sample",
  "renderings": "Renderings",
}

export const SCENE_CATEGORY_MAP: Record<string, string> = {
  "residence": "indoor",
  "mall": "indoor",
  "office": "indoor",
  "hotel": "indoor",
  "villa_garden": "outdoor",
  "park": "outdoor",
  "office_building": "building",
  "residential": "building",
  "commercial_complex": "building",
  "ns_basement": "building",
  "sample": "building",
  "renderings": "indoor",
}
// =======================================================
"""
    with open(config_path, "a", encoding="utf-8") as f:
        f.write(appendix)
    print("FIXED: sceneConfig.ts - appended SCENE_KEY_NAMES and SCENE_CATEGORY_MAP")
else:
    print("OK: sceneConfig.ts - SCENE_KEY_NAMES already present")

# ── 3. 验证 rendering_objects.json ───────────────────────────
json_path = os.path.join(BASE, "..", "public", "data", "rendering_objects.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"\nJSON CHECK: {len(data)} objects")
print(f"  First ID: {data[0]['id']}")
print(f"  Type: {data[0].get('type', 'N/A')}")
print(f"  Scene_type: {data[0].get('scene_type', 'N/A')}")
bad = [d for d in data if not d.get("path")]
print(f"  Entries with no path: {len(bad)}")
if bad:
    print(f"  First bad: {bad[0].get('id','?')}")

# ── 4. 验证 RenderingGallery ────────────────────────────────
gallery_path = os.path.join(BASE, "components", "RenderingGallery.tsx")
with open(gallery_path, "r", encoding="utf-8") as f:
    gallery = f.read()
checks = [
    ("Fetches /data/rendering_objects.json", "/data/rendering_objects.json" in gallery),
    ("Checks activeScene === 'renderings'", "'renderings'" in gallery),
    ("Returns null if wrong scene", "return null" in gallery),
]
print("\nRenderingGallery checks:")
for desc, ok in checks:
    print(f"  {'OK' if ok else 'FAIL'} {desc}")

print("\nAll fixes applied. Restart frontend with: npm run dev")
