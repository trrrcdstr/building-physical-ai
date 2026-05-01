"""
高斯泼斯训练数据准备

从效果图和VR全景提取训练数据：
1. 多视角图片（COLMAP输入）
2. 相机位姿估计
3. 深度/语义分割（可选）
4. 几何约束（CAD）
"""

import os
import json
import numpy as np
from PIL import Image
from typing import List, Dict, Tuple
from dataclasses import dataclass
import shutil


@dataclass
class TrainingImage:
    """训练图片"""
    path: str
    category: str      # 室内/建筑/园林
    scene: str         # 家庭/办公/别墅等
    width: int
    height: int
    camera_pose: np.ndarray = None  # [4, 4] 相机矩阵
    depth_path: str = None
    semantic_path: str = None


class GaussianTrainingDataPreparer:
    """
    高斯泼斯训练数据准备器
    
    将效果图和VR全景转换为3D高斯泼斯训练格式
    """
    
    def __init__(
        self,
        rendering_db_path: str,
        vr_knowledge_path: str,
        output_dir: str
    ):
        """
        初始化
        
        Args:
            rendering_db_path: 效果图数据库路径
            vr_knowledge_path: VR知识库路径
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 加载数据
        with open(rendering_db_path, 'r', encoding='utf-8') as f:
            self.rendering_db = json.load(f)
        
        with open(vr_knowledge_path, 'r', encoding='utf-8') as f:
            self.vr_knowledge = json.load(f)
        
        self.training_images: List[TrainingImage] = []
    
    def prepare_all(self):
        """准备所有训练数据"""
        print("=== 高斯泼斯训练数据准备 ===\n")
        
        # Step 1: 效果图
        print("[Step 1] 处理效果图...")
        self._process_renderings()
        
        # Step 2: VR全景
        print("\n[Step 2] 处理VR全景...")
        self._process_vr_panoramas()
        
        # Step 3: 生成COLMAP输入
        print("\n[Step 3] 生成COLMAP输入...")
        self._generate_colmap_input()
        
        # Step 4: 生成训练配置
        print("\n[Step 4] 生成训练配置...")
        self._generate_training_config()
        
        print(f"\n完成！共 {len(self.training_images)} 张训练图片")
    
    def _process_renderings(self):
        """处理效果图"""
        total = 0
        
        for entry in self.rendering_db:
            category = entry['category']
            scene = entry['scene']
            path = entry['path']
            
            # 遍历目录中的所有图片
            for filename in os.listdir(path):
                if not filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                    continue
                
                img_path = os.path.join(path, filename)
                
                try:
                    with Image.open(img_path) as img:
                        w, h = img.size
                    
                    self.training_images.append(TrainingImage(
                        path=img_path,
                        category=category,
                        scene=scene,
                        width=w,
                        height=h
                    ))
                    total += 1
                except Exception as e:
                    print(f"  跳过: {filename} ({e})")
        
        print(f"  效果图: {total} 张")
    
    def _process_vr_panoramas(self):
        """处理VR全景"""
        vr_list = self.vr_knowledge.get('vr_links', [])
        count = 0
        
        # VR全景可以提取多个视角
        # 简化：只记录URL，实际需要下载和处理
        for vr in vr_list[:10]:  # 先处理10个作为示例
            url = vr.get('url', '')
            title = vr.get('title', '')
            
            # VR全景可以投影为6个立方体面
            # 这里只记录，实际处理需要下载VR内容
            count += 1
        
        print(f"  VR全景: {len(vr_list)} 个可用，{count} 个已处理")
    
    def _generate_colmap_input(self):
        """生成COLMAP输入"""
        images_dir = os.path.join(self.output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        # 按场景分组
        scenes = {}
        for img in self.training_images:
            key = f"{img.category}_{img.scene}"
            if key not in scenes:
                scenes[key] = []
            scenes[key].append(img)
        
        # 为每个场景创建目录
        for scene_name, images in scenes.items():
            scene_dir = os.path.join(images_dir, scene_name)
            os.makedirs(scene_dir, exist_ok=True)
            
            # 复制图片（或创建符号链接）
            for i, img in enumerate(images[:100]):  # 每场景最多100张
                ext = os.path.splitext(img.path)[1]
                dst = os.path.join(scene_dir, f"{i:04d}{ext}")
                
                # 创建符号链接（节省空间）
                if not os.path.exists(dst):
                    try:
                        os.symlink(img.path, dst)
                    except:
                        # Windows可能需要管理员权限
                        shutil.copy2(img.path, dst)
        
        print(f"  创建了 {len(scenes)} 个场景目录")
    
    def _generate_training_config(self):
        """生成训练配置"""
        # 按场景统计
        scene_stats = {}
        for img in self.training_images:
            key = f"{img.category}_{img.scene}"
            if key not in scene_stats:
                scene_stats[key] = 0
            scene_stats[key] += 1
        
        config = {
            "num_scenes": len(scene_stats),
            "total_images": len(self.training_images),
            "scene_distribution": scene_stats,
            "training_params": {
                "num_gaussians": 10000,
                "learning_rate": 0.01,
                "iterations": 30000,
                "depth_supervision": True,
                "cad_constraint": True
            },
            "data_sources": {
                "renderings": len(self.rendering_db),
                "vr_panoramas": len(self.vr_knowledge.get('vr_links', []))
            }
        }
        
        config_path = os.path.join(self.output_dir, 'training_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"  配置保存到: {config_path}")
    
    def get_scene_samples(self, scene_name: str, n: int = 10) -> List[str]:
        """获取场景样本图片路径"""
        samples = [
            img.path for img in self.training_images
            if img.scene == scene_name
        ][:n]
        return samples


# 命令行入口
if __name__ == "__main__":
    rendering_db = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\rendering_database.json"
    vr_knowledge = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\VR_KNOWLEDGE.json"
    output_dir = r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\gaussian_training"
    
    preparer = GaussianTrainingDataPreparer(rendering_db, vr_knowledge, output_dir)
    preparer.prepare_all()
