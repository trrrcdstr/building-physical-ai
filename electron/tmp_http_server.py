# -*- coding: utf-8 -*-
"""Render image HTTP server - serves static images on port 8888"""
import os, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

PORT = 8888

def get_render_dir():
    # Try multiple possible locations
    base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base, 'web-app', 'public', 'rendering'),
        os.path.join(base, 'data', 'rendering'),
        os.path.join(base, 'data', 'rendering_images'),
        os.path.join(base, 'web-app', 'public'),
        base,
    ]
    for d in candidates:
        if os.path.isdir(d):
            # Check if it has image files
            for f in os.listdir(d):
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    return d
    return base

class CORSHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # Suppress log noise

def main():
    render_dir = get_render_dir()
    print(f"[RenderServer] Serving {render_dir} on port {PORT}")
    os.chdir(render_dir)
    server = HTTPServer(('0.0.0.0', PORT), CORSHandler)
    print(f"[RenderServer] Running at http://localhost:{PORT}")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == '__main__':
    main()
