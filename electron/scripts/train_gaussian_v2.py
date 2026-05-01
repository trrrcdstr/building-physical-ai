"""改进版训练测试 - 带高斯splatting"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from PIL import Image
from pathlib import Path
import json
import time

print("=" * 60)
print("改进版训练测试 - 高斯Splatting")
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
N = 500  # 高斯数量
H, W = 120, 160

# 初始化高斯（均匀分布在图像上）
positions = torch.zeros(N, 2)  # 2D位置
positions[:, 0] = torch.linspace(0, W-1, N)  # X
positions[:, 1] = torch.linspace(0, H-1, N)  # Y

scales = torch.ones(N) * 5.0  # 高斯半径
colors = torch.rand(N, 3)  # RGB
opacities = torch.ones(N) * 0.8

positions.requires_grad = True
scales.requires_grad = True
colors.requires_grad = True
opacities.requires_grad = True

print(f"初始化 {N} 个高斯")

# 高斯splatting渲染
def render_gaussians(positions, scales, colors, opacities, H=120, W=160):
    """
    高斯splatting渲染
    
    Args:
        positions: [N, 2] 屏幕坐标
        scales: [N] 高斯半径
        colors: [N, 3] RGB
        opacities: [N] 不透明度
    """
    # 创建坐标网格
    y_coords = torch.arange(H, dtype=torch.float32)
    x_coords = torch.arange(W, dtype=torch.float32)
    yy, xx = torch.meshgrid(y_coords, x_coords, indexing='ij')
    
    # 初始化累积buffer
    image = torch.zeros(3, H, W)
    weights = torch.zeros(H, W)
    
    # 对每个高斯
    for i in range(len(positions)):
        cx, cy = positions[i]
        scale = scales[i].clamp(min=1.0, max=20.0)
        color = colors[i]
        opacity = opacities[i].clamp(0, 1)
        
        # 计算影响范围
        radius = int(scale * 3)
        x_min = max(0, int(cx.item() - radius))
        x_max = min(W, int(cx.item() + radius) + 1)
        y_min = max(0, int(cy.item() - radius))
        y_max = min(H, int(cy.item() + radius) + 1)
        
        # 计算高斯权重
        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                dist_sq = (x - cx) ** 2 + (y - cy) ** 2
                weight = torch.exp(-0.5 * dist_sq / (scale ** 2))
                alpha = opacity * weight
                
                # Alpha混合 (避免in-place)
                new_val = image[:, y, x] * (1 - alpha) + color * alpha
                image[:, y, x] = new_val
                weights[y, x] = weights[y, x] * (1 - alpha) + alpha
    
    return image

# 训练
print("\n开始训练...")
optimizer = optim.Adam([positions, scales, colors, opacities], lr=0.01)
target = images[0]  # 用第一张图作为目标

start_time = time.time()
for iter in range(100):
    rendered = render_gaussians(positions, scales, colors, opacities)
    loss = torch.nn.functional.mse_loss(rendered, target)
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    if (iter + 1) % 20 == 0:
        print(f"  迭代 {iter+1}, 损失: {loss.item():.4f}")

elapsed = time.time() - start_time
print(f"\n完成! 时间: {elapsed:.1f}s")

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
        'colors': colors.detach().numpy().tolist(),
        'opacities': opacities.detach().numpy().tolist()
    }
}

output_path = output_dir / f"{scene_dir.name}_gaussian.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"保存到: {output_path}")

# 保存渲染结果对比
rendered_np = rendered.detach().numpy().transpose(1, 2, 0) * 255
rendered_img = Image.fromarray(rendered_np.astype(np.uint8))
rendered_img.save(output_dir / f"{scene_dir.name}_rendered.png")

target_np = target.numpy().transpose(1, 2, 0) * 255
target_img = Image.fromarray(target_np.astype(np.uint8))
target_img.save(output_dir / f"{scene_dir.name}_target.png")

print(f"渲染结果: {output_dir / f'{scene_dir.name}_rendered.png'}")
print(f"目标图片: {output_dir / f'{scene_dir.name}_target.png'}")
print("=" * 60)
