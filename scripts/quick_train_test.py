"""快速训练测试"""

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
print("快速训练测试")
print("=" * 60)

# 配置
training_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\gaussian_training\images")
output_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\gaussian_models")
output_dir.mkdir(exist_ok=True)

# 找一个场景
scene_dir = training_dir / "室内_家庭"
if not scene_dir.exists():
    scene_dir = list(training_dir.iterdir())[0]

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

# 初始化高斯
N = 200  # 高斯数量
positions = torch.randn(N, 3) * 3.0
scales = torch.ones(N, 3) * 0.3
colors = torch.rand(N, 3)
opacities = torch.ones(N, 1) * 0.5

positions.requires_grad = True
scales.requires_grad = True
colors.requires_grad = True
opacities.requires_grad = True

print(f"初始化 {N} 个高斯")

# 简单渲染函数
def render_simple(positions, colors, opacities, image_size=(120, 160)):
    """超简化渲染"""
    C, H, W = 3, image_size[0], image_size[1]
    image = torch.zeros(C, H, W)
    
    # 投影到XY平面
    screen_x = (positions[:, 0] / 5.0 + 1.0) * W / 2
    screen_y = (positions[:, 1] / 5.0 + 1.0) * H / 2
    
    for i in range(len(positions)):
        x, y = int(screen_x[i].item()), int(screen_y[i].item())
        if 0 <= x < W and 0 <= y < H:
            image[:, y, x] = colors[i] * opacities[i]
    
    return image

# 训练
print("\n开始训练...")
optimizer = optim.Adam([positions, colors, opacities], lr=0.01)
target = images[0]  # 用第一张图作为目标

start_time = time.time()
for iter in range(200):
    rendered = render_simple(positions, colors, opacities)
    loss = torch.nn.functional.mse_loss(rendered, target)
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    if (iter + 1) % 50 == 0:
        print(f"  迭代 {iter+1}, 损失: {loss.item():.4f}")

elapsed = time.time() - start_time
print(f"\n完成! 时间: {elapsed:.1f}s")

# 保存结果
result = {
    'scene': scene_dir.name,
    'num_gaussians': N,
    'final_loss': loss.item(),
    'training_time': elapsed,
    'positions': positions.detach().numpy().tolist(),
    'colors': colors.detach().numpy().tolist()
}

output_path = output_dir / f"{scene_dir.name}_test.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"保存到: {output_path}")
print("=" * 60)
