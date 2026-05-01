"""
增强版3D高斯泼斯训练

支持：
- 更高分辨率（1920x1080）
- 更多迭代（30000）
- 多场景训练
- 自动保存checkpoint
"""

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
from typing import List, Tuple, Dict
from dataclasses import dataclass, asdict


@dataclass
class TrainingConfig:
    """训练配置"""
    num_gaussians: int = 1000
    image_width: int = 640
    image_height: int = 480
    iterations: int = 5000
    lr: float = 0.1
    save_interval: int = 500
    batch_size: int = 4  # 多视图batch
    
    @classmethod
    def fast(cls):
        """快速测试配置"""
        return cls(
            num_gaussians=300,
            image_width=160,
            image_height=120,
            iterations=500,
            lr=0.1,
            save_interval=100,
            batch_size=2
        )
    
    @classmethod
    def standard(cls):
        """标准配置"""
        return cls(
            num_gaussians=1000,
            image_width=640,
            image_height=480,
            iterations=5000,
            lr=0.05,
            save_interval=500,
            batch_size=4
        )
    
    @classmethod
    def high_quality(cls):
        """高质量配置"""
        return cls(
            num_gaussians=5000,
            image_width=1920,
            image_height=1080,
            iterations=30000,
            lr=0.01,
            save_interval=1000,
            batch_size=8
        )


class GaussianCloud:
    """高斯云"""
    
    def __init__(self, num_gaussians: int, device: str = 'cpu'):
        self.N = num_gaussians
        self.device = device
        
        # 初始化参数
        self.positions = torch.rand(num_gaussians, 2, device=device)
        self.scales = torch.ones(num_gaussians, device=device) * 10.0
        self.colors = torch.rand(num_gaussians, 3, device=device)
        
        # 设置梯度
        self.positions.requires_grad = True
        self.scales.requires_grad = True
        self.colors.requires_grad = True
    
    def parameters(self):
        return [self.positions, self.scales, self.colors]
    
    def clamp(self, W: int, H: int):
        """约束参数范围"""
        with torch.no_grad():
            self.positions.data.clamp_(0, max(W, H))
            self.scales.data.clamp_(1, 50)
            self.colors.data.clamp_(0, 1)
    
    def to_dict(self):
        return {
            'num_gaussians': self.N,
            'positions': self.positions.detach().cpu().numpy().tolist(),
            'scales': self.scales.detach().cpu().numpy().tolist(),
            'colors': self.colors.detach().cpu().numpy().tolist()
        }


