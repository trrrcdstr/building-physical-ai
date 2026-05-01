"""
COLMAP相机位姿估计准备

为3D高斯泼斯训练准备相机参数
COLMAP需要多视角图片和相机内参
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import numpy as np
from pathlib import Path
from PIL import Image
import subprocess


def prepare_colmap_data(scene_dir: Path, output_dir: Path):
    """
    准备COLMAP输入数据
    
    COLMAP需要:
    - images/ 目录包含所有图片
    - 相机内参（可自动估计）
    """
    scene_name = scene_dir.name
    colmap_dir = output_dir / scene_name / "colmap"
    images_dir = colmap_dir / "images"
    
    images_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n准备COLMAP数据: {scene_name}")
    
    # 复制图片到COLMAP目录
    image_files = list(scene_dir.glob("*.jpg"))
    
    for i, img_path in enumerate(image_files):
        # 重命名为连续编号（COLMAP推荐）
        target_path = images_dir / f"{i:06d}.jpg"
        
        # 读取并保存（可选：调整大小）
        img = Image.open(img_path)
        img.save(target_path)
    
    print(f"  复制 {len(image_files)} 张图片到 {images_dir}")
    
    # 创建相机配置
    # 假设所有图片使用相同相机
    sample_img = Image.open(image_files[0])
    width, height = sample_img.size
    
    # 估计焦距（假设FOV约55度）
    fov = 55.0
    focal = width / (2 * np.tan(np.radians(fov / 2)))
    
    camera_config = {
        'camera_model': 'PINHOLE',  # COLMAP相机模型
        'width': width,
        'height': height,
        'focal_length': focal,
        'cx': width / 2,  # 主点x
        'cy': height / 2,  # 主点y
        'num_images': len(image_files)
    }
    
    config_path = colmap_dir / "camera_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(camera_config, f, indent=2)
    
    print(f"  相机配置: {width}x{height}, 焦距={focal:.1f}")
    
    return colmap_dir, camera_config


def create_colmap_script(colmap_dir: Path, camera_config: dict):
    """创建COLMAP运行脚本"""
    
    script_content = f"""# COLMAP相机估计脚本
# 需要先安装COLMAP: https://colmap.github.io/

# 1. 特征提取
colmap feature_extractor \\
    --database_path {colmap_dir}/database.db \\
    --image_path {colmap_dir}/images \\
    --ImageReader.camera_model PINHOLE \\
    --ImageReader.single_camera 1

# 2. 特征匹配
colmap exhaustive_matcher \\
    --database_path {colmap_dir}/database.db

# 3. 稀疏重建（SfM）
colmap mapper \\
    --database_path {colmap_dir}/database.db \\
    --image_path {colmap_dir}/images \\
    --output_path {colmap_dir}/sparse

# 4. 导出相机位姿
colmap model_converter \\
    --input_path {colmap_dir}/sparse/0 \\
    --output_path {colmap_dir}/cameras.txt \\
    --output_type TXT

# 相机参数:
# - 模型: {camera_config['camera_model']}
# - 分辨率: {camera_config['width']}x{camera_config['height']}
# - 焦距: {camera_config['focal_length']:.1f}
# - 图片数: {camera_config['num_images']}
"""
    
    script_path = colmap_dir / "run_colmap.sh"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Windows批处理版本
    bat_content = f"""@echo off
REM COLMAP相机估计脚本 (Windows)

REM 1. 特征提取
colmap feature_extractor ^
    --database_path {colmap_dir}/database.db ^
    --image_path {colmap_dir}/images ^
    --ImageReader.camera_model PINHOLE ^
    --ImageReader.single_camera 1

REM 2. 特征匹配
colmap exhaustive_matcher ^
    --database_path {colmap_dir}/database.db

REM 3. 稀疏重建
colmap mapper ^
    --database_path {colmap_dir}/database.db ^
    --image_path {colmap_dir}/images ^
    --output_path {colmap_dir}/sparse

REM 4. 导出相机位姿
colmap model_converter ^
    --input_path {colmap_dir}/sparse/0 ^
    --output_path {colmap_dir}/cameras.txt ^
    --output_type TXT
"""
    
    bat_path = colmap_dir / "run_colmap.bat"
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print(f"  创建脚本: {script_path}")
    print(f"  创建脚本: {bat_path}")


def estimate_poses_simple(scene_dir: Path, output_dir: Path):
    """
    简化版相机位姿估计
    
    假设相机围绕场景中心旋转
    适用于VR全景图提取的多视角
    """
    scene_name = scene_dir.name
    
    image_files = list(scene_dir.glob("*.jpg"))
    num_images = len(image_files)
    
    print(f"\n简化相机估计: {scene_name} ({num_images} 张)")
    
    # 假设相机参数
    sample_img = Image.open(image_files[0])
    width, height = sample_img.size
    focal = width / (2 * np.tan(np.radians(55 / 2)))
    
    poses = []
    
    for i in range(num_images):
        # 均匀分布在球面上
        theta = 2 * np.pi * i / num_images  # 水平角度
        phi = np.pi / 2  # 固定在赤道面
        
        # 相机位置（半径5米）
        radius = 5.0
        cam_x = radius * np.sin(phi) * np.cos(theta)
        cam_y = radius * np.cos(phi)
        cam_z = radius * np.sin(phi) * np.sin(theta)
        
        # 旋转矩阵（看向原点）
        # 简化：只考虑水平旋转
        R = np.array([
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)]
        ])
        
        # 4x4变换矩阵
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = [cam_x, cam_y, cam_z]
        
        poses.append({
            'image_id': i,
            'image_name': image_files[i].name,
            'camera_position': [cam_x, cam_y, cam_z],
            'rotation_matrix': R.tolist(),
            'transform_matrix': T.tolist()
        })
    
    # 保存
    result = {
        'scene': scene_name,
        'camera_model': 'PINHOLE',
        'width': width,
        'height': height,
        'focal_length': focal,
        'num_images': num_images,
        'poses': poses
    }
    
    output_path = output_dir / f"{scene_name}_poses.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  保存到: {output_path}")
    
    return result


def main():
    print("=" * 60)
    print("COLMAP相机位姿估计准备")
    print("=" * 60)
    
    base_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")
    training_dir = base_path / "data/gaussian_training/images"
    output_dir = base_path / "data/camera_poses"
    output_dir.mkdir(exist_ok=True)
    
    # 找场景
    scenes = []
    for scene_dir in training_dir.iterdir():
        if scene_dir.is_dir():
            count = len(list(scene_dir.glob("*.jpg")))
            if count > 0:
                scenes.append((scene_dir, count))
    
    scenes.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n找到 {len(scenes)} 个场景")
    
    # 为每个场景准备数据
    for scene_dir, count in scenes[:3]:
        # 简化版相机估计
        estimate_poses_simple(scene_dir, output_dir)
        
        # COLMAP准备（可选）
        # colmap_dir, camera_config = prepare_colmap_data(scene_dir, output_dir)
        # create_colmap_script(colmap_dir, camera_config)
    
    print("\n" + "=" * 60)
    print("完成!")
    print("\n下一步:")
    print("1. 安装COLMAP: https://colmap.github.io/install.html")
    print("2. 运行 run_colmap.bat 进行精确相机估计")
    print("3. 或使用简化版poses.json继续训练")
    print("=" * 60)


if __name__ == "__main__":
    main()
