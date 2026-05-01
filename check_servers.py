"""Check both servers"""
import urllib.request, json

# Check Vite
try:
    r = urllib.request.urlopen('http://localhost:3000', timeout=3)
    print(f'Vite (port 3000): {r.status} - content-type: {r.headers.get("content-type","?")}')
    html = r.read(500).decode('utf-8', errors='ignore')
    print(f'  Title: {html[html.find("<title>")+7:html.find("</title>")] if "<title>" in html else "no title"}')
    print(f'  Script tags: {html.count("<script")}')
except Exception as e:
    print(f'Vite (port 3000): ERROR - {e}')

# Check Inference
try:
    r = urllib.request.urlopen('http://localhost:5000/api/health', timeout=3)
    data = json.loads(r.read())
    print(f'Inference (port 5000): OK')
    print(f'  Models: {list(data.get("models",{}).keys())}')
    print(f'  Nodes: {data.get("scene_nodes","?")}')
except Exception as e:
    print(f'Inference (port 5000): ERROR - {e}')

# Check scene
try:
    r = urllib.request.urlopen('http://localhost:5000/api/scene', timeout=3)
    data = json.loads(r.read())
    print(f'Scene nodes: {data.get("num_nodes","?")}')
    print(f'  Types: {set(data.get("node_types",[]))}')
except Exception as e:
    print(f'Scene API: ERROR - {e}')
