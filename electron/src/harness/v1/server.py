"""
世界模型推理服务器 v1 - FastAPI
集成 v1 架构：语义嵌入 + 物理引擎 + 规则库 + 场景图 + VLA控制
端口: 5001
"""

import sys
import json
import torch
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

PROJECT_ROOT = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")
sys.path.insert(0, str(PROJECT_ROOT))

from src.harness.v1 import (
    WorldModelCore,
    SemanticEncoder,
    PhysicalEngine,
    RuleLibrary,
    SceneGraphBuilder,
    VLAController,
)


# ─── 数据模型 ─────────────────────────────────────────
class InstructionRequest(BaseModel):
    instruction: str
    target_object: str = None
    target_x: float = None
    target_z: float = None
    surface_width: float = 1.5
    surface_depth: float = 1.0
    material: str = "木材"


class RuleCheckRequest(BaseModel):
    rule_name: str
    value: float


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class PhysicsRequest(BaseModel):
    object_type: str
    surface_material: str = "木材"


class RelationRequest(BaseModel):
    source_node: str
    target_node: str


# ─── 全局状态 ────────────────────────────────────────
_app_state: dict = {"ready": False, "wm": None}


def get_world_model():
    if _app_state["wm"] is None:
        print("[Server] Loading WorldModelCore v1...")
        obj_path = PROJECT_ROOT / "data" / "processed" / "building_objects.json"
        _app_state["wm"] = WorldModelCore(str(obj_path) if obj_path.exists() else None)
        _app_state["ready"] = True
        print("[Server] [OK] WorldModelCore ready")
    return _app_state["wm"]


# ─── FastAPI 应用工厂 ────────────────────────────────
def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("[Server] Building Physical AI - World Model v1")
        print("[Server] Initializing modules (first load ~30s for model)...")
        get_world_model()
        print("[Server] [OK] Ready on http://127.0.0.1:5001")
        yield
        print("[Server] Shutdown")

    app = FastAPI(
        title="Building Physical AI - World Model API v1",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── 健康检查 ─────────────────────────────────────
    @app.get("/api/health")
    async def health():
        wm = get_world_model()
        s = wm.get_scene_stats()
        return {
            "status": "ok",
            "version": "v1.0.0",
            "architecture": "6-layer v1",
            "cuda": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            **s,
        }

    # ── 端到端推理 ──────────────────────────────────
    @app.post("/api/infer")
    async def infer(req: InstructionRequest):
        wm = get_world_model()
        target_pos = None
        if req.target_x is not None and req.target_z is not None:
            target_pos = {
                "x": req.target_x,
                "z": req.target_z,
                "surface_width": req.surface_width,
                "surface_depth": req.surface_depth,
                "material": req.material,
            }
        return wm.full_inference(req.instruction, req.target_object, target_pos)

    # ── VLA 指令处理 ─────────────────────────────────
    @app.post("/api/vla/instruction")
    async def vla_instruction(req: InstructionRequest):
        wm = get_world_model()
        target_pos = {"x": req.target_x, "z": req.target_z} if req.target_x else None
        plan = wm.vla.process_instruction(req.instruction, req.target_object, target_pos)
        return {"plan": plan, "execution": wm.vla.execute_plan(plan)}

    # ── 语义搜索 ────────────────────────────────────
    @app.post("/api/semantic/search")
    async def semantic_search(req: SemanticSearchRequest):
        wm = get_world_model()
        return {"results": wm.sem.find_similar_tasks(req.query, req.top_k, 0.25)}

    # ── 空间关系 ────────────────────────────────────
    @app.post("/api/relation")
    async def predict_relation(req: RelationRequest):
        wm = get_world_model()
        return wm.predict_relation(req.source_node, req.target_node)

    # ── 物理引擎 ────────────────────────────────────
    @app.post("/api/physics/can_push")
    async def can_push(req: PhysicsRequest):
        wm = get_world_model()
        return wm.physics.can_push(wm.physics.get_mass(req.object_type), material=req.surface_material)

    @app.post("/api/physics/stability")
    async def stability_check(req: PhysicsRequest):
        wm = get_world_model()
        mass = wm.physics.get_mass(req.object_type)
        surface = {
            "x": 0, "z": 0,
            "width": req.surface_width or 1.5,
            "depth": req.surface_depth or 1.0,
            "material": req.surface_material,
        }
        return wm.physics.stability_check({"x": 0, "z": 0, "width": 1.0, "depth": 1.0, "mass": mass}, surface)

    @app.get("/api/physics/drop")
    async def simulate_drop(height: float, mass: float, time: float = 1.0):
        return get_world_model().physics.simulate_drop(height, mass, time)

    # ── 建筑规则 ────────────────────────────────────
    @app.post("/api/rules/check")
    async def check_rule(req: RuleCheckRequest):
        return get_world_model().rules.check_rule(req.rule_name, req.value)

    @app.get("/api/rules/list")
    async def list_rules(category: str = None):
        return {"rules": get_world_model().rules.list_rules(category)}

    @app.get("/api/rules/clearances")
    async def list_clearances():
        return {"clearances": get_world_model().rules.clearances}

    # ── 场景图 ──────────────────────────────────────
    @app.get("/api/scene")
    async def get_scene():
        return get_world_model().scene_graph.to_dict()

    @app.get("/api/scene/stats")
    async def get_scene_stats():
        return get_world_model().get_scene_stats()

    @app.get("/api/scene/neighbors/{node_id}")
    async def get_neighbors(node_id: str, relation_type: str = None):
        return {"neighbors": get_world_model().scene_graph.get_neighbors(node_id, relation_type)}

    return app


# ─── 启动入口 ────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Building Physical AI - World Model API v1")
    print("  Architecture: 6-Layer Full Stack")
    print("  Embedding: paraphrase-multilingual-MiniLM-L12-v2")
    print("  Physics: Non-learned Newtonian Engine")
    print("  Rules: GB 50763 / GB 50016 / GB 50096")
    print("  Port: 5001")
    print("=" * 60)
    uvicorn.run(
        create_app(),
        host="127.0.0.1",
        port=5001,
        log_level="info",
    )


if __name__ == "__main__":
    main()
