"""快速训练测试 - 多场景"""

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
print("多场景训练测试")
print("=" * 60)

# 配置
training_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\gaussian_training\images")
output_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\gaussian_models")
output_dir.mkdir(exist_ok=True)

# 找场景
scenes = []
for scene_dir in training_dir.iterdir():
    if scene_dir.is_dir():
        count = len(list(scene_dir.glob("*.jpg")))
        if count > 0:
            scenes.append((scene_dir, count))

scenes.sort(key=lambda x: x[1], reverse=True)

print(f"\n找到 {len(scenes)} 个场景:")
for scene_dir, count in scenes[:5]:
    print(f"  {scene_dir.name}: {count} 张")

# 训练参数
N = 300  # 高斯数
H, W = 120, 160  # 图片尺寸
iterations = 300
lr = 0.1

# 向量化渲染函数
def render_gaussians(positions, scales, colors, H, W):
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

# 训练每个场景
results = []

for scene_dir, count in scenes[:3]:
    scene_name = scene_dir.name
    print(f"\n{'='*60}")
    print(f"训练: {scene_name} ({count} 张)")
    
    # 加载图片
    images = []
    for img_path in sorted(scene_dir.glob("*.jpg"))[:3]:
        img = Image.open(img_path).convert('RGB').resize((W, H))
        img_array = np.array(img).astype(np.float32) / 255.0
        images.append(torch.from_numpy(img_array).permute(2, 0, 1))
    
    print(f"  加载 {len(images)} 张")
    
    # 初始化高斯
    positions = torch.rand(N, 2) * torch.tensor([W, H]).float()
    scales = torch.ones(N) * 10.0
    colors = torch.rand(N, 3)
    
    positions.requires_grad = True
    scales.requires_grad = True
    colors.requires_grad = True
    
    # 训练
    optimizer = torch.optim.Adam([positions, scales, colors], lr=lr)
    target = images[0]
    
    start_time = time.time()
    for iter in range(iterations):
        rendered = render_gaussians(positions, scales, colors, H, W)
        loss = F.mse_loss(rendered, target)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        with torch.no_grad():
            positions.data.clamp_(0, max(W, H))
            scales.data.clamp_(1, 30)
            colors.data.clamp_(0, 1)
        
        if (iter + 1) % 100 == 0:
            print(f"  迭代 {iter+1}, 损失: {loss.item():.4f}")
    
    elapsed = time.time() - start_time
    print(f"  完成: {elapsed:.1f}s, 损失: {loss.item():.4f}")
    
    # 保存
    result = {
        'scene': scene_name,
        'num_gaussians': N,
        'final_loss': loss.item(),
        'training_time': elapsed
    }
    
    output_path = output_dir / f"{scene_name}_v4.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    results.append(result)

# 总结
print("\n" + "=" * 60)
print("训练总结:")
for r in results:
    print(f"  {r['scene']}: {r['num_gaussians']} 高斯, 损失 {r['final_loss']:.4f}, 时间 {r['training_time']:.1f}s")
print("=" * 60)
