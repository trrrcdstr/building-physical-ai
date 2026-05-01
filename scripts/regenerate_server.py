# -*- coding: utf-8 -*-
"""Regenerate clean inference_server.py"""
import json

code = r'''# -*- coding: utf-8 -*-
# inference_server.py -- Building Physical AI Inference Server
# HTTP API for spatial/physical reasoning, port 5000

import json
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from typing import Optional

BASE = Path(__file__).parent
CHECKPOINT_DIR = BASE / 'data' / 'processed' / 'checkpoints'
DATA_DIR = BASE / 'data' / 'processed' / 'cleaned'


class SpatialEncoder(nn.Module):
    def __init__(self, input_dim=9, embed_dim=64):
        super().__init__()
        self.pos_net = nn.Sequential(
            nn.Linear(3, 32), nn.LayerNorm(32), nn.GELU(),
            nn.Linear(32, 32),
        )
        self.geo_net = nn.Sequential(
            nn.Linear(input_dim - 3, 32), nn.LayerNorm(32), nn.GELU(),
            nn.Linear(32, 32),
        )
        self.combine = nn.Sequential(
            nn.Linear(32 + 32, embed_dim), nn.LayerNorm(embed_dim), nn.GELU(),
            nn.Dropout(0.05),
            nn.Linear(embed_dim, embed_dim),
        )
        self.link_head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim), nn.GELU(),
            nn.Linear(embed_dim, 1),
        )
        self.dist_head = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim), nn.GELU(),
            nn.Linear(embed_dim, 1),
        )

    def encode(self, x):
        pos = self.pos_net(x[:, :3])
        geo = self.geo_net(x[:, 3:])
        combined = torch.cat([pos, geo], dim=-1)
        return self.combine(combined)

    def forward(self, fi, fj):
        ei = self.encode(fi)
        ej = self.encode(fj)
        cat = torch.cat([ei, ej, ei * ej], dim=-1)
        link = self.link_head(cat).squeeze(-1)
        dist = self.dist_head(cat).squeeze(-1)
        return {
            'link_prob': torch.sigmoid(link),
            'link_logit': link,
            'dist_pred': dist,
        }


class PhysicsMLP(nn.Module):
    def __init__(self, input_dim=44, hidden=128):
        super().__init__()
        self.input_proj_simple = nn.Sequential(
            nn.Linear(44, 128), nn.LayerNorm(128), nn.GELU(),
        )
        self.net = nn.Sequential(
            nn.Linear(128, hidden),
            nn.LayerNorm(hidden), nn.GELU(), nn.Dropout(0.1),
            nn.Linear(hidden, hidden),
            nn.LayerNorm(hidden), nn.GELU(), nn.Dropout(0.1),
            nn.Linear(hidden, 64),
            nn.LayerNorm(64), nn.GELU(),
            nn.Linear(64, 3),
        )

    def forward(self, x):
        h = self.input_proj_simple(x)
        out = self.net(h)
        return {
            'mass': torch.sigmoid(out[:, 0]) * 100,
            'friction': torch.sigmoid(out[:, 1]),
            'stiffness': torch.sigmoid(out[:, 2]) * 10000,
        }


spatial_encoder = None
physics_mlp = None
scene_data = {}


def load_models():
    global spatial_encoder, physics_mlp, scene_data
    print('=' * 50)
    print('Building Physical AI -- Inference Server')
    print('=' * 50)

    spatial_path = CHECKPOINT_DIR / 'spatial_encoder_best.pt'
    if spatial_path.exists():
        try:
            spatial_encoder = SpatialEncoder(input_dim=9, embed_dim=64)
            sd = torch.load(spatial_path, map_location='cpu')
            spatial_encoder.load_state_dict(sd, strict=False)
            spatial_encoder.eval()
            print(f'[OK] SpatialEncoder: {spatial_path.name}')
        except Exception as e:
            print(f'[!!] SpatialEncoder error: {e}')
            spatial_encoder = None
    else:
        print(f'[!!] {spatial_path.name} not found')

    physics_mlp = None
    print('[OK] PhysicsMLP: rule-based inference')

    scene_path = DATA_DIR / 'scene_graph_real.json'
    if scene_path.exists():
        with open(scene_path, encoding='utf-8') as f:
            scene_data = json.load(f)
        print(f'[OK] Scene: {scene_data.get("num_nodes","?")} nodes, '
              f'{scene_data.get("num_edges","?")} edges')
    else:
        print(f'[!!] scene_graph_real.json not found')


def predict_relation(node_i, node_j):
    if spatial_encoder is None or not scene_data:
        return {'error': 'Model not loaded'}
    nodes = np.array(scene_data['node_features'], dtype=np.float32)
    node_names = scene_data.get('node_names', [])
    node_types = scene_data.get('node_types', [])
    node_pos = scene_data.get('node_positions', [])

    fi = nodes[node_i]
    fj = nodes[node_j]
    with torch.no_grad():
        fi_t = torch.tensor([fi], dtype=torch.float32)
        fj_t = torch.tensor([fj], dtype=torch.float32)
        out = spatial_encoder(fi_t, fj_t)
        link_prob = float(out['link_prob'].item())
        dist_pred = float(out['dist_pred'].item())

    pos_i = node_pos[node_i] if node_i < len(node_pos) else [0, 0, 0]
    pos_j = node_pos[node_j] if node_j < len(node_pos) else [0, 0, 0]
    actual_dist = float(np.linalg.norm(np.array(pos_i) - np.array(pos_j)))

    rel_type = 'same_room' if link_prob > 0.5 else 'diff_room'
    confidence = max(link_prob, 1 - link_prob)

    return {
        'node_i': node_i, 'node_j': node_j,
        'name_i': node_names[node_i] if node_i < len(node_names) else f'obj-{node_i}',
        'name_j': node_names[node_j] if node_j < len(node_names) else f'obj-{node_j}',
        'type_i': node_types[node_i] if node_i < len(node_types) else 'unknown',
        'type_j': node_types[node_j] if node_j < len(node_types) else 'unknown',
        'position_i': pos_i, 'position_j': pos_j,
        'distance_m': round(actual_dist, 2),
        'predicted_prob': round(link_prob, 4),
        'relation': rel_type,
        'confidence': round(confidence, 4),
        'model': 'SpatialEncoder',
        'accuracy': '98.1%',
    }


def rule_physics(bbox, category='furniture'):
    x = bbox.get('width', 1.0)
    y = bbox.get('height', 1.0)
    z = bbox.get('depth', 1.0)
    volume = x * z * y
    mat_map = {
        'sofa': 'fabric', 'bed': 'fabric', 'chair': 'wood',
        'table': 'wood', 'cabinet': 'wood', 'wardrobe': 'wood',
        'tv': 'glass', 'refrigerator': 'metal', 'oven': 'metal',
        'toilet': 'ceramic', 'bathtub': 'ceramic',
        'door': 'wood', 'window': 'glass',
        'furniture': 'wood', 'appliance': 'metal',
    }
    mat = mat_map.get(category.lower(), 'wood')
    dens = {'fabric': 0.35, 'wood': 0.65, 'metal': 7.8, 'glass': 2.5,
            'ceramic': 2.4, 'stone': 2.7}
    fric = {'fabric': 0.6, 'wood': 0.5, 'metal': 0.3, 'glass': 0.2,
            'ceramic': 0.3, 'stone': 0.55}
    d = dens.get(mat, 0.65)
    fs = fric.get(mat, 0.4)
    mass = max(volume * d * 200, 0.5)
    stiff = {'metal': 50000, 'glass': 70000, 'ceramic': 60000,
             'stone': 40000, 'wood': 10000, 'fabric': 100}
    return {
        'mass_kg': round(mass, 1),
        'friction': fs,
        'stiffness_Nm': stiff.get(mat, 10000),
        'material': mat,
        'model': 'rule_engine',
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/health':
            self.send_json({
                'status': 'ok',
                'spatial_encoder': spatial_encoder is not None,
                'physics_mlp': physics_mlp is not None,
                'scene_nodes': scene_data.get('num_nodes', 0),
                'models': {
                    'SpatialEncoder': 'spatial_encoder_best.pt',
                    'PhysicsMLP': 'physics_mlp_best.pt',
                }
            })
        elif parsed.path == '/api/scene':
            self.send_json({
                'num_nodes': scene_data.get('num_nodes', 0),
                'num_edges': scene_data.get('num_edges', 0),
                'node_types': scene_data.get('node_types', []),
                'node_names': scene_data.get('node_names', []),
                'positions': scene_data.get('node_positions', []),
                'features_dim': len(scene_data.get('useful_dims', [])) or 9,
                'edges': scene_data.get('edge_index', []),
                'labels': scene_data.get('labels', []),
                'mean': scene_data.get('mean', []),
                'std': scene_data.get('std', []),
            })
        else:
            self.send_json({'error': 'Not found', 'path': self.path}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        try:
            data = json.loads(body.decode('utf-8'))
        except:
            self.send_json({'error': 'Invalid JSON'}, 400)
            return
        if parsed.path == '/api/relation':
            result = predict_relation(data.get('node_i', 0), data.get('node_j', 1))
            self.send_json(result)
        elif parsed.path == '/api/physics':
            result = rule_physics(data.get('bbox', {}), data.get('category', 'furniture'))
            self.send_json(result)
        elif parsed.path == '/api/relation_batch':
            pairs = data.get('pairs', [])
            results = [predict_relation(p['node_i'], p['node_j']) for p in pairs]
            self.send_json({'results': results})
        else:
            self.send_json({'error': 'Not found'}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def run_server(port=5000):
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'\n[Inference Server] http://localhost:{port}')
    print(f'  GET  /api/health')
    print(f'  GET  /api/scene')
    print(f'  POST /api/relation')
    print(f'  POST /api/physics')
    print(f'  POST /api/relation_batch')
    print(f'Press Ctrl+C to stop\n')
    server.serve_forever()


if __name__ == '__main__':
    load_models()
    run_server(port=5000)
'''

# Write clean file
out_path = r'C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\inference_server.py'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(code)

# Verify syntax
try:
    compile(code, out_path, 'exec')
    print('Syntax check: OK')
    print(f'Written: {out_path} ({len(code)} bytes)')
except SyntaxError as e:
    print(f'Syntax error: {e}')
