"""
建筑认知Agent API服务
FastAPI实现，提供RESTful接口供机器人系统调用
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 添加技能路径
SKILLS_DIR = Path(r"C:\Program Files\QClaw\resources\openclaw\config\skills")
sys.path.insert(0, str(SKILLS_DIR / "building-spatial"))
sys.path.insert(0, str(SKILLS_DIR / "building-constraint"))
sys.path.insert(0, str(SKILLS_DIR / "robot-execution"))

# 导入Agent组件
from spatial_query_engine_v2 import SpatialQueryEngineV2
from constraint_engine import ConstraintEngine
from execution_engine import ExecutionEngine

# ============== FastAPI应用 ==============

app = FastAPI(
    title="建筑认知Agent API",
    description="为机器人系统提供建筑空间认知、操作约束、执行规划能力",
    version="1.0.0",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== 请求模型 ==============

class SpatialQueryRequest(BaseModel):
    """空间查询请求"""
    query: str = Field(..., description="空间查询文本")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")

class DrillCheckRequest(BaseModel):
    """钻孔检查请求"""
    wall_side: str = Field(..., description="墙体方向: north/south/east/west")
    diameter_cm: Optional[float] = Field(default=8.0, description="孔径(厘米)")
    depth_cm: Optional[float] = Field(default=5.0, description="深度(厘米)")
    height_m: Optional[float] = Field(default=None, description="钻孔高度(米)")
    horizontal_m: Optional[float] = Field(default=None, description="水平位置(米)")

class ExecutionPlanRequest(BaseModel):
    """执行规划请求"""
    task_type: str = Field(..., description="任务类型: drill/move/clean")
    params: Dict[str, Any] = Field(default_factory=dict, description="任务参数")

class AgentTaskRequest(BaseModel):
    """Agent任务请求"""
    instruction: str = Field(..., description="自然语言指令")
    robot_id: Optional[str] = Field(default="default", description="机器人ID")
    pose: Optional[Dict[str, float]] = Field(default=None, description="机器人当前位姿")

# ============== 响应模型 ==============

class SpatialQueryResponse(BaseModel):
    """空间查询响应"""
    answer: str
    spatial_data: Dict[str, Any]
    confidence: float
    layer: str
    suggestions: List[str]

class DrillCheckResponse(BaseModel):
    """钻孔检查响应"""
    allowed: bool
    risk_level: str
    checks: Dict[str, Any]
    warnings: List[str]
    suggestions: List[str]

class ExecutionPlanResponse(BaseModel):
    """执行规划响应"""
    task_type: str
    steps: List[Dict[str, Any]]
    tools: List[Dict[str, Any]]
    safety: List[str]
    estimated_time: str
    risk_level: str

class AgentTaskResponse(BaseModel):
    """Agent任务响应"""
    status: str
    summary: str
    subtask_results: List[Dict[str, Any]]
    execution_plan: Optional[Dict[str, Any]]
    risk_level: str
    suggestions: List[str]
    timestamp: str

# ============== 全局实例 ==============

spatial_engine = None
constraint_engine = None
execution_engine = None

def init_engines():
    """初始化引擎"""
    global spatial_engine, constraint_engine, execution_engine
    if spatial_engine is None:
        spatial_engine = SpatialQueryEngineV2()
    if constraint_engine is None:
        constraint_engine = ConstraintEngine()
    if execution_engine is None:
        execution_engine = ExecutionEngine()

@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    init_engines()
    print(f"[API] 建筑认知Agent API服务启动")

# ============== API端点 ==============

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "建筑认知Agent API",
        "version": "1.0.0",
        "endpoints": [
            "/api/spatial/query - 空间查询",
            "/api/constraint/check-drill - 钻孔检查",
            "/api/execution/plan - 执行规划",
            "/api/agent/task - Agent任务处理",
            "/api/health - 健康检查",
        ]
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engines": {
            "spatial": spatial_engine is not None,
            "constraint": constraint_engine is not None,
            "execution": execution_engine is not None,
        }
    }

@app.post("/api/spatial/query", response_model=SpatialQueryResponse)
async def spatial_query(request: SpatialQueryRequest):
    """空间查询"""
    try:
        result = spatial_engine.query(request.query)
        return SpatialQueryResponse(
            answer=result.answer_text,
            spatial_data=result.spatial_data,
            confidence=result.confidence,
            layer=result.layer,
            suggestions=["查看更多空间信息", "查询相邻区域"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/constraint/check-drill", response_model=DrillCheckResponse)
async def check_drill(request: DrillCheckRequest):
    """钻孔约束检查"""
    try:
        result = constraint_engine.check_drill(
            wall_side=request.wall_side,
            diameter_cm=request.diameter_cm,
            depth_cm=request.depth_cm,
            height_m=request.height_m,
            horizontal_m=request.horizontal_m
        )
        return DrillCheckResponse(
            allowed=result.allowed,
            risk_level=result.risk_level,
            checks=result.checks,
            warnings=result.warnings,
            suggestions=result.suggestions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execution/plan", response_model=ExecutionPlanResponse)
async def generate_plan(request: ExecutionPlanRequest):
    """生成执行方案"""
    try:
        plan = execution_engine.generate_plan(request.task_type, request.params)
        return ExecutionPlanResponse(
            task_type=plan.task_type,
            steps=[{"step": s.step, "action": s.action, "params": s.params, "duration_sec": s.duration_sec} for s in plan.steps],
            tools=plan.tools,
            safety=plan.safety,
            estimated_time=plan.estimated_time,
            risk_level=plan.risk_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/task", response_model=AgentTaskResponse)
async def process_task(request: AgentTaskRequest):
    """处理Agent任务"""
    try:
        from agent_coordinator import BuildingCognitiveAgent
        agent = BuildingCognitiveAgent()
        result = agent.process(request.instruction)

        return AgentTaskResponse(
            status=result.status,
            summary=result.summary,
            subtask_results=[{"agent": r.agent, "success": r.success, "result": r.result, "confidence": r.confidence} for r in result.subtask_results],
            execution_plan=result.execution_plan,
            risk_level=result.risk_level,
            suggestions=result.suggestions,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== 统计接口 ==============

@app.get("/api/stats")
async def get_stats():
    """获取统计数据"""
    return {
        "rooms": len(spatial_engine.rooms) if spatial_engine else 0,
        "objects": len(spatial_engine.objects) if spatial_engine else 0,
        "edges": len(spatial_engine.edges) if spatial_engine else 0,
        "walls": len(constraint_engine.walls) if constraint_engine else 0,
        "pipes": len(constraint_engine.pipes) if constraint_engine else 0,
    }

# ============== 主入口 ==============

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("建筑认知Agent API服务")
    print("=" * 60)
    print("\nAPI端点:")
    print("  http://localhost:8000/")
    print("  http://localhost:8000/api/spatial/query")
    print("  http://localhost:8000/api/constraint/check-drill")
    print("  http://localhost:8000/api/execution/plan")
    print("  http://localhost:8000/api/agent/task")
    print("  http://localhost:8000/docs (Swagger UI)")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
