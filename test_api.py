"""Test inference API"""
import urllib.request, json

url = 'http://localhost:5000/api/relation'
tests = [(0, 3), (10, 50), (20, 80), (50, 100), (0, 150)]

for i, j in tests:
    data = json.dumps({'node_i': i, 'node_j': j}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    r = urllib.request.urlopen(req)
    result = json.loads(r.read())
    dist = result['distance_m']
    rel = result['relation']
    prob = result['predicted_prob']
    print(f'Node {i} vs {j}: dist={dist}m, pred={rel}, p={prob:.3f}')

print()
req = urllib.request.urlopen('http://localhost:5000/api/scene')
scene = json.loads(req.read())
print(f'Scene: {scene["num_nodes"]} nodes')
print(f'Types: door={scene["node_types"].count("door")}, window={scene["node_types"].count("window")}')
xs = [p[0] for p in scene['positions']]
print(f'X range: [{min(xs):.0f}, {max(xs):.0f}]')
