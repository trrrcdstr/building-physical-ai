"""
CAD几何约束模块

从CAD施工图提取几何约束，用于精修高斯泼斯
"""

import numpy as np
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class CADObject:
    """CAD几何对象"""
    object_id: str
    object_type: str       # door, window, wall, floor, etc.
    position: np.ndarray   # [3] 中心位置
    normal: np.ndarray     # [3] 法向量
    dimensions: np.ndarray # [3] 尺寸 (长宽高)
    layer: str             # CAD图层


class CADGeometryConstraint:
    """
    CAD几何约束
    
    从CAD施工图提取门/窗/墙等几何信息，约束高斯泼斯位置
    """
    
    def __init__(self, cad_data: Dict = None):
        """
        初始化约束
        
        Args:
            cad_data: CAD数据库字典
        """
        self.cad_data = cad_data or {}
        self.building_objects: List[CADObject] = []
        
        if cad_data:
            self._parse_cad_data()
    
    def _parse_cad_data(self):
        """解析CAD数据"""
        objects = self.cad_data.get('building_objects', [])
        
        for obj in objects:
            self.building_objects.append(CADObject(
                object_id=obj.get('id', ''),
                object_type=obj.get('type', 'unknown'),
                position=np.array(obj.get('position', [0, 0, 0])),
                normal=np.array(obj.get('normal', [0, 1, 0])),
                dimensions=np.array(obj.get('dimensions', [1, 1, 1])),
                layer=obj.get('layer', '')
            ))
    
    def get_constraints_for_type(self, obj_type: str) -> List[CADObject]:
        """获取特定类型的约束"""
        return [obj for obj in self.building_objects if obj.object_type == obj_type]
    
    def project_to_constraint(
        self,
        position: np.ndarray,
        constraint: CADObject
    ) -> np.ndarray:
        """
        将位置投影到约束平面
        
        Args:
            position: 原始位置 [3]
            constraint: CAD约束对象
            
        Returns:
            投影后的位置 [3]
        """
        # 计算到平面的距离
        d = np.dot(position - constraint.position, constraint.normal)
        # 投影
        return position - d * constraint.normal
    
    def apply_to_gaussians(
        self,
        positions: np.ndarray,
        threshold: float = 2.0
    ) -> np.ndarray:
        """
        将约束应用到高斯位置
        
        Args:
            positions: 高斯位置 [N, 3]
            threshold: 距离阈值（米）
            
        Returns:
            约束后的位置 [N, 3]
        """
        result = positions.copy()
        
        for obj in self.building_objects:
            # 计算每个高斯到约束对象的距离
            distances = np.linalg.norm(result - obj.position, axis=1)
            
            # 对距离阈值内的高斯应用约束
            mask = distances < threshold
            if np.any(mask):
                for i in np.where(mask)[0]:
                    result[i] = self.project_to_constraint(result[i], obj)
        
        return result
