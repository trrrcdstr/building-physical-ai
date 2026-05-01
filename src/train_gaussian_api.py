"""
train_gaussian_api.py — 3D Gaussian Splatting 训练入口

用法:
    python src/train_gaussian_api.py --scene 室内_家庭 --epochs 300 --num_gaussians 300
    python src/train_gaussian_api.py --scene 室内_工装 --epochs 500 --num_gaussians 500
    python src/train_gaussian_api.py --list

输出: data/gaussian_models/{scene}_model.json
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import json
import time
import os
from pathlib import Path

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).parent.parent
RENDERINGS_DIR = PROJECT_ROOT / "data" / "processed" / "renderings"
MODELS_DIR = PROJECT_ROOT / "data" / "gaussian_models"
MODELS_DIR.mkdir(exist_ok=True)


def list_scenes():
    """列出所有可用训练场景"""
    print("\n可用训练场景:")
    scene_map = {
        "室内_家庭": "家庭场景",
        "室内_工装": "工装场景",
        "室内_餐饮": "餐饮场景",
        "室内_酒店民俗": "酒店民宿",
        "建筑_别墅建筑花园": "别墅花园",
        "建筑_产业园写字楼": "产业园写字楼",
        "建筑_商场综合体": "商场综合体",
        "建筑_市政公园": "市政公园",
        "园林": "园林景观",
    }
    for key, name in scene_map.items():
        scene_dir = RENDERINGS_DIR / key
        if scene_dir.exists():
            count = len(list(scene_dir.glob("*.jpg"))) + len(list(scene_dir.glob("*.png")))
            print(f"  {key} ({name}): {count} 张图")
        else:
            print(f"  {key} ({name}): 目录不存在")


def find_images(scene_name: str, max_images: int = 10):
    """从渲染图目录找图片"""
    scene_dir = RENDERINGS_DIR / scene_name
    if not scene_dir.exists():
        # 尝试模糊匹配
        for d in RENDERINGS_DIR.iterdir():
            if scene_name in d.name or d.name in scene_name:
                scene_dir = d
                break

    if not scene_dir.exists():
        raise FileNotFoundError(f"场景目录不存在: {scene_dir}")

    images = sorted(scene_dir.glob("*.jpg")) + sorted(scene_dir.glob("*.png"))
    images = images[:max_images]
    print(f"找到 {len(images)} 张图片: {scene_dir.name}")
    return images


def render_gaussians_vectorized(positions, scales, colors, H=120, W=160):
    """向量化高斯渲染"""
    N = positions.shape[0]
    y_coords = torch.arange(H, dtype=torch.float32)
    x_coords = torch.arange(W, dtype=torch.float32)
    grid = torch.stack(torch.meshgrid(y_coords, x_coords, indexing='ij'), dim=-1)

    pos_expanded = positions.view(1, 1, N, 2)
    grid_expanded = grid.unsqueeze(2)
    dist_sq = ((grid_expanded - pos_expanded) ** 2).sum(dim=-1)

    scales_expanded = scales.view(1, 1, N)
    weights = torch.exp(-0.5 * dist_sq / (scales_expanded ** 2 + 1e-6))
    weights = weights / (weights.sum(dim=-1, keepdim=True) + 1e-6)

    colors_expanded = colors.view(1, 1, N, 3)
    weights_expanded = weights.unsqueeze(-1)

    image = (weights_expanded * colors_expanded).sum(dim=2)
    return image.permute(2, 0, 1)


def train_scene(scene_name: str, epochs: int = 300, num_gaussians: int = 300, image_size=(120, 160)):
    """训练指定场景"""
    H, W = image_size
    N = num_gaussians

    print(f"\n{'='*60}")
    print(f"训练场景: {scene_name}")
    print(f"高斯数量: {N} | 迭代: {epochs} | 图像: {W}x{H}")
    print(f"{'='*60}")

    # 加载图片
    images = []
    for img_path in find_images(scene_name):
        try:
            img = Image.open(img_path).convert('RGB').resize((W, H))
            img_array = np.array(img).astype(np.float32) / 255.0
            images.append(torch.from_numpy(img_array).permute(2, 0, 1))
        except Exception as e:
            print(f"  跳过 {img_path.name}: {e}")

    if not images:
        print("没有可用图片，退出")
        return None

    print(f"加载 {len(images)} 张图片")

    # 初始化高斯参数
    positions = torch.rand(N, 2) * torch.tensor([W, H]).float()
    scales = torch.ones(N) * (min(W, H) * 0.1)
    colors = torch.rand(N, 3)

    positions.requires_grad = True
    scales.requires_grad = True
    colors.requires_grad = True

    optimizer = torch.optim.Adam([positions, scales, colors], lr=0.1)
    target = images[0]  # 用第一张作为目标

    start_time = time.time()

    for epoch in range(epochs):
        rendered = render_gaussians_vectorized(positions, scales, colors)
        loss = F.mse_loss(rendered, target)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        with torch.no_grad():
            positions.data.clamp_(0, max(W, H))
            scales.data.clamp_(1, min(W, H) * 0.5)
            colors.data.clamp_(0, 1)

        if (epoch + 1) % 50 == 0:
            print(f"  迭代 {epoch+1}/{epochs}, 损失: {loss.item():.4f}")

    elapsed = time.time() - start_time

    # 保存模型
    result = {
        "scene": scene_name,
        "config": {
            "num_gaussians": N,
            "image_width": W,
            "image_height": H,
            "iterations": epochs,
            "lr": 0.1,
        },
        "final_loss": float(loss.item()),
        "training_time": elapsed,
        "gaussians": {
            "num_gaussians": N,
            "positions": positions.detach().numpy().tolist(),
            "scales": scales.detach().numpy().tolist(),
            "colors": colors.detach().numpy().tolist(),
        }
    }

    output_path = MODELS_DIR / f"{scene_name}_model.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 保存渲染预览
    rendered_np = rendered.detach().numpy().transpose(1, 2, 0).clip(0, 1) * 255
    Image.fromarray(rendered_np.astype(np.uint8)).save(MODELS_DIR / f"{scene_name}_rendered.png")

    target_np = target.numpy().transpose(1, 2, 0) * 255
    Image.fromarray(target_np.astype(np.uint8)).save(MODELS_DIR / f"{scene_name}_target.png")

    print(f"\n✅ 完成!")
    print(f"   场景: {scene_name}")
    print(f"   高斯数: {N}")
    print(f"   最终损失: {loss.item():.4f}")
    print(f"   训练时间: {elapsed:.1f}s")
    print(f"   模型: {output_path}")
    print(f"   预览: {MODELS_DIR / f'{scene_name}_rendered.png'}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D Gaussian Splatting 训练")
    parser.add_argument("--scene", type=str, help="场景名称（如：室内_家庭）")
    parser.add_argument("--epochs", type=int, default=300, help="迭代次数（默认300）")
    parser.add_argument("--num-gaussians", type=int, default=300, help="高斯数量（默认300）")
    parser.add_argument("--list", action="store_true", help="列出所有可用场景")
    parser.add_argument("--image-size", type=str, default="160x120", help="图像尺寸（默认160x120）")

    args = parser.parse_args()

    if args.list or not args.scene:
        list_scenes()
        sys.exit(0)

    w, h = map(int, args.image_size.split('x'))
    result = train_scene(args.scene, epochs=args.epochs, num_gaussians=args.num_gaussians, image_size=(h, w))
