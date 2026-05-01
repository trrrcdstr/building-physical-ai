# -*- coding: utf-8 -*-
"""测试 WebSocket connect 认证"""
import json, os, websocket, time, hashlib, hmac, base64, random, string
from datetime import datetime

def rand_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

cfg = json.load(open(os.path.join(os.environ["USERPROFILE"],".qclaw","openclaw.json"),encoding="utf-8"))
remote_token = cfg["gateway"]["remote"]["token"]
remote_url   = cfg["gateway"]["remote"]["url"]
local_token  = cfg["gateway"]["auth"]["token"]
local_port   = cfg["gateway"]["port"]

def test_gateway(name, url, token):
    print(f"\n{'='*50}")
    print(f"测试: {name}  {url}")
    print(f"Token: {token[:8]}...")
    try:
        ws = websocket.create_connection(url, timeout=8)
        print("  连接: OK")

        # 接收 challenge
        evt = json.loads(ws.recv())
        print(f"  STEP1 challenge: {evt}")
        nonce = evt.get("payload",{}).get("nonce","")
        ts = str(int(time.time()*1000))

        if not nonce:
            ws.close()
            return

        # 签名 nonce
        sig = base64.b64encode(hmac.new(
            token.encode(), nonce.encode(), hashlib.sha256
        ).digest()).decode()

        # STEP2: 发送 connect（最小参数）
        connect_frame = {
            "type": "req",
            "id": rand_id(),
            "method": "connect",
            "params": {
                "minProtocol": 3,
                "maxProtocol": 3,
                "client": {
                    "id": "gateway-client",
                    "displayName": "Physics Agent (Python)",
                    "version": "1.0.0",
                    "platform": "win32",
                    "mode": "backend"
                },
                "auth": {"token": token},
                "role": "operator",
                "scopes": ["operator.admin"],
                "caps": []
            }
        }
        ws.send(json.dumps(connect_frame))
        ws.settimeout(10)
        resp = json.loads(ws.recv())
        print(f"  STEP2 connect resp: {resp}")
        ok = resp.get("ok", False)

        if ok:
            # STEP3: 发送 sessions.send
            send_frame = {
                "type": "req",
                "id": rand_id(),
                "method": "sessions.send",
                "params": {
                    "sessionKey": "agent:main:main",
                    "message": f"[Physics Agent] Python WebSocket 连通成功 @ {datetime.now().strftime('%H:%M:%S')}"
                }
            }
            ws.send(json.dumps(send_frame))
            ws.settimeout(5)
            try:
                resp2 = json.loads(ws.recv())
                print(f"  STEP3 sessions.send resp: {resp2}")
            except Exception as e:
                print(f"  STEP3: {e}")

        ws.close()
        print("  完成")

    except Exception as e:
        print(f"  失败: {e}")

# 测试远程 Gateway
test_gateway("远程", remote_url, remote_token)
# 测试本地 Gateway
test_gateway("本地", f"ws://127.0.0.1:{local_port}", local_token)
