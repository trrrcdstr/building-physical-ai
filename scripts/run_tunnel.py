# -*- coding: utf-8 -*-
"""
Cloudflare Tunnel 持久化运行脚本
"""
import subprocess, time, re, os, sys

CF_PATH = os.environ.get('TEMP', '/tmp') + '\\cloudflared.exe'
LOG_FILE = os.environ['TEMP'] + '\\cf_url_live.txt'

def get_url_from_log(log_content):
    match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', log_content)
    return match.group(0) if match else None

def start_tunnel():
    print('Starting cloudflared tunnel...')
    proc = subprocess.Popen(
        [CF_PATH, 'tunnel', '--url', 'http://localhost:3000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    print(f'PID: {proc.pid}')
    
    url = None
    start = time.time()
    
    while time.time() - start < 30:
        line = proc.stdout.readline()
        if line:
            print(line.rstrip())
            if not url:
                url = get_url_from_log(line)
        if proc.poll() is not None:
            print('Process exited! Restarting...')
            return None
        if url and time.time() - start > 3:
            # URL found and tunnel is live
            break
        time.sleep(0.5)
    
    if url:
        print(f'\n✅ Tunnel LIVE: {url}')
        with open(LOG_FILE, 'w') as f:
            f.write(url)
        print('URL saved. Tunnel running in background.')
        return url
    else:
        print('URL not found in 30s')
        return None

if __name__ == '__main__':
    # Check if cloudflared exists
    if not os.path.exists(CF_PATH):
        print(f'ERROR: cloudflared not found at {CF_PATH}')
        sys.exit(1)
    
    url = start_tunnel()
    if url:
        print(f'\nPublic URL: {url}')
        # Keep running and restarting if needed
        while True:
            try:
                time.sleep(60)
            except KeyboardInterrupt:
                print('\nStopped.')
                break
    else:
        sys.exit(1)
