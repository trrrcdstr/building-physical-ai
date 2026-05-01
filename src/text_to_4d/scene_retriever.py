"""
场景检索器

从VR/CAD数据库检索相似场景，用于初始化高斯泼斯
"""

import json
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
import os


@dataclass
class RetrievedScene:
    """检索到的场景"""
    vr_id: int
    url: str
    platform: str
    room_type: str
    similarity: float
    gaussian_params: Optional[dict] = None


class SceneRetriever:
    """
    场景检索器
    
    从VR知识库和CAD数据库检索相似场景
    """
    
    def __init__(
        self,
        vr_knowledge_path: str = None,
        cad_database_path: str = None
    ):
        """
        初始化检索器
        
        Args:
            vr_knowledge_path: VR知识库路径
            cad_database_path: CAD数据库路径
        """
        self.vr_knowledge_path = vr_knowledge_path
        self.cad_database_path = cad_database_path
        
        # 加载数据
        self.vr_data = self._load_vr_knowledge()
        self.cad_data = self._load_cad_database()
        
        # 构建索引
        self.room_index = self._build_room_index()
    
    def _load_vr_knowledge(self) -> dict:
        """加载VR知识库"""
        if self.vr_knowledge_path and os.path.exists(self.vr_knowledge_path):
            with open(self.vr_knowledge_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'raw_vr': []}
    
    def _load_cad_database(self) -> dict:
        """加载CAD数据库"""
        if self.cad_database_path and os.path.exists(self.cad_database_path):
            with open(self.cad_database_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _build_room_index(self) -> Dict[str, List[int]]:
        """构建房间类型索引"""
        index = {}
        for vr in self.vr_data.get('raw_vr', []):
            rooms = vr.get('rooms', [])
            for room in rooms:
                if room not in index:
                    index[room] = []
                index[room].append(vr.get('index', 0))
        return index
    
    def retrieve(
        self,
        room_type: str,
        style: str = "modern",
        top_k: int = 5
    ) -> List[RetrievedScene]:
        """
        检索相似场景
        
        Args:
            room_type: 房间类型（living_room, bedroom等）
            style: 风格（modern, classic等）
            top_k: 返回数量
            
        Returns:
            检索到的场景列表
        """
        # 中文房间名映射
        room_cn_map = {
            'living_room': '客厅',
            'bedroom': '卧室',
            'kitchen': '厨房',
            'dining_room': '餐厅',
            'study': '书房',
            'bathroom': '卫生间',
        }
        
        room_cn = room_cn_map.get(room_type, room_type)
        
        # 从索引检索
        vr_ids = self.room_index.get(room_cn, [])
        
        # 获取VR详情
        results = []
        for vr in self.vr_data.get('raw_vr', []):
            if vr.get('index') in vr_ids[:top_k * 2]:
                results.append(RetrievedScene(
                    vr_id=vr.get('index', 0),
                    url=vr.get('url', ''),
                    platform=vr.get('platform', ''),
                    room_type=room_cn,
                    similarity=1.0  # 简单匹配，相似度为1
                ))
        
        # 按相似度排序
        results.sort(key=lambda x: x.similarity, reverse=True)
        
        return results[:top_k]
    
    def retrieve_by_text(
        self,
        text: str,
        top_k: int = 5
    ) -> List[RetrievedScene]:
        """
        通过文本检索场景
        
        Args:
            text: 文本描述
            top_k: 返回数量
            
        Returns:
            检索到的场景列表
        """
        # 提取房间类型
        room_keywords = {
            '客厅': 'living_room',
            '卧室': 'bedroom',
            '厨房': 'kitchen',
            '餐厅': 'dining_room',
            '书房': 'study',
            '卫生间': 'bathroom',
            '花园': 'garden',
            '园林': 'landscape',
        }
        
        room_type = 'unknown'
        for kw, rt in room_keywords.items():
            if kw in text:
                room_type = rt
                break
        
        return self.retrieve(room_type, top_k=top_k)
    
    def get_cad_geometry(self, project_name: str = None) -> List[dict]:
        """
        获取CAD几何约束
        
        Args:
            project_name: 项目名称（可选）
            
        Returns:
            CAD几何对象列表
        """
        if not self.cad_data:
            return []
        
        # 返回建筑对象
        building_objects = self.cad_data.get('building_objects', [])
        
        if project_name:
            building_objects = [
                obj for obj in building_objects
                if obj.get('project') == project_name
            ]
        
        return building_objects
    
    def initialize_gaussians_from_vr(
        self,
        vr: RetrievedScene,
        num_gaussians: int = 1000
    ) -> dict:
        """
        从VR初始化高斯参数
        
        Args:
            vr: 检索到的VR场景
            num_gaussians: 高斯数量
            
        Returns:
            高斯参数字典
        """
        # 简化版：生成随机高斯
        # 实际应从VR全景提取
        
        positions = np.random.randn(num_gaussians, 3).astype(np.float32) * 5
        scales = np.random.rand(num_gaussians, 3).astype(np.float32) * 0.5 + 0.1
        rotations = np.random.rand(num_gaussians, 4).astype(np.float32)
        rotations = rotations / np.linalg.norm(rotations, axis=1, keepdims=True)
        colors = np.random.rand(num_gaussians, 3).astype(np.float32)
        opacities = np.random.rand(num_gaussians, 1).astype(np.float32) * 0.5 + 0.5
        
        return {
            'positions': positions.tolist(),
            'scales': scales.tolist(),
            'rotations': rotations.tolist(),
            'colors': colors.tolist(),
            'opacities': opacities.tolist(),
        }


# 测试
if __name__ == "__main__":
    # 初始化检索器
    vr_path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\VR_KNOWLEDGE.json"
    retriever = SceneRetriever(vr_knowledge_path=vr_path)
    
    # 检索客厅场景
    scenes = retriever.retrieve('living_room', top_k=5)
    print(f"Found {len(scenes)} living room scenes:")
    for s in scenes:
        print(f"  - VR#{s.vr_id} from {s.platform}: {s.url[:50]}...")
    
    # 文本检索
    scenes = retriever.retrieve_by_text("客厅里有人在沙发上喝茶")
    print(f"\nText search found {len(scenes)} scenes")
