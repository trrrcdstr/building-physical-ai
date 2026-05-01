"""
Gaussian Splatting API

FastAPI 服务：3D Gaussian Splatting 训练和推理接口

REST API:
  GET  /api/gaussian/scenes           → 列出所有可用 Gaussian 模型
  GET  /api/gaussian/scene/{name}     → 加载指定 Gaussian 模型，返回 JSON
  POST /api/gaussian/train            → 用指定场景图片训练新模型（异步）
  GET  /api/gaussian/status/{job_id}  → 查询训练任务状态
  POST /api/gaussian/render           → 渲染指定场景的视角
  GET  /health                        → 健康检查
"""

from __future__ import annotations
import sys
import os
import json
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# 加载项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ==================== 数据模型 ====================

class SceneInfo(BaseModel):
    """场景信息"""
    name: str
    model_path: str
    num_gaussians: int
    file_size_kb: float
    last_modified: str
    has_rendered_image: bool


class GaussianModelResponse(BaseModel):
    """高斯模型响应"""
    name: str
    num_gaussians: int
    gaussians: dict
    config: Optional[dict] = None
    training_info: Optional[dict] = None


class TrainRequest(BaseModel):
    """训练请求"""
    scene_name: str
    epochs: int = 300
    num_gaussians: int = 300
    image_size: List[int] = [160, 120]
    learning_rate: float = 0.1
    image_source: str = "renderings"  # "renderings" 或 "training"
    description: Optional[str] = None


class TrainResponse(BaseModel):
    """训练响应"""
    job_id: str
    scene_name: str
    status: str
    message: str
    estimated_time_minutes: float


class JobStatus(BaseModel):
    """任务状态"""
    job_id: str
    scene_name: str
    status: str  # "pending", "running", "completed", "failed"
    progress: float  # 0.0 - 1.0
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    current_loss: Optional[float] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    model_path: Optional[str] = None


class RenderRequest(BaseModel):
    """渲染请求"""
    scene_name: str
    camera_position: List[float] = [0, 3, -5]
    camera_target: List[float] = [0, 0.5, 0]
    width: int = 640
    height: int = 480


# ==================== 全局状态 ====================

# 训练任务存储
training_jobs: Dict[str, dict] = {}

# 路径配置
MODELS_DIR = PROJECT_ROOT / "data" / "gaussian_models"
RENDERINGS_DIR = PROJECT_ROOT / "data" / "processed" / "renderings"
TRAINING_IMAGES_DIR = PROJECT_ROOT / "data" / "gaussian_training" / "images"

# 确保目录存在
MODELS_DIR.mkdir(parents=True, exist_ok=True)
RENDERINGS_DIR.mkdir(parents=True, exist_ok=True)

# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="Gaussian Splatting API",
    description="3D Gaussian Splatting 训练和推理服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 工具函数 ====================

