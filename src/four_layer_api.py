"""
四层空间模型 API

提供RESTful API接口:
- /api/scene — 场景数据（151节点，供给前端NeuralInferencePanel）
- /api/model/* — 四层模型查询
- /api/query/* — 空间查询
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
from pathlib import Path
import json
import math
import uvicorn

# ==================== 数据模型 ====================

class ModelStats(BaseModel):
    total_blocks: int
    total_area_m2: float
    total_road_nodes: int
    total_objects: int

# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="四层空间模型 API",
    description="场景数据 + CAD解析 → 四层空间模型 → API查询",
    version="0.6.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_DATA = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\processed")

# ==================== 场景数据加载 ====================

def load_scene_data() -> dict:
    """加载VR场景数据 — 供给NeuralInferencePanel"""
    nodes = []
    edges = []
    
    objs_file = PROJECT_DATA / "building_objects_enhanced.json"
    if objs_file.exists():
        objs = json.loads(objs_file.read_text(encoding="utf-8"))
        for obj in objs:
            pos_raw = obj.get("position", [0, 1, 0])
            if isinstance(pos_raw, str):
                parts = pos_raw.split()
                pos = [float(parts[0]), float(parts[1]), float(parts[2])] if len(parts) >= 3 else [0, 1, 0]
            elif isinstance(pos_raw, list):
                pos = pos_raw
            else:
                pos = [0, 1, 0]
            nodes.append({
                "id": obj.get("id", f"obj-{len(nodes)}"),
                "type": obj.get("type", "door"),
                "name": obj.get("name", obj.get("id", "Unknown")),
                "position": pos,
                "physics": obj.get("physics", {}),
                "category": obj.get("category", "structure"),
            })
            
    # 按x坐标区间分组建边
    from collections import defaultdict
    x_groups = defaultdict(list)
    for n in nodes:
        x = n.get("position", [0])[0] if n.get("position") else 0
        x_groups[int(x // 20)].append(n["id"])
    
    for _, obj_ids in x_groups.items():
        for i in range(len(obj_ids)):
            for j in range(i + 1, len(obj_ids)):
                edges.append({
                    "source": obj_ids[i],
                    "target": obj_ids[j],
                    "relation": "same_zone",
                    "weight": 0.8,
                })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "num_nodes": len(nodes),
        "num_edges": len(edges),
        "embedding_dim": 44,
        "model_type": "vr_spatial",
    }

# ==================== API 端点 ====================

@app.get("/")
async def root():
    stats = load_scene_data()
    return {
        "name": "四层空间模型 API",
        "version": "0.6.1",
        "nodes": stats["num_nodes"],
        "edges": stats["num_edges"],
        "endpoints": ["/api/scene", "/api/model/stats", "/api/model/blocks"]
    }

@app.get("/api/scene")
async def get_scene():
    """场景数据 — NeuralInferencePanel调用"""
    return load_scene_data()

@app.get("/api/model/stats", response_model=ModelStats)
async def get_model_stats():
    stats = load_scene_data()
    return ModelStats(
        total_blocks=0,
        total_area_m2=0,
        total_road_nodes=0,
        total_objects=stats["num_nodes"]
    )

@app.get("/api/model/blocks")
async def get_all_blocks():
    data = load_scene_data()
    return {"blocks": data["nodes"], "total": data["num_nodes"]}

# ==================== 启动 ====================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    stats = load_scene_data()
    print(f"[API] 启动: http://localhost:{args.port} ({stats['num_nodes']}节点)")
    uvicorn.run(app, host="127.0.0.1", port=args.port)