# -*- coding: utf-8 -*-
"""
unified_api.py — 统一 API 入口（云端部署版）
=============================================
将 4 个后端服务合并为一个 FastAPI 应用：
  /neural/*   — 神经网络推理 (原 port 5000)
  /scene/*    — 场景数据 API (原 port 5001)
  /agent/*    — Agent 指令处理 (原 port 5002)
  /vla/*      — VLA 指令分类 (原 port 5004)

Railway 部署只需 1 个服务，1 个端口。
"""

from __future__ import annotations
import sys
import os
from pathlib import Path

# ── 路径设置 ──
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── 创建主应用 ──
app = FastAPI(
    title="Building Physical AI - Unified API",
    version="2.0.0",
    description="建筑物理AI世界模型 - 统一API服务",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 挂载子应用 ──
# 1. Neural Inference (原 5000)
try:
    from neural_inference_server import create_api_server
    neural_app = create_api_server()
    if neural_app is not None:
        app.mount("/neural", neural_app)
        NEURAL_OK = True
    else:
        NEURAL_OK = False
        NEURAL_ERROR = "create_api_server() returned None"
except Exception as e:
    NEURAL_OK = False
    NEURAL_ERROR = str(e)
    print(f"[WARN] Neural Inference 加载失败: {e}")

# 2. Scene API (原 5001)
try:
    from four_layer_api import app as scene_app
    app.mount("/scene", scene_app)
    SCENE_OK = True
except Exception as e:
    SCENE_OK = False
    SCENE_ERROR = str(e)
    print(f"[WARN] Scene API 加载失败: {e}")

# 3. Agent API (原 5002)
try:
    # agent_api_simple.py 在项目根目录
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "agent_api_simple",
        str(PROJECT_ROOT / "agent_api_simple.py")
    )
    agent_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_mod)
    app.mount("/agent", agent_mod.app)
    AGENT_OK = True
except Exception as e:
    AGENT_OK = False
    AGENT_ERROR = str(e)
    print(f"[WARN] Agent API 加载失败: {e}")

# 4. VLA Service (原 5004)
try:
    from vla_server import load_model, infer, ACTION_KEYWORDS, DEFAULT_PORT
    vla_model, vla_task_list, vla_val_acc = load_model()
    
    from fastapi import FastAPI as _FastAPI
    from pydantic import BaseModel as _BaseModel
    
    vla_app = _FastAPI(title="Psi-R2 VLA", version="v3")
    
    class _VLARequest(_BaseModel):
        instruction: str
        room_id: str = 'room_00'
    
    @vla_app.get("/api/health")
    async def vla_health():
        return {
            "status": "ok", "model": "Psi-R2 VLA",
            "version": "v3-balanced",
            "val_acc": vla_val_acc or 0,
            "tasks": vla_task_list or [],
            "ready": vla_model is not None,
        }
    
    @vla_app.post("/api/classify")
    async def vla_classify(req: _VLARequest):
        result = infer(req.instruction, req.room_id, vla_model, vla_task_list)
        return result
    
    app.mount("/vla", vla_app)
    VLA_OK = True
except Exception as e:
    VLA_OK = False
    VLA_ERROR = str(e)
    print(f"[WARN] VLA Service 加载失败: {e}")


# ── 根路由：健康检查 + 服务状态 ──
@app.get("/")
async def root():
    return {
        "service": "Building Physical AI - Unified API",
        "version": "2.0.0",
        "status": "online",
        "services": {
            "neural": {"status": "ok" if NEURAL_OK else "error",
                       "error": None if NEURAL_OK else NEURAL_ERROR},
            "scene": {"status": "ok" if SCENE_OK else "error",
                      "error": None if SCENE_OK else SCENE_ERROR},
            "agent": {"status": "ok" if AGENT_OK else "error",
                      "error": None if AGENT_OK else AGENT_ERROR},
            "vla": {"status": "ok" if VLA_OK else "error",
                    "error": None if VLA_OK else VLA_ERROR},
        }
    }

@app.get("/api/health")
async def health():
    return await root()


# ── 启动入口 ──
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Unified API on port {port}...")
    print(f"  Neural:  {'OK' if NEURAL_OK else 'ERROR'}")
    print(f"  Scene:   {'OK' if SCENE_OK else 'ERROR'}")
    print(f"  Agent:   {'OK' if AGENT_OK else 'ERROR'}")
    print(f"  VLA:     {'OK' if VLA_OK else 'ERROR'}")
    uvicorn.run(app, host="0.0.0.0", port=port)
