"""
实时渲染器

使用CUDA加速的高斯泼斯渲染器
"""

import numpy as np
from typing import Optional
import time


class RealtimeRenderer:
    """
    实时渲染器
    
    将3D高斯泼斯渲染为2D图像
    """
    
    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        use_cuda: bool = True
    ):
        """
        初始化渲染器
        
        Args:
            width: 图像宽度
            height: 图像高度
            use_cuda: 是否使用CUDA加速
        """
        self.width = width
        self.height = height
        self.use_cuda = use_cuda
        
        # 相机参数
        self.fov = 55.0
        self.near = 0.1
        self.far = 1000.0
    
    def render(
        self,
        positions: np.ndarray,
        colors: np.ndarray,
        opacities: np.ndarray,
        scales: np.ndarray,
        camera_position: np.ndarray,
        camera_target: np.ndarray,
        camera_up: np.ndarray = None
    ) -> np.ndarray:
        """
        渲染高斯泼斯
        
        Args:
            positions: 高斯位置 [N, 3]
            colors: 高斯颜色 [N, 3]
            opacities: 高斯不透明度 [N, 1]
            scales: 高斯尺度 [N, 3]
            camera_position: 相机位置 [3]
            camera_target: 相机朝向 [3]
            camera_up: 相机上方向 [3]
            
        Returns:
            渲染图像 [H, W, 3]
        """
        if camera_up is None:
            camera_up = np.array([0, 1, 0])
        
        # 简化版：使用CPU渲染
        # 实际应使用CUDA实现
        image = np.zeros((self.height, self.width, 3), dtype=np.float32)
        
        # 构建相机矩阵
        view_matrix = self._build_view_matrix(camera_position, camera_target, camera_up)
        proj_matrix = self._build_projection_matrix()
        
        # 投影高斯到2D
        num_gaussians = len(positions)
        
        for i in range(num_gaussians):
            # 变换到相机空间
            pos_cam = view_matrix @ np.append(positions[i], 1.0)
            
            # 跳过相机后面的点
            if pos_cam[2] >= 0:
                continue
            
            # 投影到屏幕
            pos_proj = proj_matrix @ pos_cam
            pos_proj = pos_proj / pos_proj[3]
            
            # 转换到像素坐标
            x = int((pos_proj[0] + 1) * 0.5 * self.width)
            y = int((1 - pos_proj[1]) * 0.5 * self.height)
            
            # 检查是否在图像范围内
            if 0 <= x < self.width and 0 <= y < self.height:
                # 简单alpha混合
                alpha = opacities[i, 0]
                image[y, x] = image[y, x] * (1 - alpha) + colors[i] * alpha
        
        return (image * 255).astype(np.uint8)
    
    def _build_view_matrix(
        self,
        position: np.ndarray,
        target: np.ndarray,
        up: np.ndarray
    ) -> np.ndarray:
        """构建视图矩阵"""
        forward = target - position
        forward = forward / np.linalg.norm(forward)
        
        right = np.cross(forward, up)
        right = right / np.linalg.norm(right)
        
        up_new = np.cross(right, forward)
        
        view = np.eye(4)
        view[0, :3] = right
        view[1, :3] = up_new
        view[2, :3] = -forward
        view[:3, 3] = -np.array([
            np.dot(right, position),
            np.dot(up_new, position),
            np.dot(-forward, position)
        ])
        
        return view
    
    def _build_projection_matrix(self) -> np.ndarray:
        """构建投影矩阵"""
        aspect = self.width / self.height
        fov_rad = np.radians(self.fov)
        tan_half_fov = np.tan(fov_rad / 2)
        
        proj = np.zeros((4, 4))
        proj[0, 0] = 1 / (aspect * tan_half_fov)
        proj[1, 1] = 1 / tan_half_fov
        proj[2, 2] = -(self.far + self.near) / (self.far - self.near)
        proj[2, 3] = -2 * self.far * self.near / (self.far - self.near)
        proj[3, 2] = -1
        
        return proj
    
    def render_video(
        self,
        frames: list,
        output_path: str,
        fps: int = 30
    ):
        """
        渲染视频
        
        Args:
            frames: 帧列表
            output_path: 输出路径
            fps: 帧率
        """
        # 简化版：保存为numpy文件
        # 实际应使用OpenCV或ffmpeg
        np.save(output_path, np.array(frames))
        print(f"Saved {len(frames)} frames to {output_path}")
