"""
3D/4D 高斯泼斯表示与渲染

核心概念:
- 3D高斯: 由中心位置μ、协方差Σ、颜色、不透明度定义
- 4D高斯: 时变高斯，参数随时间变化
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Callable, Optional
import json


@dataclass
class GaussianParameters:
    """单个高斯的参数"""
    position: np.ndarray      # μ: [3] 中心位置
    scale: np.ndarray         # s: [3] 缩放（协方差特征值）
    rotation: np.ndarray      # q: [4] 四元数旋转
    color: np.ndarray         # c: [3] RGB 或 [K, 3] 球谐系数
    opacity: float            # α: 不透明度 [0, 1]
    
    def get_covariance(self) -> np.ndarray:
        """计算协方差矩阵 Σ = R * S * S^T * R^T"""
        # 四元数转旋转矩阵
        R = self._quaternion_to_matrix(self.rotation)
        # 缩放矩阵
        S = np.diag(self.scale)
        # 协方差
        return R @ S @ S @ R.T
    
    @staticmethod
    def _quaternion_to_matrix(q: np.ndarray) -> np.ndarray:
        """四元数转旋转矩阵"""
        w, x, y, z = q
        return np.array([
            [1 - 2*(y*y + z*z), 2*(x*y - w*z), 2*(x*z + w*y)],
            [2*(x*y + w*z), 1 - 2*(x*x + z*z), 2*(y*z - w*x)],
            [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x*x + y*y)]
        ])


class GaussianSplatting3D:
    """
    3D高斯泼斯场景表示
    
    每个场景由N个3D高斯组成，可从任意视角渲染
    """
    
    def __init__(self, num_gaussians: int = 0):
        """
        初始化3D高斯场景
        
        Args:
            num_gaussians: 高斯数量
        """
        self.num_gaussians = num_gaussians
        self.gaussians: List[GaussianParameters] = []
        
        # 批量参数（用于GPU渲染）
        self.positions = np.zeros((num_gaussians, 3), dtype=np.float32)
        self.scales = np.zeros((num_gaussians, 3), dtype=np.float32)
        self.rotations = np.zeros((num_gaussians, 4), dtype=np.float32)
        self.colors = np.zeros((num_gaussians, 3), dtype=np.float32)
        self.opacities = np.zeros((num_gaussians, 1), dtype=np.float32)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GaussianSplatting3D':
        """从字典加载"""
        gs = cls(len(data.get('positions', [])))
        if 'positions' in data:
            gs.positions = np.array(data['positions'], dtype=np.float32)
        if 'scales' in data:
            gs.scales = np.array(data['scales'], dtype=np.float32)
        if 'rotations' in data:
            gs.rotations = np.array(data['rotations'], dtype=np.float32)
        if 'colors' in data:
            gs.colors = np.array(data['colors'], dtype=np.float32)
        if 'opacities' in data:
            gs.opacities = np.array(data['opacities'], dtype=np.float32)
        return gs
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'num_gaussians': self.num_gaussians,
            'positions': self.positions.tolist(),
            'scales': self.scales.tolist(),
            'rotations': self.rotations.tolist(),
            'colors': self.colors.tolist(),
            'opacities': self.opacities.tolist(),
        }
    
    def add_gaussian(self, params: GaussianParameters):
        """添加单个高斯"""
        self.gaussians.append(params)
        self.num_gaussians = len(self.gaussians)
        
        # 更新批量数组
        self.positions = np.vstack([self.positions, params.position]) if len(self.positions) > 0 else params.position.reshape(1, -1)
        self.scales = np.vstack([self.scales, params.scale]) if len(self.scales) > 0 else params.scale.reshape(1, -1)
        self.rotations = np.vstack([self.rotations, params.rotation]) if len(self.rotations) > 0 else params.rotation.reshape(1, -1)
        self.colors = np.vstack([self.colors, params.color]) if len(self.colors) > 0 else params.color.reshape(1, -1)
        self.opacities = np.vstack([self.opacities, [params.opacity]]) if len(self.opacities) > 0 else np.array([[params.opacity]])
    
    def render(
        self,
        camera_position: np.ndarray,
        camera_target: np.ndarray,
        fov: float = 55.0,
        width: int = 1920,
        height: int = 1080
    ) -> np.ndarray:
        """
        从指定视角渲染场景
        
        Args:
            camera_position: 相机位置 [3]
            camera_target: 相机朝向 [3]
            fov: 视场角（度）
            width: 图像宽度
            height: 图像高度
            
        Returns:
            rendered_image: [H, W, 3] RGB图像
        """
        # 简化版：返回占位图像
        # 实际实现需要CUDA高斯泼水渲染器
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # TODO: 实现高斯泼水渲染
        # 1. 将3D高斯投影到2D
        # 2. 按深度排序
        # 3. Alpha混合渲染
        
        return image
    
    def apply_cad_constraint(self, constraint):
        """
        应用CAD几何约束
        
        Args:
            constraint: CADGeometryConstraint实例
        """
        # 将高斯中心投影到CAD定义的平面上
        for obj in constraint.building_objects:
            if obj['type'] in ['door', 'window', 'wall']:
                # 找到最近的高斯
                distances = np.linalg.norm(self.positions - np.array(obj['position']), axis=1)
                nearest_idx = np.argmin(distances)
                
                # 投影到平面
                if distances[nearest_idx] < 2.0:  # 2米阈值
                    self.positions[nearest_idx] = self._project_to_plane(
                        self.positions[nearest_idx],
                        obj['plane_normal'],
                        obj['plane_point']
                    )
    
    @staticmethod
    def _project_to_plane(point, normal, plane_point):
        """将点投影到平面"""
        d = np.dot(point - plane_point, normal)
        return point - d * normal


class GaussianSplatting4D:
    """
    4D高斯泼斯场景表示（带时间维度）
    
    高斯参数随时间变化，支持动态场景渲染
    """
    
    def __init__(self, gaussian_func: Callable[[float], GaussianSplatting3D]):
        """
        初始化4D高斯场景
        
        Args:
            gaussian_func: 时变高斯函数 t -> GaussianSplatting3D
        """
        self.gaussian_func = gaussian_func
        self.duration = 10.0  # 默认10秒
    
    def at_time(self, t: float) -> GaussianSplatting3D:
        """获取t时刻的3D高斯"""
        return self.gaussian_func(t)
    
    def render_frame(
        self,
        t: float,
        camera_position: np.ndarray,
        camera_target: np.ndarray,
        **kwargs
    ) -> np.ndarray:
        """渲染t时刻的帧"""
        gs_3d = self.at_time(t)
        return gs_3d.render(camera_position, camera_target, **kwargs)
    
    def render_video(
        self,
        camera_trajectory: Callable[[float], tuple],
        fps: int = 30,
        duration: Optional[float] = None
    ) -> List[np.ndarray]:
        """
        渲染完整视频
        
        Args:
            camera_trajectory: t -> (position, target) 相机轨迹
            fps: 帧率
            duration: 时长（秒）
            
        Returns:
            frames: 帧列表
        """
        if duration is None:
            duration = self.duration
        
        num_frames = int(duration * fps)
        frames = []
        
        for i in range(num_frames):
            t = i / fps
            cam_pos, cam_target = camera_trajectory(t)
            frame = self.render_frame(t, cam_pos, cam_target)
            frames.append(frame)
        
        return frames


def create_simple_scene() -> GaussianSplatting3D:
    """
    创建简单测试场景
    
    Returns:
        一个包含基本家具的客厅场景
    """
    gs = GaussianSplatting3D()
    
    # 地板（大量小高斯）
    for x in np.linspace(-5, 5, 50):
        for y in np.linspace(-5, 5, 50):
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, 0, y]),
                scale=np.array([0.2, 0.01, 0.2]),
                rotation=np.array([1, 0, 0, 0]),  # 无旋转
                color=np.array([0.8, 0.7, 0.6]),  # 木地板色
                opacity=0.9
            ))
    
    # 沙发（简化为几个高斯）
    for x in np.linspace(-2, 2, 10):
        gs.add_gaussian(GaussianParameters(
            position=np.array([x, 0.5, 3]),
            scale=np.array([0.5, 0.3, 0.3]),
            rotation=np.array([1, 0, 0, 0]),
            color=np.array([0.3, 0.3, 0.5]),  # 蓝色沙发
            opacity=0.95
        ))
    
    # 茶几
    gs.add_gaussian(GaussianParameters(
        position=np.array([0, 0.4, 1]),
        scale=np.array([1.0, 0.05, 0.6]),
        rotation=np.array([1, 0, 0, 0]),
        color=np.array([0.6, 0.4, 0.2]),  # 木色
        opacity=0.95
    ))
    
    return gs


# 测试
if __name__ == "__main__":
    # 创建测试场景
    scene = create_simple_scene()
    print(f"Created scene with {scene.num_gaussians} gaussians")
    
    # 保存
    data = scene.to_dict()
    print(f"Scene data size: {len(json.dumps(data))} bytes")
    
    # 渲染测试
    image = scene.render(
        camera_position=np.array([0, 3, -5]),
        camera_target=np.array([0, 0.5, 0])
    )
    print(f"Rendered image shape: {image.shape}")
