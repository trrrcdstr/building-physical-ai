"""
简化版3D高斯泼斯训练

不依赖CUDA，使用PyTorch CPU训练
适合快速验证和原型开发
"""

import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from PIL import Image
from typing import List, Dict, Tuple
from dataclasses import dataclass
import time


@dataclass
class GaussianCloud:
    """高斯云"""
    positions: torch.Tensor  # [N, 3]
    scales: torch.Tensor     # [N, 3]
    rotations: torch.Tensor  # [N, 4] 四元数
    colors: torch.Tensor     # [N, 3] RGB
    opacities: torch.Tensor  # [N, 1]
    
    @property
    def num_gaussians(self):
        return self.positions.shape[0]
    
    def to_dict(self):
        return {
            'num_gaussians': self.num_gaussians,
            'positions': self.positions.cpu().numpy().tolist(),
            'scales': self.scales.cpu().numpy().tolist(),
            'rotations': self.rotations.cpu().numpy().tolist(),
            'colors': self.colors.cpu().numpy().tolist(),
            'opacities': self.opacities.cpu().numpy().tolist()
        }


class SimpleGaussianRenderer(nn.Module):
    """
    简化版高斯渲染器
    
    使用可微分的splatting渲染
    """
    
    def __init__(self, image_width: int = 640, image_height: int = 480):
        super().__init__()
        self.width = image_width
        self.height = image_height
        
        # 相机参数
        self.fov = 55.0
        self.focal = image_width / (2 * np.tan(np.radians(self.fov / 2)))
    
    def project_to_screen(
        self,
        positions: torch.Tensor,
        camera_pose: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        将3D点投影到2D屏幕
        
        Args:
            positions: [N, 3]
            camera_pose: [4, 4] 相机矩阵
            
        Returns:
            screen_pos: [N, 2] 屏幕坐标
            depths: [N] 深度
        """
        # 变换到相机空间
        R = camera_pose[:3, :3]
        t = camera_pose[:3, 3]
        
        cam_pos = (positions - t) @ R.T
        
        # 投影
        depths = -cam_pos[:, 2]
        
        # 避免除零
        depths = torch.clamp(depths, min=0.1)
        
        screen_x = self.focal * cam_pos[:, 0] / depths + self.width / 2
        screen_y = self.focal * cam_pos[:, 1] / depths + self.height / 2
        
        return torch.stack([screen_x, screen_y], dim=1), depths
    
    def forward(
        self,
        gaussians: GaussianCloud,
        camera_pose: torch.Tensor
    ) -> torch.Tensor:
        """
        渲染高斯云
        
        Args:
            gaussians: 高斯云
            camera_pose: [4, 4] 相机矩阵
            
        Returns:
            image: [3, H, W] 渲染图像
        """
        N = gaussians.num_gaussians
        
        # 投影到屏幕
        screen_pos, depths = self.project_to_screen(gaussians.positions, camera_pose)
        
        # 初始化图像
        image = torch.zeros(3, self.height, self.width, device=gaussians.positions.device)
        weights = torch.zeros(1, self.height, self.width, device=gaussians.positions.device)
        
        # 简化渲染：每个高斯贡献到附近的像素
        # 实际应使用CUDA加速的tile-based渲染
        
        for i in range(N):
            x, y = screen_pos[i]
            depth = depths[i]
            
            # 检查是否在图像内
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                continue
            
            # 计算屏幕空间的高斯大小
            scale = gaussians.scales[i].mean() * self.focal / depth
            screen_scale = torch.clamp(scale, min=1.0, max=20.0)
            
            # 计算影响范围
            radius = int(screen_scale * 3)
            x_int, y_int = int(x), int(y)
            
            # 遍历影响范围内的像素
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    px, py = x_int + dx, y_int + dy
                    
                    if px < 0 or px >= self.width or py < 0 or py >= self.height:
                        continue
                    
                    # 计算高斯权重
                    dist_sq = (px - x) ** 2 + (py - y) ** 2
                    weight = torch.exp(-0.5 * dist_sq / (screen_scale ** 2))
                    
                    # Alpha混合
                    alpha = gaussians.opacities[i] * weight
                    color = gaussians.colors[i]
                    
                    # 累积
                    image[:, py, px] = image[:, py, px] * (1 - alpha) + color * alpha
                    weights[:, py, px] += alpha
        
        return image


class SimpleGaussianTrainer:
    """
    简化版高斯训练器
    
    使用梯度下降优化高斯参数
    """
    
    def __init__(
        self,
        num_gaussians: int = 1000,
        image_size: Tuple[int, int] = (640, 480),
        device: str = 'cpu'
    ):
        self.num_gaussians = num_gaussians
        self.image_size = image_size
        self.device = device
        
        self.renderer = SimpleGaussianRenderer(image_size[0], image_size[1])
    
    def initialize_gaussians(self, scene_radius: float = 5.0) -> GaussianCloud:
        """初始化高斯云"""
        N = self.num_gaussians
        
        # 随机初始化
        positions = torch.randn(N, 3, device=self.device) * scene_radius
        scales = torch.ones(N, 3, device=self.device) * 0.1
        rotations = torch.zeros(N, 4, device=self.device)
        rotations[:, 0] = 1.0  # 单位四元数
        colors = torch.rand(N, 3, device=self.device)
        opacities = torch.ones(N, 1, device=self.device) * 0.5
        
        # 设置梯度
        positions.requires_grad = True
        scales.requires_grad = True
        rotations.requires_grad = True
        colors.requires_grad = True
        opacities.requires_grad = True
        
        return GaussianCloud(positions, scales, rotations, colors, opacities)
    
    def load_training_images(self, scene_dir: str) -> List[torch.Tensor]:
        """加载训练图片"""
        images = []
        
        scene_path = Path(scene_dir)
        if not scene_path.exists():
            return images
        
        for img_path in sorted(scene_path.glob("*.jpg"))[:10]:  # 最多10张
            try:
                img = Image.open(img_path).convert('RGB')
                img = img.resize(self.image_size)
                img_tensor = torch.from_numpy(np.array(img)).float() / 255.0
                img_tensor = img_tensor.permute(2, 0, 1)  # [H,W,C] -> [C,H,W]
                images.append(img_tensor)
            except Exception as e:
                print(f"  跳过: {img_path.name} ({e})")
        
        return images
    
    def generate_camera_poses(self, num_views: int) -> List[torch.Tensor]:
        """生成相机位姿"""
        poses = []
        
        for i in range(num_views):
            # 围绕场景旋转
            angle = 2 * np.pi * i / num_views
            
            # 相机位置
            cam_x = 5 * np.sin(angle)
            cam_z = 5 * np.cos(angle)
            cam_y = 2.0
            
            # 相机矩阵
            pose = torch.eye(4)
            
            # 旋转（看向原点）
            pose[0, 0] = np.cos(angle)
            pose[0, 2] = np.sin(angle)
            pose[2, 0] = -np.sin(angle)
            pose[2, 2] = np.cos(angle)
            
            # 平移
            pose[0, 3] = cam_x
            pose[1, 3] = cam_y
            pose[2, 3] = cam_z
            
            poses.append(pose)
        
        return poses
    
    def train(
        self,
        scene_dir: str,
        iterations: int = 1000,
        lr: float = 0.01,
        save_interval: int = 100
    ) -> GaussianCloud:
        """
        训练高斯云
        
        Args:
            scene_dir: 场景目录
            iterations: 迭代次数
            lr: 学习率
            save_interval: 保存间隔
            
        Returns:
            训练后的高斯云
        """
        print(f"\n训练场景: {Path(scene_dir).name}")
        
        # 加载图片
        images = self.load_training_images(scene_dir)
        if not images:
            print("  没有找到训练图片")
            return None
        
        print(f"  加载 {len(images)} 张图片")
        
        # 生成相机位姿
        poses = self.generate_camera_poses(len(images))
        
        # 初始化高斯
        gaussians = self.initialize_gaussians()
        print(f"  初始化 {gaussians.num_gaussians} 个高斯")
        
        # 优化器
        params = [
            gaussians.positions,
            gaussians.scales,
            gaussians.colors,
            gaussians.opacities
        ]
        optimizer = optim.Adam(params, lr=lr)
        
        # 训练循环
        print(f"  开始训练 ({iterations} 迭代)...")
        start_time = time.time()
        
        for iter in range(iterations):
            total_loss = 0.0
            
            for img, pose in zip(images, poses):
                # 渲染
                rendered = self.renderer(gaussians, pose)
                
                # 计算损失
                loss = torch.nn.functional.mse_loss(rendered, img)
                total_loss += loss.item()
                
                # 反向传播
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            # 打印进度
            if (iter + 1) % 100 == 0:
                elapsed = time.time() - start_time
                print(f"  迭代 {iter+1}/{iterations}, 损失: {total_loss:.4f}, 时间: {elapsed:.1f}s")
        
        elapsed = time.time() - start_time
        print(f"  完成! 总时间: {elapsed:.1f}s")
        
        return gaussians


def main():
    print("=" * 60)
    print("简化版3D高斯泼斯训练")
    print("=" * 60)
    
    # 配置
    base_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")
    training_dir = base_path / "data/gaussian_training/images"
    output_dir = base_path / "data/gaussian_models"
    output_dir.mkdir(exist_ok=True)
    
    # 找到图片最多的场景
    scenes = []
    for scene_dir in training_dir.iterdir():
        if scene_dir.is_dir():
            count = len(list(scene_dir.glob("*.jpg")))
            scenes.append((scene_dir, count))
    
    scenes.sort(key=lambda x: x[1], reverse=True)
    
    # 训练前3个场景
    trainer = SimpleGaussianTrainer(
        num_gaussians=500,
        image_size=(320, 240),  # 小分辨率快速训练
        device='cpu'
    )
    
    results = []
    
    for scene_dir, count in scenes[:3]:
        gaussians = trainer.train(
            str(scene_dir),
            iterations=500,
            lr=0.01
        )
        
        if gaussians:
            # 保存模型
            model_path = output_dir / f"{scene_dir.name}.json"
            with open(model_path, 'w', encoding='utf-8') as f:
                json.dump(gaussians.to_dict(), f)
            
            results.append({
                'scene': scene_dir.name,
                'num_gaussians': gaussians.num_gaussians,
                'model_path': str(model_path)
            })
    
    # 保存结果
    print("\n" + "=" * 60)
    print("训练结果:")
    for r in results:
        print(f"  {r['scene']}: {r['num_gaussians']} 高斯 -> {r['model_path']}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
