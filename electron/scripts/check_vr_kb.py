import json
p = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\VR_KNOWLEDGE.json"
with open(p, "r", encoding="utf-8") as f:
    d = json.load(f)
print("Type:", type(d).__name__)
if isinstance(d, list):
    print("List length:", len(d))
elif isinstance(d, dict):
    for k, v in d.items():
        vl = len(v) if hasattr(v, "__len__") else ""
        print("  {}: {} {}".format(k, type(v).__name__, vl))
