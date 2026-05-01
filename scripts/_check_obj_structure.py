import json
from pathlib import Path

DATA_DIR = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed")
with open(DATA_DIR / "building_objects.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check structure
if isinstance(data, dict) and 'nodes' in data:
    sample = list(data['nodes'].values())[0] if isinstance(data['nodes'], dict) else data['nodes'][0]
else:
    sample = data[0] if isinstance(data, list) else data

print(f"Sample object keys: {list(sample.keys())}")
print(f"Position type: {type(sample.get('position'))}")
print(f"Position value: {sample.get('position')}")
print(f"Dimensions type: {type(sample.get('dimensions'))}")
print(f"Dimensions value: {sample.get('dimensions')}")
