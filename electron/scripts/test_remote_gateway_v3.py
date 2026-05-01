# -*- coding: utf-8 -*-
"""测试远程 Gateway 连接 - 使用正确 token"""
import websocket
import json
import time
import threading

WS_URL = 'ws://192.168.3.11:28789'
REMOTE_TOKEN = 'fe00bf4dd7a9e505f00403c6377556bd013d5d34ec863ae6'

def on_message(ws, msg):
    data = json.loads(msg)
    msg_type = data.get('type')
    event = data.get('event', '')
    
    print(f'< {json.dumps(data, ensure_ascii=False)[:500]}')
    
    # 处理 challenge
    if msg_type == 'event' and event == 'connect.challenge':
        nonce = data.get('payload', {}).get('nonce')
        print(f'\n收到 challenge nonce: {nonce}')
        
        # 用 auth.token 响应
        ws.send(json.dumps({
            'type': 'auth.token',
            'params': {
                'token': REMOTE_TOKEN,
                'nonce': nonce
            }
        }))
        print('> 发送 auth.token (远程token)')

    # 认证成功
    if msg_type == 'response' and data.get('ok'):
        print('\n✅ 认证成功!')
        # 发送测试消息
        ws.send(json.dumps({
            'type': 'req',
            'id': 'test-1',
            'method': 'send',
            'params': {
                'target': 'agent:main:main',
                'content': '来自 Physics Agent 的测试消息'
            }
        }))
        print('> 发送测试消息')

def on_error(ws, err):
    print(f'错误: {err}')

def on_open(ws):
    print(f'连接 {WS_URL} 成功!')
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
    
    time.sleep(10)
    print('\n测试结束')