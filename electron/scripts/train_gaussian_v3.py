"""简化训练 - 向量化版本"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from pathlib import Path
import json
import time

print("=" * 60)
print("简化训练 - 向量化高斯Splatting")
print("=" * 60)

# 配置
training_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\gaussian_training\images")
output_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\gaussian_models")
output_dir.mkdir(exist_ok=True)

# 找一个场景
scene_dir = training_dir / "室内_家庭"
print(f"\n场景: {scene_dir.name}")

# 加载图片
images = []
for img_path in sorted(scene_dir.glob("*.jpg"))[:5]:
    try:
        img = Image.open(img_path).convert('RGB').resize((160, 120))
        img_array = np.array(img).astype(np.float32) / 255.0
        images.append(torch.from_numpy(img_array).permute(2, 0, 1))
    except Exception as e:
        print(f"  跳过: {img_path.name}")

print(f"加载 {len(images)} 张图片")

if len(images) == 0:
    print("没有图片，退出")
    sys.exit(0)

# 高斯参数
N = 300  # 高斯数量
H, W = 120, 160

# 初始化高斯
positions = torch.rand(N, 2) * torch.tensor([W, H]).float()  # 随机位置
scales = torch.ones(N) * 10.0  # 高斯半径
colors = torch.rand(N, 3)  # RGB

positions.requires_grad = True
scales.requires_grad = True
colors.requires_grad = True

print(f"初始化 {N} 个高斯")

# 向量化高斯渲染
def render_gaussians_vectorized(positions, scales, colors, H=120, W=160):
    """向量化高斯渲染"""
    N = positions.shape[0]
    
    # 创建坐标网格 [H, W, 2]
    y_coords = torch.arange(H, dtype=torch.float32)
    x_coords = torch.arange(W, dtype=torch.float32)
    grid = torch.stack(torch.meshgrid(y_coords, x_coords, indexing='ij'), dim=-1)  # [H, W, 2]
    
    # 计算每个像素到每个高斯的距离 [H, W, N]
    # positions: [N, 2] -> [1, 1, N, 2]
    # grid: [H, W, 2] -> [H, W, 1, 2]
    pos_expanded = positions.view(1, 1, N, 2)
    grid_expanded = grid.unsqueeze(2)
    
    dist_sq = ((grid_expanded - pos_expanded) ** 2).sum(dim=-1)  # [H, W, N]
    
    # 计算高斯权重
    scales_expanded = scales.view(1, 1, N)
    weights = torch.exp(-0.5 * dist_sq / (scales_expanded ** 2))  # [H, W, N]
    
    # 归一化权重
    weights = weights / (weights.sum(dim=-1, keepdim=True) + 1e-6)
    
    # 加权颜色
    colors_expanded = colors.view(1, 1, N, 3)  # [1, 1, N, 3]
    weights_expanded = weights.unsqueeze(-1)  # [H, W, N, 1]
    
    image = (weights_expanded * colors_expanded).sum(dim=2)  # [H, W, 3]
    image = image.permute(2, 0, 1)  # [3, H, W]
    
    return image

# 训练
print("\n开始训练...")
optimizer = torch.optim.Adam([positions, scales, colors], lr=0.1)
target = images[0]

start_time = time.time()
for iter in range(200):
    rendered = render_gaussians_vectorized(positions, scales, colors)
    loss = F.mse_loss(rendered, target)
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    # 约束
    with torch.no_grad():
        positions.data.clamp_(0, max(W, H))
        scales.data.clamp_(1, 30)
        colors.data.clamp_(0, 1)
    
    if (iter + 1) % 50 == 0:
        print(f"  迭代 {iter+1}, 损失: {loss.item():.4f}")

elapsed = time.time() - start_time
print(f"\n完成! 时间: {elapsed:.1f}s, 最终损失: {loss.item():.4f}")

# 保存结果
result = {
    'scene': scene_dir.name,
    'num_gaussians': N,
    'final_loss': loss.item(),
    'training_time': elapsed,
    'image_size': [H, W],
    'gaussians': {
        'positions': positions.detach().numpy().tolist(),
        'scales': scales.detach().numpy().tolist(),
        'colors': colors.detach().numpy().tolist()
    }
}

output_path = output_dir / f"{scene_dir.name}_v3.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"保存到: {output_path}")

# 保存渲染结果
rendered_np = rendered.detach().numpy().transpose(1, 2, 0) * 255
rendered_img = Image.fromarray(rendered_np.astype(np.uint8))
rendered_img.save(output_dir / f"{scene_dir.name}_rendered_v3.png")

target_np = target.numpy().transpose(1, 2, 0) * 255
target_img = Image.fromarray(target_np.astype(np.uint8))
target_img.save(output_dir / f"{scene_dir.name}_target_v3.png")

print(f"渲染结果: {output_dir / f'{scene_dir.name}_rendered_v3.png'}")
print("=" * 60)
