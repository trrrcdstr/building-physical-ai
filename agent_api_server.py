"""
建筑认知Agent API服务 v2
提供HTTP接口让机器人系统调用Agent能力
改进：增强任务分类、搬运能力、真实数据接入
"""
import sys, io, json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# FastAPI
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 导入主Agent v2
BASE_DIR = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai")
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent / "skills" / "building-spatial"))
sys.path.insert(0, str(BASE_DIR.parent / "skills" / "building-constraint"))
sys.path.insert(0, str(BASE_DIR.parent / "skills" / "robot-execution"))

from agent_coordinator import BuildingCognitiveAgent, TaskResult

# ============== FastAPI应用 ==============

app = FastAPI(
    title="建筑认知Agent API",
    description="提供建筑空间理解、操作约束检查、执行方案生成等能力",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化Agent
agent = None

@app.on_event("startup")
async def startup():
    global agent
    agent = BuildingCognitiveAgent()
    print("[API] 建筑认知Agent已初始化")

# ============== 请求模型 ==============

class InstructionRequest(BaseModel):
    """指令请求"""
    instruction: str
    context: Optional[Dict[str, Any]] = None

class DrillCheckRequest(BaseModel):
    """钻孔检查请求"""
    wall_side: str
    diameter_cm: Optional[float] = None
    depth_cm: Optional[float] = None
    height_m: Optional[float] = None

class SpatialQueryRequest(BaseModel):
    """空间查询请求"""
    query: str

# ============== API端点 ==============

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "建筑认知Agent API v2",
        "version": "2.0.0",
        "improvements": [
            "增强任务分类（钻孔关键词扩展）",
            "北墙承重墙正确拒绝",
            "搬运能力补充（物体定位+路径规划）",
            "真实数据接入（building_objects.json）"
        ],
        "endpoints": [
            "/api/agent/process - 处理用户指令",
            "/api/constraint/check-drill - 检查钻孔约束",
            "/api/spatial/query - 空间查询",
            "/api/spatial/locate-object - 物体定位",
            "/api/spatial/find-path - 路径规划",
            "/api/data/stats - 数据统计",
            "/api/health - 健康检查"
        ]
    }

@app.get("/api/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "agent_initialized": agent is not None,
        "version": "2.0.0",
        "capabilities": [
            "spatial_understanding", 
            "constraint_checking", 
            "execution_planning",
            "object_location",      # 新增
            "path_planning",        # 新增
            "real_data_connection"  # 新增
        ]
    }

@app.post("/api/agent/process")
async def process_instruction(request: InstructionRequest):
    """处理用户指令"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    result = agent.process(request.instruction)
    
    return {
        "status": result.status,
        "summary": result.summary,
        "risk_level": result.risk_level,
        "suggestions": result.suggestions,
        "subtask_results": [
            {
                "agent": r.agent,
                "success": r.success,
                "confidence": r.confidence,
                "result": r.result
            }
            for r in result.subtask_results
        ],
        "execution_plan": result.execution_plan
    }

@app.post("/api/constraint/check-drill")
async def check_drill(request: DrillCheckRequest):
    """检查钻孔约束"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    result = agent.constraint_engine.check_drill(
        request.wall_side,
        request.diameter_cm,
        request.depth_cm,
        request.height_m
    )
    
    return {
        "allowed": result.allowed,
        "risk_level": result.risk_level,
        "checks": result.checks,
        "warnings": result.warnings,
        "suggestions": result.suggestions
    }

@app.post("/api/spatial/query")
async def spatial_query(request: SpatialQueryRequest):
    """空间查询"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    result = agent.spatial_engine.query(request.query)
    
    return {
        "answer": result.answer_text,
        "confidence": result.confidence,
        "spatial_data": result.spatial_data,
        "query_type": result.query_type
    }

# ============== 新增API端点 ==============

class LocateObjectRequest(BaseModel):
    """物体定位请求"""
    object_name: str

class FindPathRequest(BaseModel):
    """路径规划请求"""
    start_x: float
    start_y: float
    end_x: float
    end_y: float

@app.post("/api/spatial/locate-object")
async def locate_object(request: LocateObjectRequest):
    """物体定位"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    result = agent.object_locator.locate(request.object_name)
    
    return {
        "object": result['object'],
        "position": result['position'],
        "confidence": result['confidence']
    }

@app.post("/api/spatial/find-path")
async def find_path(request: FindPathRequest):
    """路径规划"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    start = {'x': request.start_x, 'y': request.start_y, 'z': 0}
    end = {'x': request.end_x, 'y': request.end_y, 'z': 0}
    
    result = agent.object_locator.find_path(start, end)
    
    return {
        "path": result['path'],
        "distance": result['distance'],
        "estimated_time": result['estimated_time'],
        "obstacles": result['obstacles']
    }

@app.get("/api/data/stats")
async def data_stats():
    """数据统计"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    stats = agent.data_connector.get_object_count()
    
    return {
        "building_objects": stats['total'],
        "doors": stats['doors'],
        "windows": stats['windows'],
        "walls": len(agent.data_connector.walls),
        "scene_graph_nodes": len(agent.data_connector.scene_graph.get('nodes', []))
    }

@app.get("/api/walls")
async def list_walls():
    """列出所有墙体"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    return {
        "walls": agent.data_connector.walls
    }

# ============== 启动入口 ==============

if __name__ == "__main__":
    import uvicorn
    print("[API v2] 建筑认知Agent API服务启动中...")
    print("  地址: http://localhost:5002")
    print("  文档: http://localhost:5002/docs")
    uvicorn.run(app, host="0.0.0.0", port=5002)
