# -*- coding: utf-8 -*-
"""Physics Agent v2 - WebSocket 直连 Gateway 发送物理仿真数据"""
import json, os, websocket, time, hashlib, hmac, base64, random, string, traceback, threading
from datetime import datetime

# ===== 配置 =====
G = 9.81
DT = 0.001
POLL_MS = 500
INIT_H = 10.0

def rand_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def load_config():
    p = os.path.join(os.environ["USERPROFILE"],".qclaw","openclaw.json")
    with open(p,encoding="utf-8") as f:
        return json.load(f)

cfg = load_config()

TARGET_SESSION = "agent:main:main"

# ===== 物理引擎 =====
class FallingBody:
    def __init__(self, h=INIT_H):
        self.h = float(h); self.v = 0.0; self.t = 0.0; self.grounded = False
    def step(self, dt=DT):
        if self.grounded: return
        self.v += G * dt; self.h -= self.v * dt; self.t += dt
        if self.h <= 0:
            self.h = 0.0; self.v = 0.0; self.grounded = True
    def reset(self, h=INIT_H):
        self.__init__(h)
    def state(self):
        return {"height_m": round(self.h,6), "velocity_ms": round(self.v,6),
                "time_s": round(self.t,6), "grounded": self.grounded}

# ===== Gateway WebSocket 客户端 =====
class GatewayClient:
    def __init__(self, url, token):
        self.url = url; self.token = token; self.ws = None; self.connected = False

    def connect(self):
        try:
            self.ws = websocket.create_connection(self.url, timeout=8)
            evt = json.loads(self.ws.recv())
            nonce = evt.get("payload",{}).get("nonce","")
            if not nonce:
                print(f"[GW] 无 nonce"); return False

            self.ws.send(json.dumps({
                "type":"req","id":rand_id(),"method":"connect","params":{
                    "minProtocol":3,"maxProtocol":3,
                    "client":{"id":"gateway-client","displayName":"Physics Agent","version":"1.0.0",
                              "platform":"win32","mode":"backend"},
                    "auth":{"token":self.token},
                    "role":"operator","scopes":["operator.admin"],"caps":[]
                }
            }))
            self.ws.settimeout(10)
            resp = json.loads(self.ws.recv())
            self.connected = resp.get("ok", False)
            if self.connected:
                print(f"[GW] 连接成功: {self.url}")
                # 启动接收线程（吃掉 health/tick 等事件）
                threading.Thread(target=self._recv_loop, daemon=True).start()
            else:
                print(f"[GW] 连接失败: {resp.get('error',{})}")
            return self.connected
        except Exception as e:
            print(f"[GW] 连接异常: {e}"); return False

    def _recv_loop(self):
        """后台接收 Gateway 推送（health/tick 等），防止阻塞"""
        while self.connected:
            try:
                self.ws.settimeout(5)
                data = self.ws.recv()
                # 静默消费
            except websocket.WebSocketTimeoutException:
                continue
            except:
                self.connected = False
                break

    def send_to_session(self, session_key, message):
        if not self.connected: return False
        try:
            self.ws.send(json.dumps({
                "type":"req","id":rand_id(),"method":"send","params":{
                    "sessionKey": session_key, "message": message
                }
            }))
            return True
        except Exception as e:
            print(f"[GW] send 失败: {e}"); self.connected = False; return False

    def close(self):
        self.connected = False
        if self.ws:
            try: self.ws.close()
            except: pass

# ===== 连接（本地优先，远程次之）=====
def make_client():
    local = f"ws://127.0.0.1:{cfg['gateway']['port']}"
    c = GatewayClient(local, cfg["gateway"]["auth"]["token"])
    if c.connect(): return c

    c2 = GatewayClient(cfg["gateway"]["remote"]["url"], cfg["gateway"]["remote"]["token"])
    if c2.connect(): return c2

    return None

# ===== 主循环 =====
def main():
    print(f"[PhysicsAgent v2] 启动 | g={G} dt={DT} 每{POLL_MS}ms")
    gw = make_client()
    if not gw:
        print("[PhysicsAgent] Gateway 连接全部失败，退出")
        return

    body = FallingBody(INIT_H)
    cycle = 0
    last_send = time.time()
    start = time.time()
    msg_count = 0

    try:
        while True:
            cycle += 1
            body.step(DT)
            now = time.time()

            if now - last_send >= POLL_MS / 1000.0:
                last_send = now
                s = body.state()
                elapsed = round(now - start, 1)
                flag = "落地" if s["grounded"] else "下落"
                ts = datetime.now().strftime("%H:%M:%S")

                msg = (
                    f"[Physics #{cycle}] {flag} "
                    f"y={s['height_m']:.4f}m  v={s['velocity_ms']:.4f}m/s  t={s['time_s']}s"
                )
                ok = gw.send_to_session(TARGET_SESSION, msg)
                if ok: msg_count += 1

                print(f"[{ts}] #{cycle:5d} y={s['height_m']:8.4f}m v={s['velocity_ms']:7.4f}m/s "
                      f"{flag:4s} send={'OK' if ok else 'FAIL'} msgs={msg_count}", flush=True)

                if s["grounded"]:
                    time.sleep(2)
                    body.reset(INIT_H)

    except KeyboardInterrupt:
        print(f"\n[PhysicsAgent] 停止 | 共发送 {msg_count} 条消息")
    except Exception as e:
        traceback.print_exc()
    finally:
        gw.close()

if __name__ == "__main__":
    main()
