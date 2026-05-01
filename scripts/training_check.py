"""
高斯泼斯训练检测

检查训练环境和数据准备情况
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    return f"{version.major}.{version.minor}.{version.micro}"


def check_gpu():
    """检查GPU"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            return True, gpu_name, f"{gpu_memory:.1f}GB"
        else:
            return False, "无", "0GB"
    except ImportError:
        return None, "PyTorch未安装", "—"


def check_dependencies():
    """检查依赖"""
    deps = {
        'numpy': 'numpy',
        'PIL': 'pillow',
        'torch': 'torch',
        'cv2': 'opencv-python',
        'scipy': 'scipy',
        'trimesh': 'trimesh',
    }
    
    results = {}
    for import_name, package_name in deps.items():
        try:
            __import__(import_name)
            results[package_name] = "✅"
        except ImportError:
            results[package_name] = "❌"
    
    return results


def check_training_data():
    """检查训练数据"""
    base_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")
    
    data_files = {
        'VR知识库': base_path / "knowledge/VR_KNOWLEDGE.json",
        '效果图索引': base_path / "data/rendering_database.json",
        '训练配置': base_path / "data/gaussian_training/training_config.json",
        'CAD数据库': base_path / "knowledge/CAD_DATABASE.json",
        '建筑对象': base_path / "data/processed/building_objects.json",
    }
    
    results = {}
    for name, path in data_files.items():
        if path.exists():
            size = path.stat().st_size / 1024
            results[name] = f"✅ {size:.1f}KB"
        else:
            results[name] = "❌ 不存在"
    
    return results


def count_training_images():
    """统计训练图片"""
    training_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\gaussian_training\images")
    
    if not training_dir.exists():
        return {}
    
    scenes = {}
    for scene_dir in training_dir.iterdir():
        if scene_dir.is_dir():
            count = len(list(scene_dir.glob("*.jpg"))) + len(list(scene_dir.glob("*.png")))
            scenes[scene_dir.name] = count
    
    return scenes


def estimate_training_time(num_images, num_gaussians=10000):
    """估算训练时间"""
    # 经验值：每张图片每1000高斯约0.1秒（RTX 3090）
    # 实际取决于GPU和迭代次数
    
    # 假设RTX 3060 (6GB)
    seconds_per_image = 0.15  # 保守估计
    
    total_time = num_images * seconds_per_image * (num_gaussians / 1000) * 30  # 30k iterations
    
    hours = total_time / 3600
    return hours


def main():
    import io
    import sys
    # Force UTF-8 output
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("高斯泼斯训练检测")
    print("=" * 60)
    print()
    
    # 1. Python版本
    print("【1】Python环境")
    print(f"    版本: {check_python_version()}")
    print()
    
    # 2. GPU
    print("【2】GPU检测")
    gpu_ok, gpu_name, gpu_mem = check_gpu()
    if gpu_ok is True:
        print(f"    状态: ✅ CUDA可用")
        print(f"    GPU: {gpu_name}")
        print(f"    显存: {gpu_mem}")
    elif gpu_ok is False:
        print(f"    状态: ⚠️ CUDA不可用（将使用CPU）")
    else:
        print(f"    状态: {gpu_name}")
    print()
    
    # 3. 依赖
    print("【3】依赖检查")
    deps = check_dependencies()
    for name, status in deps.items():
        print(f"    {name}: {status}")
    print()
    
    # 4. 训练数据
    print("【4】训练数据")
    data = check_training_data()
    for name, status in data.items():
        print(f"    {name}: {status}")
    print()
    
    # 5. 场景分布
    print("【5】场景分布")
    scenes = count_training_images()
    total_images = sum(scenes.values())
    for scene, count in sorted(scenes.items(), key=lambda x: x[1], reverse=True):
        print(f"    {scene}: {count}张")
    print(f"    ————————————")
    print(f"    总计: {total_images}张")
    print()
    
    # 6. 训练估算
    print("【6】训练估算")
    if total_images > 0:
        hours = estimate_training_time(total_images)
        print(f"    图片数: {total_images}")
        print(f"    高斯数: 10,000/场景")
        print(f"    迭代数: 30,000")
        print(f"    预估时间: {hours:.1f}小时 (RTX 3060)")
        print(f"    预估时间: {hours*0.5:.1f}小时 (RTX 3090)")
    print()
    
    # 7. 建议
    print("【7】建议")
    
    issues = []
    
    if deps.get('torch') == '❌':
        issues.append("安装PyTorch: pip install torch torchvision")
    
    if deps.get('opencv-python') == '❌':
        issues.append("安装OpenCV: pip install opencv-python")
    
    if gpu_ok is False:
        issues.append("CUDA不可用，训练将使用CPU（速度慢）")
    
    if total_images < 100:
        issues.append("训练图片较少，建议增加数据")
    
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"    {i}. {issue}")
    else:
        print("    ✅ 环境就绪，可以开始训练")
    
    print()
    print("=" * 60)
    
    # 返回状态
    return {
        'gpu_available': gpu_ok,
        'total_images': total_images,
        'ready': len(issues) == 0,
        'issues': issues
    }


if __name__ == "__main__":
    result = main()
    
    # 保存结果
    output_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\training_check.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