def list_available_scenes() -> List[SceneInfo]:
    """列出所有可用的 Gaussian 模型场景"""
    scenes = []
    
    if not MODELS_DIR.exists():
        return scenes
    
    for model_file in MODELS_DIR.glob("*.json"):
        try:
            # 读取模型信息
            with open(model_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            num_gaussians = data.get('num_gaussians', 0)
            if 'gaussians' in data and 'num_gaussians' in data['gaussians']:
                num_gaussians = data['gaussians']['num_gaussians']
            
            # 文件信息
            stat = model_file.stat()
            file_size_kb = stat.st_size / 1024
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # 检查是否有渲染图
            rendered_image = model_file.stem + "_rendered.png"
            has_rendered = (MODELS_DIR / rendered_image).exists()
            
            scenes.append(SceneInfo(
                name=model_file.stem,
                model_path=str(model_file.relative_to(PROJECT_ROOT)),
                num_gaussians=num_gaussians,
                file_size_kb=round(file_size_kb, 2),
                last_modified=last_modified,
                has_rendered_image=has_rendered
            ))
        except Exception as e:
            print(f"Error reading {model_file}: {e}")
    
    return scenes


def load_gaussian_model(scene_name: str) -> Optional[dict]:
    """加载 Gaussian 模型"""
    # 尝试不同的文件名模式
    possible_names = [
        f"{scene_name}_model.json",
        f"{scene_name}.json",
        f"{scene_name}_gpu.json",
        f"{scene_name}_v3.json",
        f"{scene_name}_v4.json"
    ]
    
    for name in possible_names:
        model_path = MODELS_DIR / name
        if model_path.exists():
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {model_path}: {e}")
                continue
    
    return None


def find_training_images(scene_name: str, source: str = "renderings") -> List[Path]:
    """查找训练图片"""
    images = []
    
    if source == "renderings":
        # 从渲染图目录查找
        scene_dir = RENDERINGS_DIR / scene_name
        if scene_dir.exists():
            images = sorted(scene_dir.glob("*.jpg"))[:10]  # 最多10张
            if not images:
                images = sorted(scene_dir.glob("*.png"))[:10]
    
    elif source == "training":
        # 从训练图目录查找
        scene_dir = TRAINING_IMAGES_DIR / scene_name
        if scene_dir.exists():
            images = sorted(scene_dir.glob("*.jpg"))[:10]
            if not images:
                images = sorted(scene_dir.glob("*.png"))[:10]
    
    return images


def train_gaussian_background(
    job_id: str,
    scene_name: str,
    epochs: int,
    num_gaussians: int,
    image_size: List[int],
    learning_rate: float,
    image_source: str
):
    """后台训练任务"""
    try:
        # 更新任务状态
        training_jobs[job_id]["status"] = "running"
        training_jobs[job_id]["start_time"] = datetime.now().isoformat()
        
        # 导入训练模块
        from text_to_4d.gaussian_splatting import GaussianSplatting3D
        
        # 查找训练图片
        images = find_training_images(scene_name, image_source)
        if not images:
            raise ValueError(f"未找到场景 '{scene_name}' 的训练图片 (source: {image_source})")
        
        training_jobs[job_id]["progress"] = 0.1
        
        # 简化训练：使用 train_gaussian_simple.py 的逻辑
        # 这里直接调用训练函数
        import torch
        import numpy as np
        from PIL import Image
        
        # 加载图片
        H, W = image_size
        image_tensors = []
        for img_path in images[:5]:  # 最多5张
            try:
                img = Image.open(img_path).convert('RGB').resize((W, H))
                img_array = np.array(img).astype(np.float32) / 255.0
                image_tensors.append(torch.from_numpy(img_array).permute(2, 0, 1))
            except Exception as e:
                print(f"跳过图片 {img_path}: {e}")
        
        if not image_tensors:
            raise ValueError("没有成功加载任何图片")
        
        # 初始化高斯参数
        N = num_gaussians
        positions = torch.rand(N, 2) * torch.tensor([W, H]).float()
        scales = torch.ones(N) * 10.0
        colors = torch.rand(N, 3)
        
        positions.requires_grad = True
        scales.requires_grad = True
        colors.requires_grad = True
        
        # 优化器
        optimizer = torch.optim.Adam([positions, scales, colors], lr=learning_rate)
        
        # 训练循环
        start_time = time.time()
        for epoch in range(epochs):
            total_loss = 0.0
            
            for img_tensor in image_tensors:
                # 向量化渲染
                N = positions.shape[0]
                y_coords = torch.arange(H, dtype=torch.float32)
                x_coords = torch.arange(W, dtype=torch.float32)
                grid = torch.stack(torch.meshgrid(y_coords, x_coords, indexing='ij'), dim=-1)
                
                pos_expanded = positions.view(1, 1, N, 2)
                grid_expanded = grid.unsqueeze(2)
                dist_sq = ((grid_expanded - pos_expanded) ** 2).sum(dim=-1)
                
                scales_expanded = scales.view(1, 1, N)
                weights = torch.exp(-0.5 * dist_sq / (scales_expanded ** 2))
                weights = weights / (weights.sum(dim=-1, keepdim=True) + 1e-6)
                
                colors_expanded = colors.view(1, 1, N, 3)
                weights_expanded = weights.unsqueeze(-1)
                rendered = (weights_expanded * colors_expanded).sum(dim=2).permute(2, 0, 1)
                
                # 损失
                loss = torch.nn.functional.mse_loss(rendered, img_tensor)
                total_loss += loss.item()
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            # 更新进度
            if (epoch + 1) % 10 == 0:
                progress = 0.1 + 0.9 * (epoch + 1) / epochs
                training_jobs[job_id]["progress"] = round(progress, 2)
                training_jobs[job_id]["current_epoch"] = epoch + 1
                training_jobs[job_id]["total_epochs"] = epochs
                training_jobs[job_id]["current_loss"] = round(total_loss, 4)
        
        # 保存模型
        result = {
            'scene': scene_name,
            'num_gaussians': N,
            'image_size': [H, W],
            'epochs': epochs,
            'final_loss': round(total_loss, 4),
            'training_time': round(time.time() - start_time, 1),
            'gaussians': {
                'positions': positions.detach().numpy().tolist(),
                'scales': scales.detach().numpy().tolist(),
                'colors': colors.detach().numpy().tolist()
            }
        }
        
        # 保存为 JSON
        output_path = MODELS_DIR / f"{scene_name}_model.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 更新任务状态
        training_jobs[job_id]["status"] = "completed"
        training_jobs[job_id]["progress"] = 1.0
        training_jobs[job_id]["end_time"] = datetime.now().isoformat()
        training_jobs[job_id]["model_path"] = str(output_path.relative_to(PROJECT_ROOT))
        
    except Exception as e:
        training_jobs[job_id]["status"] = "failed"
        training_jobs[job_id]["error_message"] = str(e)
        training_jobs[job_id]["end_time"] = datetime.now().isoformat()
        print(f"Training failed: {e}")


# ==================== API 端点 ====================

@app.get("/")
async def root():
    return {
        "service": "Gaussian Splatting API",
        "version": "1.0.0",
        "endpoints": {
            "scenes": "/api/gaussian/scenes",
            "scene": "/api/gaussian/scene/{name}",
            "train": "/api/gaussian/train",
            "status": "/api/gaussian/status/{job_id}",
            "render": "/api/gaussian/render",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_dir": str(MODELS_DIR),
        "models_count": len(list(MODELS_DIR.glob("*.json"))) if MODELS_DIR.exists() else 0
    }


@app.get("/api/gaussian/scenes", response_model=List[SceneInfo])
async def get_scenes():
    """列出所有可用 Gaussian 模型"""
    return list_available_scenes()


@app.get("/api/gaussian/scene/{scene_name}", response_model=GaussianModelResponse)
async def get_scene(scene_name: str):
    """加载指定 Gaussian 模型"""
    model_data = load_gaussian_model(scene_name)
    
    if not model_data:
        raise HTTPException(status_code=404, detail=f"场景 '{scene_name}' 未找到")
    
    # 提取高斯数据
    gaussians = model_data.get('gaussians', {})
    if not gaussians and 'positions' in model_data:
        # 兼容旧格式
        gaussians = {
            'num_gaussians': model_data.get('num_gaussians', 0),
            'positions': model_data.get('positions', []),
            'scales': model_data.get('scales', []),
            'colors': model_data.get('colors', []),
            'opacities': model_data.get('opacities', []),
            'rotations': model_data.get('rotations', [])
        }
    
    return GaussianModelResponse(
        name=scene_name,
        num_gaussians=gaussians.get('num_gaussians', 0),
        gaussians=gaussians,
        config=model_data.get('config'),
        training_info={
            'final_loss': model_data.get('final_loss'),
            'training_time': model_data.get('training_time')
        }
    )


@app.post("/api/gaussian/train", response_model=TrainResponse)
async def train_scene(request: TrainRequest, background_tasks: BackgroundTasks):
    """训练新场景（异步）"""
    # 检查场景图片是否存在
    images = find_training_images(request.scene_name, request.image_source)
    if not images:
        raise HTTPException(
            status_code=404,
            detail=f"未找到场景 '{request.scene_name}' 的训练图片 (source: {request.image_source})"
        )
    
    # 创建任务ID
    job_id = str(uuid.uuid4())[:8]
    
    # 初始化任务状态
    training_jobs[job_id] = {
        "job_id": job_id,
        "scene_name": request.scene_name,
        "status": "pending",
        "progress": 0.0,
        "current_epoch": 0,
        "total_epochs": request.epochs,
        "current_loss": None,
        "start_time": None,
        "end_time": None,
        "error_message": None,
        "model_path": None
    }
    
    # 启动后台训练任务
    background_tasks.add_task(
        train_gaussian_background,
        job_id,
        request.scene_name,
        request.epochs,
        request.num_gaussians,
        request.image_size,
        request.learning_rate,
        request.image_source
    )
    
    # 估算训练时间（简单估算）
    estimated_time = (request.epochs * len(images)) / 1000  # 粗略估算
    
    return TrainResponse(
        job_id=job_id,
        scene_name=request.scene_name,
        status="pending",
        message=f"训练任务已提交，使用 {len(images)} 张图片",
        estimated_time_minutes=round(estimated_time, 1)
    )


@app.get("/api/gaussian/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """查询训练任务状态"""
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail=f"任务 '{job_id}' 未找到")
    
    job = training_jobs[job_id]
    return JobStatus(**job)


@app.post("/api/gaussian/render")
async def render_scene(request: RenderRequest):
    """渲染指定场景的视角"""
    model_data = load_gaussian_model(request.scene_name)
    
    if not model_data:
        raise HTTPException(status_code=404, detail=f"场景 '{request.scene_name}' 未找到")
    
    # 简化渲染：返回占位响应
    # 实际应调用 renderer.py 的渲染器
    return {
        "scene_name": request.scene_name,
        "camera_position": request.camera_position,
        "camera_target": request.camera_target,
        "width": request.width,
        "height": request.height,
        "message": "渲染功能开发中，当前返回占位数据",
        "rendered_image_url": f"/api/gaussian/scene/{request.scene_name}/rendered.png"
    }


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Gaussian Splatting API 服务")
    print("=" * 60)
    print(f"模型目录: {MODELS_DIR}")
    print(f"渲染图目录: {RENDERINGS_DIR}")
    print(f"已加载场景数: {len(list_available_scenes())}")
    print("=" * 60)
    print("启动服务...")
    print("访问: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
