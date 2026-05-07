"""图片 HTTP 代理服务器
把 Desktop 效果图文件夹映射为 HTTP 服务
解决 file:// 协议的浏览器 CORS 限制

Usage: python image_proxy.py
Then access: http://localhost:8888/效果图/餐厅/1.jpg
"""
import os
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 效果图根目录（Desktop）
RENDER_ROOT = r"C:\Users\Administrator\Desktop\设计数据库\效果图"

class ImageProxyHandler(SimpleHTTPRequestHandler):
    """支持中文 URL 的图片代理"""

    def translate_path(self, path):
        # URL decode + 安全清理
        try:
            decoded = urllib.parse.unquote(path)
        except Exception:
            decoded = path
        # 去掉前导 /
        decoded = decoded.lstrip('/')
        # 防止 .. 路径穿越
        decoded = os.path.normpath(decoded).replace('\\', '/')
        if decoded.startswith('..'):
            decoded = decoded[3:]
        full = os.path.join(RENDER_ROOT, decoded)
        # 确保在 RENDER_ROOT 下
        norm_root = os.path.normpath(RENDER_ROOT)
        if not os.path.normpath(full).startswith(norm_root):
            return None
        return full

    def do_GET(self):
        path = self.translate_path(self.path)
        if path is None or not os.path.isfile(path):
            self.send_error(404, f"Not found: {self.path}")
            return
        # 图片 MIME
        ext = os.path.splitext(path)[1].lower()
        mime_map = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif',
            '.webp': 'image/webp', '.bmp': 'image/bmp',
        }
        mime = mime_map.get(ext, 'application/octet-stream')
        try:
            with open(path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', len(data))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")


def main():
    if not os.path.isdir(RENDER_ROOT):
        print(f"ERROR: 效果图目录不存在: {RENDER_ROOT}")
        return
    # 统计
    count = sum(len(files) for _, _, files in os.walk(RENDER_ROOT))
    print(f"效果图目录: {RENDER_ROOT}")
    print(f"图片总数: {count}")
    print(f"代理地址: http://localhost:8888/")
    print(f"示例: http://localhost:8888/餐厅/1.jpg")
    print()
    server = HTTPServer(('0.0.0.0', 8888), ImageProxyHandler)
    print("图片代理服务启动，按 Ctrl+C 停止")
    server.serve_forever()


if __name__ == '__main__':
    main()
