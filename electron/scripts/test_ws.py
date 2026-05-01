# -*- coding: utf-8 -*-
import json, os, websocket, time
path = os.path.join(os.environ["USERPROFILE"], ".qclaw", "openclaw.json")
with open(path, encoding="utf-8") as f:
    cfg = json.load(f)
token = cfg["gateway"]["auth"]["token"]
url = f"ws://127.0.0.1:{cfg['gateway']['port']}"
print(f"URL: {url}")
print(f"Token: {token[:8]}...")
try:
    ws = websocket.create_connection(url, header=[f"Authorization: Bearer {token}"], timeout=5)
    print("Connected OK")
    ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {}}))
    ws.settimeout(3)
    resp = ws.recv()
    print(f"Response: {resp}")
    ws.close()
except Exception as e:
    print(f"Error: {e}")
