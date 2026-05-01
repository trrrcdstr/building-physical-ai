"""
GPU多场景高斯Splatting训练
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from pathlib import Path
import json, time, os
from collections import defaultdict

print("=" * 60)
print("GPU 高斯Splatting 多场景训练")
print("=" * 60)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

DB_PATH = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\RENDERING_DATABASE.json")
with open(DB_PATH, 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f"\n数据库: {db['meta']['total_images']} 张效果图")

by_sub = defaultdict(list)
for r in db['records']:
    by_sub[r['subcategory']].append(r)

SCENE_MIN = 5
usable = {k: v for k, v in sorted(by_sub.items(), key=lambda x: -len(x[1])) if len(v) >= SCENE_MIN}

print(f"\n可用场景 ({len(usable)} 个):")
for name, recs in sorted(usable.items(), key=lambda x: -len(x[1])):
    print(f"  {name}: {len(recs)} 张")

def render_gaussians(pos, scale, color, H, W):
    N = pos.shape[0]
    y = torch.arange(H, dtype=torch.float32, device=pos.device)
    x = torch.arange(W, dtype=torch.float32, device=pos.device)
    grid = torch.stack(torch.meshgrid(y, x, indexing='ij'), dim=-1)
    d2 = ((grid.unsqueeze(2) - pos.view(1, 1, N, 2)) ** 2).sum(dim=-1)
    w = torch.exp(-0.5 * d2 / (scale.view(1, 1, N) ** 2 + 1e-6))
    w = w / (w.sum(dim=-1, keepdim=True) + 1e-6)
    img = (w.unsqueeze(-1) * color.view(1, 1, N, 3)).sum(dim=2)
    return img.permute(2, 0, 1)

def train_scene(name, records, cfg):
    N = cfg['n_gaussians']
    H, W = cfg['image_h'], cfg['image_w']
    iters = cfg['iters']
    lr = cfg['lr']
    n_imgs = cfg['n_images']

    print(f"\n--- 训练场景: {name} ({len(records)} 张) ---")

    images = []
    for rec in records[:n_imgs]:
        path_str = rec['path'].replace('file:///', '')
        img_path = Path(path_str)
        try:
            img = Image.open(img_path).convert('RGB').resize((W, H))
            arr = np.array(img).astype(np.float32) / 255.0
            images.append(torch.from_numpy(arr).permute(2, 0, 1).to(device))
        except Exception as e:
            print(f"  跳过: {rec['filename']}")

    if len(images) == 0:
        print(f"  无可用图片，跳过")
        return None

    print(f"  加载 {len(images)} 张图片, 尺寸 {W}x{H}")

    target_img = images[0]

    positions = torch.rand(N, 2, device=device) * torch.tensor([W, H], device=device, dtype=torch.float32)
    scales = torch.ones(N, device=device) * cfg['init_scale']
    colors = torch.rand(N, 3, device=device)
    positions.requires_grad_(True)
    scales.requires_grad_(True)
    colors.requires_grad_(True)

    optimizer = torch.optim.Adam([positions, scales, colors], lr=lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=iters)

    start = time.time()
    for i in range(iters):
        target = images[i % len(images)]
        rendered = render_gaussians(positions, scales, colors, H, W)
        loss = F.mse_loss(rendered, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        scheduler.step()
        with torch.no_grad():
            positions.data.clamp_(0, max(W, H))
            scales.data.clamp_(1, 50)
            colors.data.clamp_(0, 1)
        if (i + 1) % (iters // 4) == 0:
            print(f"  iter {i+1}/{iters}, loss={loss.item():.4f}")

    elapsed = time.time() - start
    final_loss = loss.item()
    print(f"  完成! {elapsed:.1f}s, loss={final_loss:.4f}")

    with torch.no_grad():
        rendered_final = render_gaussians(positions, scales, colors, H, W)

    result = {
        'scene': name,
        'num_images': len(records),
        'images_trained': len(images),
        'n_gaussians': N,
        'image_size': [H, W],
        'iters': iters,
        'final_loss': float(final_loss),
        'training_time_sec': float(elapsed),
        'gaussians': {
            'positions': positions.detach().cpu().numpy().tolist(),
            'scales': scales.detach().cpu().numpy().tolist(),
            'colors': colors.detach().cpu().numpy().tolist(),
        }
    }
    return result, rendered_final, target_img

def get_cfg(n_images):
    if n_images >= 50:
        return {'n_gaussians': 500, 'image_h': 120, 'image_w': 160, 'iters': 500, 'lr': 0.05, 'n_images': 30, 'init_scale': 15}
    elif n_images >= 20:
        return {'n_gaussians': 300, 'image_h': 120, 'image_w': 160, 'iters': 300, 'lr': 0.08, 'n_images': 20, 'init_scale': 12}
    else:
        return {'n_gaussians': 200, 'image_h': 100, 'image_w': 140, 'iters': 200, 'lr': 0.1, 'n_images': 10, 'init_scale': 10}

OUT_DIR = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\gaussian_models")
OUT_DIR.mkdir(parents=True, exist_ok=True)

results = []
for name, records in sorted(usable.items(), key=lambda x: -len(x[1])):
    cfg = get_cfg(len(records))
    ret = train_scene(name, records, cfg)
    if ret is None:
        continue
    result, rendered_final, target_img = ret
    results.append(result)
    fname = f"{name}_gpu.json"
    with open(OUT_DIR / fname, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    if rendered_final is not None:
        rendered_np = rendered_final.cpu().numpy().transpose(1, 2, 0) * 255
        Image.fromarray(rendered_np.astype(np.uint8)).save(OUT_DIR / f"{name}_rendered.png")
        target_np = target_img.cpu().numpy().transpose(1, 2, 0) * 255
        Image.fromarray(target_np.astype(np.uint8)).save(OUT_DIR / f"{name}_target.png")

print("\n" + "=" * 60)
print("训练汇总")
print("=" * 60)
total_time = sum(r['training_time_sec'] for r in results)
for r in results:
    print(f"  {r['scene']}: loss={r['final_loss']:.4f} ({r['training_time_sec']:.1f}s, {r['images_trained']}张)")
print(f"\n总计: {len(results)} 个场景, {total_time:.1f}s")
print(f"输出: {OUT_DIR}")
