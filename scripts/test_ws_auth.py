# -*- coding: utf-8 -*-
import json, os, websocket, time, hashlib, hmac, base64

cfg = json.load(open(os.path.join(os.environ["USERPROFILE"],".qclaw","openclaw.json"),encoding="utf-8"))
token = cfg["gateway"]["remote"]["token"]
url   = cfg["gateway"]["remote"]["url"]
print(f"URL: {url}")
print(f"Token: {token[:8]}...")

ws = websocket.create_connection(url, timeout=5, enable_multithread=True)
print("连接: OK")

# Step 1: 接收 challenge
evt = json.loads(ws.recv())
print(f"STEP1 challenge: {evt}")

nonce = evt.get("payload",{}).get("nonce","")
if not nonce:
    print("无 nonce，关闭")
    ws.close()
else:
    # HMAC-SHA256 签名
    sig = base64.b64encode(hmac.new(
        token.encode(), nonce.encode(), hashlib.sha256
    ).digest()).decode()
    ts = str(int(time.time()*1000))

    # Step 2: 发送 auth
    auth_frame = {"type":"req","id":"1","method":"auth.token","params":{
        "token": token, "nonce": nonce, "signature": sig, "signedAt": ts
    }}
    ws.send(json.dumps(auth_frame))
    ws.settimeout(8)
    try:
        resp = json.loads(ws.recv())
        print(f"STEP2 auth resp: {resp}")
    except Exception as e:
        print(f"STEP2 响应: {e}")

    # Step 3: 尝试 sessions.send
    send_frame = {"type":"req","id":"2","method":"sessions.send","params":{
        "sessionKey": "agent:main:main",
        "message": "[Physics Agent] WebSocket 连通测试 from local Python"
    }}
    ws.send(json.dumps(send_frame))
    ws.settimeout(8)
    try:
        resp2 = json.loads(ws.recv())
        print(f"STEP3 send resp: {resp2}")
    except Exception as e:
        print(f"STEP3: {e}")

    ws.close()
    print("完成")
