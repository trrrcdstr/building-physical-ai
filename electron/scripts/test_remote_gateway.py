# -*- coding: utf-8 -*-
"""测试远程 Gateway 连接"""
import websocket
import json
import time
import threading

WS_URL = 'ws://192.168.3.11:28789'

def on_message(ws, msg):
    data = json.loads(msg)
    print(f'< {json.dumps(data, ensure_ascii=False)[:200]}')
    
    # 处理 challenge
    if data.get('type') == 'event' and data.get('event') == 'connect.challenge':
        nonce = data.get('payload', {}).get('nonce')
        print(f'收到 challenge nonce: {nonce}')
        # 回应 challenge (用 connect)
        ws.send(json.dumps({
            'type': 'connect',
            'params': {
                'client.id': 'gateway-client',
                'mode': 'backend',
                'nonce': nonce
            }
        }))
        print('> 发送 connect 响应')

def on_error(ws, err):
    print(f'错误: {err}')

def on_open(ws):
    print(f'连接 {WS_URL} 成功!')
    # 发送初始 connect
    ws.send(json.dumps({
        'type': 'connect',
        'params': {
            'client.id': 'gateway-client',
            'mode': 'backend'
        }
    }))
    print('> 发送初始 connect')

def on_close(ws, code, reason):
    print(f'关闭: code={code} reason={reason}')

if __name__ == '__main__':
    ws = websocket.WebSocketApp(WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    t = threading.Thread(target=lambda: ws.run_forever(), daemon=True)
    t.start()
    
    # 等待一段时间观察
    time.sleep(10)
    print('测试结束')