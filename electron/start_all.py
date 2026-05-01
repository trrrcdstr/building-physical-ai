# -*- coding: utf-8 -*-
"""
一键启动脚本 - 同时启动前端 + 推理服务器 + Cloudflare隧道
用法: 双击此文件 或 python start_all.py
"""
import subprocess
import time
import os
import sys
import re
import signal
import threading

CF_PATH = os.environ.get('TEMP', os.path.expanduser('~')) + '\\cloudflared.exe'
LOG_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = LOG_DIR
TUNNEL_LOG = os.path.join(LOG_DIR, 'tunnel_url.txt')

class Service:
    def __init__(self, name, cmd, cwd=None):
        self.name = name
        self.cmd = cmd
        self.cwd = cwd or LOG_DIR
        self.proc = None
        self.url = None

    def start(self):
        print(f"[{self.name}] Starting...")
        try:
            self.proc = subprocess.Popen(
                self.cmd,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            print(f"[{self.name}] PID={self.proc.pid}")
            return True
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return False

    def is_running(self):
        if self.proc is None:
            return False
        return self.proc.poll() is None

    def stop(self):
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except:
                self.proc.kill()


def get_tunnel_url():
    """从日志中提取tunnel URL"""
    for log_file in [os.path.join(os.environ.get('TEMP', ''), f'cf_{n}.txt') for n in ['latest', 'out2', 'out', 'stderr']]:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                m = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', content)
                if m:
                    return m.group(0)
            except:
                pass
    return None


def run_tunnel():
    """启动cloudflared隧道"""
    print("\n[Cloudflare Tunnel] Starting...")
    
    # 检查cloudflared
    if not os.path.exists(CF_PATH):
        print(f"[Cloudflare] Downloading cloudflared...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        subprocess.run(['powershell', '-Command', 
            f'[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; '
            f'$wc = New-Object System.Net.WebClient; '
            f'$wc.DownloadFile("{url}", "{CF_PATH}")'], check=True)
        print(f"[Cloudflare] Downloaded to {CF_PATH}")

    log_file = os.path.join(os.environ.get('TEMP', ''), 'cf_tunnel_live.txt')
    proc = subprocess.Popen(
        [CF_PATH, 'tunnel', '--url', 'http://localhost:3000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    url = None
    start = time.time()
    while time.time() - start < 20:
        line = proc.stdout.readline()
        if line:
            print(f"  {line.rstrip()}")
            if not url:
                m = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
                if m:
                    url = m.group(0)
        if proc.poll() is not None:
            print("[Cloudflare] Process exited! Restarting in 5s...")
            time.sleep(5)
            return run_tunnel()  # restart
        time.sleep(0.5)

    if url:
        with open(TUNNEL_LOG, 'w') as f:
            f.write(url)
        print(f"\n*** PUBLIC URL: {url} ***\n")
        print("Keep this window open. Close it to stop the tunnel.")
        # keep alive
        while proc.poll() is None:
            time.sleep(5)
            # write latest log
            with open(log_file, 'w') as f:
                f.write(f"URL: {url}\nActive since: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        return url
    else:
        print("[Cloudflare] Could not get URL in 20s")
        return None


def check_services():
    """检查服务是否在运行"""
    import socket
    for host, port, name in [('127.0.0.1', 3000, 'Frontend'), ('127.0.0.1', 5000, 'Inference')]:
        try:
            sock = socket.socket()
            sock.settimeout(2)
            sock.connect((host, port))
            sock.close()
            print(f"  [{name}] :{port} OK")
        except:
            print(f"  [{name}] :{port} NOT responding")
            return False
    return True


def main():
    print("=" * 50)
    print("Building Physical AI - 一键启动")
    print("=" * 50)

    # 1. 启动推理服务器
    inference = Service(
        "Inference Server",
        [sys.executable, "src/harness/inference_server.py"],
        cwd=FRONTEND_DIR
    )
    inference.start()
    print("[Inference] Waiting 5s to start...")
    time.sleep(5)

    # 2. 启动前端
    frontend = Service(
        "Frontend (Vite)",
        ["npm.cmd", "run", "dev"],
        cwd=os.path.join(FRONTEND_DIR, "web-app")
    )
    frontend.start()
    print("[Frontend] Waiting 6s to start...")
    time.sleep(6)

    # 3. 检查服务
    if check_services():
        print("\nAll services ready!")
        # 4. 启动隧道
        run_tunnel()
    else:
        print("\nSome services failed to start. Check logs above.")

    # 等待所有进程
    try:
        while True:
            time.sleep(10)
            for svc in [inference, frontend]:
                if not svc.is_running():
                    print(f"[{svc.name}] Stopped! Restarting...")
                    svc.start()
                    time.sleep(3)
    except KeyboardInterrupt:
        print("\nStopping all services...")
        inference.stop()
        frontend.stop()
        print("Done.")


if __name__ == '__main__':
    main()
