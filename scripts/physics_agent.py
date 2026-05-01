# -*- coding: utf-8 -*-
"""
Physics Agent - 500ms 物理仿真 + WebSocket sessions_send + 发到主控会话
WebSocket RPC 到 OpenClaw Gateway
"""
import sys, time, json, os, traceback
import websocket
from datetime import datetime

# ===== 配置 =====
G = 9.81
DT = 0.001      # 仿真步长 s
POLL_MS = 500   # 发送间隔 ms
INIT_H = 10.0  # 初始高度 m

# ===== 读取配置 =====
def get_config():
    path = os.path.join(os.environ["USERPROFILE"], ".qclaw", "openclaw.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

cfg = get_config()
LOCAL_PORT = cfg["gateway"]["port"]                      # 28789
LOCAL_TOKEN = cfg["gateway"]["auth"]["token"]             # 本地 auth token
REMOTE_URL = cfg["gateway"]["remote"]["url"]              # ws://192.168.3.11:28789
REMOTE_TOKEN = cfg["gateway"]["remote"]["token"]          # 远程 token

TARGET_SESSION = "agent:main:main"
LOCAL_WS = f"ws://127.0.0.1:{LOCAL_PORT}"
REMOTE_WS = REMOTE_URL

# ===== 物理仿真 =====
class FallingBody:
    def __init__(self, h=INIT_H):
        self.h = h; self.v = 0.0; self.t = 0.0; self.grounded = False

    def step(self, dt=DT):
        if self.grounded:
            return
        self.v += G * dt
        self.h -= self.v * dt
        self.t += dt
        if self.h <= 0:
            self.h = 0.0; self.v = 0.0; self.grounded = True

    def reset(self, h=INIT_H):
        self.__init__(h)

    def state(self):
        return {"t_s": round(self.t, 4), "y_m": round(self.h, 4),
                "v_ms": round(self.v, 4), "grounded": self.grounded}

# ===== WebSocket RPC 客户端 =====
class OpenClawWS:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.ws = None
        self._id = 0
        self._connected = False
        self._resp_queue = {}
        self._reader_thread = None
        self._running = False

    def connect(self):
        try:
            self.ws = websocket.create_connection(
                self.url,
                header=[f"Authorization: Bearer {self.token}"],
                timeout=5
            )
            self._connected = True
            self._running = True
            print(f"[WS] Connected: {self.url}", flush=True)
            return True
        except Exception as e:
            print(f"[WS] 连接失败 {self.url}: {e}", flush=True)
            return False

    def _send_raw(self, obj):
        if self.ws:
            self.ws.send(json.dumps(obj))

    def _next_id(self):
        self._id += 1
        return self._id

    def rpc(self, method, params=None):
        """发送 JSON-RPC 请求"""
        if not self._connected:
            return None
        mid = self._next_id()
        msg = {"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}}
        try:
            self._send_raw(msg)
            # 短暂等待响应
            self.ws.settimeout(2.0)
            resp = self.ws.recv()
            return json.loads(resp)
        except Exception as e:
            print(f"[WS] RPC {method} 失败: {e}", flush=True)
            return None

    def sessions_send(self, session_key, message):
        """发送消息到指定会话"""
        return self.rpc("sessions.send", {
            "sessionKey": session_key,
            "message": message
        })

    def close(self):
        self._running = False
        if self.ws:
            self.ws.close()

# ===== 尝试连接（本地优先，失败则远程）=====
def connect_gateway():
    print("[PhysicsAgent] 尝试连接本地 Gateway...", flush=True)
    ws = OpenClawWS(LOCAL_WS, LOCAL_TOKEN)
    if ws.connect():
        return ws

    print("[PhysicsAgent] 本地失败，尝试远程...", flush=True)
    ws2 = OpenClawWS(REMOTE_WS, REMOTE_TOKEN)
    if ws2.connect():
        return ws2

    return None

# ===== 主循环 =====
def main():
    print(f"[PhysicsAgent] 启动: g={G}m/s2 dt={DT}s 每{POLL_MS}ms | 目标={TARGET_SESSION}", flush=True)

    ws = connect_gateway()
    if not ws:
        print("[PhysicsAgent] 无法连接 Gateway，退出。", flush=True)
        sys.exit(1)

    body = FallingBody(INIT_H)
    cycle = 0
    last_send = time.time()
    start = time.time()

    try:
        while True:
            cycle += 1
            body.step(DT)
            now = time.time()

            if now - last_send >= POLL_MS / 1000.0:
                last_send = now
                s = body.state()
                elapsed = round(time.time() - start, 1)
                flag = "[落地]" if s["grounded"] else "[下落]"
                msg = (
                    f"[Physics #{cycle}] {flag} "
                    f"y={s['y_m']:.4f}m  v={s['v_ms']:.4f}m/s  t={s['t_s']}s"
                    f"  | 累计{elapsed}s"
                )
                ok = ws.sessions_send(TARGET_SESSION, msg)
                ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                status = "OK" if ok else "FAIL"
                print(f"[{ts}] #{cycle:5d}  y={s['y_m']:8.4f}m  v={s['v_ms']:7.4f}m/s  "
                      f"{flag:6s}  send={status}", flush=True)

                if s["grounded"]:
                    time.sleep(2)
                    body.reset(INIT_H)
                    print("[PhysicsAgent] === 重置 10m ===", flush=True)

    except KeyboardInterrupt:
        print("\n[PhysicsAgent] 已停止.", flush=True)
    except Exception as e:
        traceback.print_exc()
    finally:
        ws.close()

if __name__ == "__main__":
    main()
