import json

with open('knowledge/VR_KNOWLEDGE.json', 'r', encoding='utf-8') as f:
    vr_data = json.load(f)

print(f'Type: {type(vr_data)}')
if isinstance(vr_data, dict):
    print(f'Keys: {list(vr_data.keys())[:10]}')
    for k in list(vr_data.keys())[:3]:
        print(f'\n--- {k} ---')
        print(f'Type: {type(vr_data[k])}')
        if isinstance(vr_data[k], list):
            print(f'Length: {len(vr_data[k])}')
            if vr_data[k]:
                print(f'First item type: {type(vr_data[k][0])}')
                print(json.dumps(vr_data[k][0], ensure_ascii=False, indent=2)[:500])
        elif isinstance(vr_data[k], dict):
            print(f'Keys: {list(vr_data[k].keys())[:5]}')
            print(json.dumps(vr_data[k], ensure_ascii=False, indent=2)[:500])
        else:
            print(repr(vr_data[k])[:200])
elif isinstance(vr_data, list):
    print(f'Length: {len(vr_data)}')
    print(f'First item: {type(vr_data[0])}')
    print(json.dumps(vr_data[0], ensure_ascii=False, indent=2)[:500])
