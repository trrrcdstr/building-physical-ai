# -*- coding: utf-8 -*-
"""测试远程 Gateway WebSocket 连接"""
import json, os, time, websocket

path = os.path.join(os.environ["USERPROFILE"], ".qclaw", "openclaw.json")
with open(path, encoding="utf-8") as f:
    cfg = json.load(f)

remote_ws = cfg["gateway"]["remote"]["url"]  # ws://192.168.3.11:28789
remote_token = cfg["gateway"]["remote"]["token"]
local_ws = f"ws://127.0.0.1:{cfg['gateway']['port']}"
local_token = cfg["gateway"]["auth"]["token"]

targets = [
    ("远程 Gateway", remote_ws, remote_token),
    ("本地 Gateway", local_ws, local_token),
]

for name, url, token in targets:
    print(f"\n--- 测试 {name}: {url} ---")
    try:
        ws = websocket.create_connection(
            url,
            header=[f"Authorization: Bearer {token}"],
            timeout=5,
        )
        print(f"  连接: OK")

        # 尝试 ping
        ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}))
        ws.settimeout(3)
        try:
            resp = json.loads(ws.recv())
            print(f"  ping 响应: {json.dumps(resp, ensure_ascii=False)[:200]}")
        except Exception as e:
            print(f"  ping 响应: {e}")

        # 尝试 sessions.send
        ws.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "sessions.send",
            "params": {"sessionKey": "agent:main:main", "message": "[Physics Agent] WebSocket 连通测试"}
        }))
        ws.settimeout(3)
        try:
            resp2 = json.loads(ws.recv())
            print(f"  sessions.send 响应: {json.dumps(resp2, ensure_ascii=False)[:200]}")
        except Exception as e:
            print(f"  sessions.send 响应: {e}")

        ws.close()
    except Exception as e:
        print(f"  失败: {e}")