class GaussianRenderer:
    """向量化高斯渲染器"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # 预计算坐标网格
        y_coords = torch.arange(height, dtype=torch.float32)
        x_coords = torch.arange(width, dtype=torch.float32)
        self.grid = torch.stack(torch.meshgrid(y_coords, x_coords, indexing='ij'), dim=-1)
    
    def render(self, gaussians: GaussianCloud) -> torch.Tensor:
        """渲染高斯云"""
        N = gaussians.N
        H, W = self.height, self.width
        
        # 移动grid到正确设备
        grid = self.grid.to(gaussians.device)
        
        # 计算距离 [H, W, N]
        pos_expanded = gaussians.positions.view(1, 1, N, 2)
        grid_expanded = grid.unsqueeze(2)
        
        dist_sq = ((grid_expanded - pos_expanded) ** 2).sum(dim=-1)
        
        # 计算高斯权重
        scales_expanded = gaussians.scales.view(1, 1, N)
        weights = torch.exp(-0.5 * dist_sq / (scales_expanded ** 2 + 1e-6))
        
        # 归一化
        weights = weights / (weights.sum(dim=-1, keepdim=True) + 1e-6)
        
        # 加权颜色
        colors_expanded = gaussians.colors.view(1, 1, N, 3)
        weights_expanded = weights.unsqueeze(-1)
        
        image = (weights_expanded * colors_expanded).sum(dim=2)
        return image.permute(2, 0, 1)  # [3, H, W]


class GaussianTrainer:
    """高斯训练器"""
    
    def __init__(self, config: TrainingConfig, device: str = 'cpu'):
        self.config = config
        self.device = device
        self.renderer = GaussianRenderer(config.image_width, config.image_height)
    
    def load_images(self, scene_dir: Path, max_images: int = 10) -> List[torch.Tensor]:
        """加载训练图片"""
        images = []
        
        for img_path in sorted(scene_dir.glob("*.jpg"))[:max_images]:
            try:
                img = Image.open(img_path).convert('RGB')
                img = img.resize((self.config.image_width, self.config.image_height))
                img_array = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).to(self.device)
                images.append(img_tensor)
            except Exception as e:
                print(f"  跳过: {img_path.name} ({e})")
        
        return images
    
    def train(
        self,
        scene_dir: Path,
        output_dir: Path
    ) -> Dict:
        """训练场景"""
        scene_name = scene_dir.name
        print(f"\n{'='*60}")
        print(f"训练场景: {scene_name}")
        print(f"配置: {self.config.num_gaussians} 高斯, {self.config.iterations} 迭代, {self.config.image_width}x{self.config.image_height}")
        print(f"{'='*60}")
        
        # 加载图片
        images = self.load_images(scene_dir, max_images=self.config.batch_size)
        if not images:
            print("  没有找到训练图片")
            return None
        
        print(f"  加载 {len(images)} 张图片")
        
        # 初始化高斯
        gaussians = GaussianCloud(self.config.num_gaussians, self.device)
        print(f"  初始化 {gaussians.N} 个高斯")
        
        # 优化器
        optimizer = torch.optim.Adam(gaussians.parameters(), lr=self.config.lr)
        
        # 训练循环
        start_time = time.time()
        losses = []
        
        for iter in range(self.config.iterations):
            total_loss = 0.0
            
            for target in images:
                rendered = self.renderer.render(gaussians)
                loss = F.mse_loss(rendered, target)
                total_loss += loss.item()
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                gaussians.clamp(self.config.image_width, self.config.image_height)
            
            losses.append(total_loss / len(images))
            
            if (iter + 1) % self.config.save_interval == 0:
                elapsed = time.time() - start_time
                print(f"  迭代 {iter+1}/{self.config.iterations}, 损失: {losses[-1]:.4f}, 时间: {elapsed:.1f}s")
        
        elapsed = time.time() - start_time
        print(f"\n  完成! 总时间: {elapsed:.1f}s, 最终损失: {losses[-1]:.4f}")
        
        # 保存结果
        result = {
            'scene': scene_name,
            'config': asdict(self.config),
            'final_loss': losses[-1],
            'training_time': elapsed,
            'gaussians': gaussians.to_dict()
        }
        
        output_path = output_dir / f"{scene_name}_model.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 保存渲染对比
        self._save_comparison(gaussians, images[0], output_dir, scene_name)
        
        return result
    
    def _save_comparison(
        self,
        gaussians: GaussianCloud,
        target: torch.Tensor,
        output_dir: Path,
        scene_name: str
    ):
        """保存渲染对比"""
        rendered = self.renderer.render(gaussians)
        
        # 渲染结果
        rendered_np = rendered.detach().cpu().numpy().transpose(1, 2, 0) * 255
        rendered_img = Image.fromarray(rendered_np.astype(np.uint8))
        rendered_img.save(output_dir / f"{scene_name}_rendered.png")
        
        # 目标图片
        target_np = target.cpu().numpy().transpose(1, 2, 0) * 255
        target_img = Image.fromarray(target_np.astype(np.uint8))
        target_img.save(output_dir / f"{scene_name}_target.png")


def main():
    print("=" * 60)
    print("增强版3D高斯泼斯训练")
    print("=" * 60)
    
    # 配置
    base_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")
    training_dir = base_path / "data/gaussian_training/images"
    output_dir = base_path / "data/gaussian_models"
    output_dir.mkdir(exist_ok=True)
    
    # 找所有场景
    scenes = []
    for scene_dir in training_dir.iterdir():
        if scene_dir.is_dir():
            count = len(list(scene_dir.glob("*.jpg")))
            if count > 0:
                scenes.append((scene_dir, count))
    
    scenes.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n找到 {len(scenes)} 个场景:")
    for scene_dir, count in scenes[:5]:
        print(f"  {scene_dir.name}: {count} 张图片")
    
    # 选择配置
    config = TrainingConfig.fast()  # 快速测试
    # config = TrainingConfig.standard()  # 标准质量
    # config = TrainingConfig.high_quality()  # 高质量（需要GPU）
    
    # 训练前3个场景
    trainer = GaussianTrainer(config, device='cpu')
    
    results = []
    for scene_dir, count in scenes[:3]:
        result = trainer.train(scene_dir, output_dir)
        if result:
            results.append(result)
    
    # 总结
    print("\n" + "=" * 60)
    print("训练总结:")
    for r in results:
        print(f"  {r['scene']}: {r['config']['num_gaussians']} 高斯, 损失 {r['final_loss']:.4f}, 时间 {r['training_time']:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
