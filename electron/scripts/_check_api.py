import urllib.request, json

endpoints = ['/api/scene', '/api/relation', '/api/physics', '/api/vla', '/api/v1/vla/infer']
for ep in endpoints:
    try:
        r = urllib.request.urlopen('http://localhost:5001' + ep, timeout=3).read()
        data = json.loads(r)
        if 'status' in data:
            print(f'{ep}: status={data["status"]}')
        elif 'nodes' in data:
            print(f'{ep}: nodes={data["nodes"]}')
        elif 'scene' in data:
            print(f'{ep}: scene={data["scene"][:50] if isinstance(data["scene"], str) else data["scene"]}')
        else:
            keys = list(data.keys())
            print(f'{ep}: keys={keys[:5]}')
    except Exception as e:
        print(f'{ep}: FAIL - {str(e)[:80]}')