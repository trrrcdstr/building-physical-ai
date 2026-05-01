"""
文本→4D 完整管线

整合所有模块，实现端到端的文本→4D场景生成
"""

import numpy as np
from typing import Optional, List
import json
import time

from .text_parser import TextToSceneParser, SceneDescription
from .scene_retriever import SceneRetriever, RetrievedScene
from .gaussian_splatting import GaussianSplatting3D, GaussianSplatting4D, GaussianParameters


class TextTo4DPipeline:
    """
    文本→4D完整管线
    
    示例:
        pipeline = TextTo4DPipeline()
        scene_4d = pipeline.generate("客厅里有人在沙发上喝茶")
        video = scene_4d.render_video(fps=30, duration=5.0)
    """
    
    def __init__(
        self,
        vr_knowledge_path: str = None,
        cad_database_path: str = None,
        llm_client = None
    ):
        """
        初始化管线
        
        Args:
            vr_knowledge_path: VR知识库路径
            cad_database_path: CAD数据库路径
            llm_client: LLM客户端（可选）
        """
        self.parser = TextToSceneParser(llm_client)
        self.retriever = SceneRetriever(vr_knowledge_path, cad_database_path)
    
    def generate(
        self,
        text: str,
        num_gaussians: int = 5000,
        apply_cad_constraint: bool = True
    ) -> GaussianSplatting4D:
        """
        从文本生成4D场景
        
        Args:
            text: 文本描述
            num_gaussians: 高斯数量
            apply_cad_constraint: 是否应用CAD约束
            
        Returns:
            4D高斯场景
        """
        print(f"[Pipeline] Processing: {text}")
        
        # Step 1: 文本解析
        print("[Step 1] Parsing text...")
        scene_desc = self.parser.parse(text)
        print(f"  Room: {scene_desc.room}")
        print(f"  Objects: {len(scene_desc.objects)}")
        print(f"  Actions: {len(scene_desc.actions)}")
        print(f"  Duration: {scene_desc.duration}s")
        
        # Step 2: 场景检索
        print("[Step 2] Retrieving similar scenes...")
        similar_scenes = self.retriever.retrieve(scene_desc.room, top_k=3)
        print(f"  Found {len(similar_scenes)} similar scenes")
        
        # Step 3: 初始化高斯
        print("[Step 3] Initializing gaussians...")
        gs_3d = self._initialize_gaussians(scene_desc, similar_scenes, num_gaussians)
        print(f"  Created {gs_3d.num_gaussians} gaussians")
        
        # Step 4: CAD约束
        if apply_cad_constraint:
            print("[Step 4] Applying CAD constraints...")
            cad_objects = self.retriever.get_cad_geometry()
            if cad_objects:
                gs_3d = self._apply_cad_constraints(gs_3d, cad_objects)
                print(f"  Applied {len(cad_objects)} CAD constraints")
        
        # Step 5: 添加时间维度
        print("[Step 5] Adding temporal dimension...")
        gs_4d = self._add_temporal_dimension(gs_3d, scene_desc)
        print(f"  Created 4D scene with duration {gs_4d.duration}s")
        
        print("[Pipeline] Done!")
        return gs_4d
    
    def _initialize_gaussians(
        self,
        scene_desc: SceneDescription,
        similar_scenes: List[RetrievedScene],
        num_gaussians: int
    ) -> GaussianSplatting3D:
        """初始化3D高斯"""
        gs = GaussianSplatting3D()
        
        # 基于场景描述生成基础几何
        room_generators = {
            'living_room': self._generate_living_room,
            'bedroom': self._generate_bedroom,
            'kitchen': self._generate_kitchen,
            'dining_room': self._generate_dining_room,
            'study': self._generate_study,
            'bathroom': self._generate_bathroom,
            'garden': self._generate_garden,
        }
        
        generator = room_generators.get(scene_desc.room, self._generate_generic)
        gs = generator(gs, num_gaussians)
        
        return gs
    
    def _generate_living_room(self, gs: GaussianSplatting3D, n: int) -> GaussianSplatting3D:
        """生成客厅场景"""
        # 地板
        floor_n = n // 4
        for _ in range(floor_n):
            x, z = np.random.uniform(-5, 5, 2)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, 0, z]),
                scale=np.array([0.3, 0.02, 0.3]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.8, 0.7, 0.6]),
                opacity=0.9
            ))
        
        # 墙壁
        wall_n = n // 4
        for _ in range(wall_n):
            x = np.random.uniform(-5, 5)
            y = np.random.uniform(0, 3)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, y, 5]),
                scale=np.array([0.3, 0.3, 0.02]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.9, 0.9, 0.9]),
                opacity=0.8
            ))
        
        # 沙发
        sofa_n = n // 8
        for _ in range(sofa_n):
            x = np.random.uniform(-2, 2)
            y = np.random.uniform(0.3, 0.8)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, y, 3]),
                scale=np.array([0.4, 0.2, 0.3]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.3, 0.3, 0.5]),
                opacity=0.95
            ))
        
        # 茶几
        table_n = n // 16
        for _ in range(table_n):
            x = np.random.uniform(-0.8, 0.8)
            z = np.random.uniform(0.5, 1.5)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, 0.4, z]),
                scale=np.array([0.3, 0.02, 0.2]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.6, 0.4, 0.2]),
                opacity=0.95
            ))
        
        # 电视
        gs.add_gaussian(GaussianParameters(
            position=np.array([0, 1.2, 4.8]),
            scale=np.array([1.5, 0.8, 0.05]),
            rotation=np.array([1, 0, 0, 0]),
            color=np.array([0.1, 0.1, 0.1]),
            opacity=0.95
        ))
        
        return gs
    
    def _generate_bedroom(self, gs: GaussianSplatting3D, n: int) -> GaussianSplatting3D:
        """生成卧室场景"""
        # 简化版：地板 + 床 + 衣柜
        for _ in range(n // 2):
            x, z = np.random.uniform(-4, 4, 2)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, 0, z]),
                scale=np.array([0.3, 0.02, 0.3]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.7, 0.6, 0.5]),
                opacity=0.9
            ))
        
        # 床
        for _ in range(n // 4):
            x = np.random.uniform(-1.5, 1.5)
            y = np.random.uniform(0.2, 0.6)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, y, 0]),
                scale=np.array([0.5, 0.15, 0.8]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.9, 0.9, 0.8]),
                opacity=0.95
            ))
        
        return gs
    
    def _generate_kitchen(self, gs: GaussianSplatting3D, n: int) -> GaussianSplatting3D:
        """生成厨房场景"""
        # 地板 + 橱柜 + 灶台
        for _ in range(n // 2):
            x, z = np.random.uniform(-3, 3, 2)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, 0, z]),
                scale=np.array([0.2, 0.02, 0.2]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.6, 0.6, 0.6]),
                opacity=0.9
            ))
        
        # 橱柜
        for _ in range(n // 4):
            x = np.random.uniform(-2, 2)
            y = np.random.uniform(0.5, 1.5)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, y, 2.5]),
                scale=np.array([0.3, 0.3, 0.15]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.8, 0.8, 0.7]),
                opacity=0.95
            ))
        
        return gs
    
    def _generate_dining_room(self, gs: GaussianSplatting3D, n: int) -> GaussianSplatting3D:
        """生成餐厅场景"""
        return self._generate_generic(gs, n)  # 简化
    
    def _generate_study(self, gs: GaussianSplatting3D, n: int) -> GaussianSplatting3D:
        """生成书房场景"""
        return self._generate_generic(gs, n)  # 简化
    
    def _generate_bathroom(self, gs: GaussianSplatting3D, n: int) -> GaussianSplatting3D:
        """生成卫生间场景"""
        return self._generate_generic(gs, n)  # 简化
    
    def _generate_garden(self, gs: GaussianSplatting3D, n: int) -> GaussianSplatting3D:
        """生成花园场景"""
        # 地面 + 植物
        for _ in range(n // 2):
            x, z = np.random.uniform(-10, 10, 2)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, 0, z]),
                scale=np.array([0.5, 0.02, 0.5]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.3, 0.6, 0.2]),
                opacity=0.9
            ))
        
        # 树木
        for _ in range(n // 10):
            x, z = np.random.uniform(-8, 8, 2)
            y = np.random.uniform(1, 4)
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, y, z]),
                scale=np.array([0.8, 1.5, 0.8]),
                rotation=np.array([1, 0, 0, 0]),
                color=np.array([0.2, 0.5, 0.1]),
                opacity=0.85
            ))
        
        return gs
    
    def _generate_generic(self, gs: GaussianSplatting3D, n: int) -> GaussianSplatting3D:
        """生成通用场景"""
        for _ in range(n):
            x, y, z = np.random.uniform(-5, 5, 3)
            y = abs(y)  # 确保在地面以上
            gs.add_gaussian(GaussianParameters(
                position=np.array([x, y, z]),
                scale=np.random.uniform(0.1, 0.5, 3),
                rotation=np.array([1, 0, 0, 0]),
                color=np.random.uniform(0.3, 0.9, 3),
                opacity=np.random.uniform(0.7, 0.95)
            ))
        return gs
    
    def _apply_cad_constraints(
        self,
        gs: GaussianSplatting3D,
        cad_objects: List[dict]
    ) -> GaussianSplatting3D:
        """应用CAD几何约束"""
        # 将高斯中心投影到CAD定义的位置
        for obj in cad_objects[:10]:  # 限制数量
            obj_type = obj.get('type', '')
            obj_pos = obj.get('position', [0, 0, 0])
            
            if obj_type in ['door', 'window', 'wall']:
                # 找到最近的高斯并移动
                distances = np.linalg.norm(gs.positions - np.array(obj_pos), axis=1)
                nearest_idx = np.argmin(distances)
                
                if distances[nearest_idx] < 3.0:  # 3米阈值
                    gs.positions[nearest_idx] = np.array(obj_pos)
        
        return gs
    
    def _add_temporal_dimension(
        self,
        gs_3d: GaussianSplatting3D,
        scene_desc: SceneDescription
    ) -> GaussianSplatting4D:
        """添加时间维度"""
        duration = max(scene_desc.duration, 1.0)
        
        def gaussian_at_time(t: float) -> GaussianSplatting3D:
            """t时刻的高斯"""
            # 复制基础场景
            gs_t = GaussianSplatting3D(gs_3d.num_gaussians)
            gs_t.positions = gs_3d.positions.copy()
            gs_t.scales = gs_3d.scales.copy()
            gs_t.rotations = gs_3d.rotations.copy()
            gs_t.colors = gs_3d.colors.copy()
            gs_t.opacities = gs_3d.opacities.copy()
            
            # 应用动作
            for action in scene_desc.actions:
                if action.start_time <= t <= action.end_time:
                    # 简单动画：人在沙发上轻微移动
                    if action.action == 'drink_tea':
                        # 找到"人"的高斯并添加轻微运动
                        # 简化：给所有高斯添加微小扰动
                        noise = np.random.randn(*gs_t.positions.shape) * 0.01
                        gs_t.positions += noise
            
            return gs_t
        
        gs_4d = GaussianSplatting4D(gaussian_at_time)
        gs_4d.duration = duration
        return gs_4d


# 命令行入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Text to 4D Scene Generation")
    parser.add_argument("text", help="Text description")
    parser.add_argument("--output", "-o", default="output.json", help="Output file")
    parser.add_argument("--num-gaussians", "-n", type=int, default=1000, help="Number of gaussians")
    
    args = parser.parse_args()
    
    # 初始化管线
    vr_path = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\VR_KNOWLEDGE.json"
    pipeline = TextTo4DPipeline(vr_knowledge_path=vr_path)
    
    # 生成场景
    scene_4d = pipeline.generate(args.text, num_gaussians=args.num_gaussians)
    
    # 保存
    gs_0 = scene_4d.at_time(0)
    data = gs_0.to_dict()
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved to {args.output}")
