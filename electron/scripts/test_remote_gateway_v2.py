# -*- coding: utf-8 -*-
"""测试远程 Gateway 连接 - 正确认证流程"""
import websocket
import json
import time
import threading

WS_URL = 'ws://192.168.3.11:28789'
# 注意：需要从配置中获取 token，或使用 auth.challenge 流程

def on_message(ws, msg):
    data = json.loads(msg)
    msg_type = data.get('type')
    event = data.get('event', '')
    
    print(f'< {json.dumps(data, ensure_ascii=False)[:300]}')
    
    # 处理 challenge - 需要用 auth.token 响应
    if msg_type == 'event' and event == 'connect.challenge':
        nonce = data.get('payload', {}).get('nonce')
        print(f'\n收到 challenge nonce: {nonce}')
        print('需要提供 token 认证...')
        
        # 尝试 auth.token 响应
        ws.send(json.dumps({
            'type': 'auth.token',
            'params': {
                'token': 'test-token',  # 需要正确的 token
                'nonce': nonce
            }
        }))
        print('> 发送 auth.token')

def on_error(ws, err):
    print(f'错误: {err}')

def on_open(ws):
    print(f'连接 {WS_URL} 成功!')
    # 不发 connect，等 challenge
    print('等待 challenge...')

def on_close(ws, code, reason):
    print(f'\n关闭: code={code} reason={reason}')

if __name__ == '__main__':
    ws = websocket.WebSocketApp(WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    t = threading.Thread(target=lambda: ws.run_forever(), daemon=True)
    t.start()
    
    time.sleep(8)
    print('\n测试结束')