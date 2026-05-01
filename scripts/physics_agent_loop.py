# -*- coding: utf-8 -*-
"""
Physics Agent - 每 500ms 读取 world_state.json → 自由落体仿真 → 写回
"""
import json, time, os, threading
from datetime import datetime

# ===== 配置 =====
# ===== 数据目录 =====
UNC_BASE  = r"\\192.168.3.11\physics\bus"
LOCAL_BASE = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data"
STATE_FILE = os.path.join(UNC_BASE, "world_state.json")
G = 9.81           # m/s²
DT = 0.001         # 仿真步长 s
POLL_MS = 500      # 轮询间隔 ms
INIT_H = 10.0     # 初始高度 m

# ===== 物理引擎：自由落体 =====
class FallingBody:
    def __init__(self, h=INIT_H):
        self.h = float(h)
        self.v = 0.0
        self.t = 0.0
        self.grounded = False
        self._grounded_at = None

    def step(self, dt=DT):
        if self.grounded:
            return
        self.v += G * dt
        self.h -= self.v * dt
        self.t += dt
        if self.h <= 0:
            self.h = 0.0
            self.v = 0.0
            self.grounded = True
            self._grounded_at = self.t

    def reset(self, h=INIT_H):
        self.h = float(h)
        self.v = 0.0
        self.t = 0.0
        self.grounded = False
        self._grounded_at = None

    def to_dict(self):
        return {
            "height_m":   round(self.h, 6),
            "velocity_ms": round(self.v, 6),
            "time_s":      round(self.t, 6),
            "grounded":    self.grounded,
        }

# ===== 自动选择数据目录 =====
def resolve_path():
    """优先 UNC 网络路径，不可用则回退本地"""
    try:
        if not os.path.exists(UNC_BASE):
            os.makedirs(UNC_BASE, exist_ok=True)
        test = os.path.join(UNC_BASE, ".physics_probe")
        with open(test, "w") as f:
            f.write("ok")
        os.remove(test)
        return os.path.join(UNC_BASE, "world_state.json")
    except Exception:
        return os.path.join(LOCAL_BASE, "world_state.json")

ACTIVE_PATH = None  # 启动时确定

# ===== 读取 / 写入 world_state.json =====
def read_state():
    if not os.path.exists(ACTIVE_PATH):
        return None
    try:
        with open(ACTIVE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def write_state(data):
    with open(ACTIVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def patch_state(extra):
    """只更新 extra 中的字段，保留其余字段"""
    state = read_state() or {}
    state.update(extra)
    write_state(state)

# ===== 主循环 =====
def run():
    body = FallingBody(INIT_H)
    cycle = 0
    last_time = time.time()
    start = time.time()
    reset_pending = False

    global ACTIVE_PATH
    ACTIVE_PATH = resolve_path()
    is_unc = ACTIVE_PATH == STATE_FILE

    print(f"[PhysicsAgent] 启动")
    print(f"  UNC 目录:  {UNC_BASE}")
    print(f"  本地回退:  {LOCAL_BASE}")
    print(f"  状态文件:  {ACTIVE_PATH}")
    print(f"  {'✅ 网络' if ACTIVE_PATH.startswith('\\\\') else '⚠️ 本地回退'}")
    print(f"  轮询间隔:  {POLL_MS}ms | 重力: {G} m/s² | 步长: {DT}s")
    print()

    try:
        while True:
            cycle += 1

            # --- 物理仿真：dt 内步进 ---
            body.step(DT)

            now = time.time()
            wall_elapsed = round(now - start, 3)

            # --- 每 POLL_MS 同步到文件 ---
            if now - last_time >= POLL_MS / 1000.0:
                last_time = now

                # 从 world_state.json 读取外部指令（如有重置请求）
                ext = read_state()
                cmd = (ext or {}).get("physics_command", "").strip().lower()
                if cmd == "reset" and body.grounded:
                    body.reset(INIT_H)
                    patch_state({"physics_command": ""})
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] === 重置 {INIT_H}m ===")

                # 写入仿真结果
                patch_state({
                    "physics_frame": cycle,
                    "physics_wall_clock_s": wall_elapsed,
                    "physics_sim_time_s": round(body.t, 6),
                    "falling_body": body.to_dict(),
                    "physics_updated_at": datetime.now().isoformat(),
                })

                # 日志（屏显）
                flag = "落地" if body.grounded else "↓"
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"#{cycle:5d}  y={body.h:8.4f}m  v={body.v:7.4f}m/s  "
                      f"t={body.t:.4f}s  {flag:4s}  "
                      f"| wall={wall_elapsed:.1f}s")

                # 落地后自动重置
                if body.grounded and not reset_pending:
                    reset_pending = True
                    def delayed_reset():
                        time.sleep(2)
                        body.reset(INIT_H)
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] === 自动重置 {INIT_H}m ===")
                    threading.Thread(target=delayed_reset, daemon=True).start()

    except KeyboardInterrupt:
        print("\n[PhysicsAgent] 已停止.")
        # 最后写一次最终状态
        patch_state({"physics_status": "stopped", "physics_frame": cycle})


if __name__ == "__main__":
    run()
