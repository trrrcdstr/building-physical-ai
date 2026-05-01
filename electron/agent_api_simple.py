"""
简化版 Agent API Server
不依赖缺失的 spatial_query_engine_v2 模块
使用本地数据和内存知识库
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
import uvicorn

# ============== 数据模型 ==============

class CommandRequest(BaseModel):
    command: str
    room_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class DrillRequest(BaseModel):
    wall: str  # north/south/east/west
    room_id: str
    depth_cm: Optional[float] = 6.0

class SpatialQuery(BaseModel):
    room_id: str
    query_type: str  # locate/find_path/query

# ============== FastAPI 应用 ==============

app = FastAPI(
    title="建筑认知Agent API (简化版)",
    description="基于本地数据的Agent能力",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== 本地数据 ==============

# 墙体数据
WALLS = {
    "north": {"load_bearing": True, "material": "混凝土", "thickness_cm": 24},
    "south": {"load_bearing": False, "material": "砖墙", "thickness_cm": 12},
    "east": {"load_bearing": False, "material": "砖墙", "thickness_cm": 12, "has_window": True},
    "west": {"load_bearing": False, "material": "砖墙", "thickness_cm": 12},
}

# 房间数据
ROOMS = {
    "master_bathroom": {
        "name": "主卧卫生间",
        "area_m2": 8.5,
        "type": "wet_room",
        "adjacent_rooms": ["主卧"],
        "physics_tags": ["湿区", "瓷砖地面", "玻璃隔断"],
    },
    "shower_room": {
        "name": "淋浴房",
        "area_m2": 2.1,
        "type": "wet_room",
        "adjacent_rooms": ["主卧卫生间", "马桶区", "洗手台"],
        "physics_tags": ["湿区", "瓷砖地面", "玻璃隔断", "防滑要求"],
    },
    "bedroom": {
        "name": "主卧",
        "area_m2": 20.0,
        "type": "dry_room",
        "adjacent_rooms": ["书房", "主卧卫生间"],
        "physics_tags": ["实木地板", "干燥区域"],
    },
}

# 材质物理参数
MATERIALS = {
    "瓷砖": {"friction_dry": 0.40, "friction_wet": 0.20, "density": 2300},
    "钢化玻璃": {"friction_dry": 0.35, "friction_wet": 0.18, "density": 2500},
    "实木地板": {"friction_dry": 0.40, "friction_wet": 0.25, "density": 700},
    "不锈钢": {"friction_dry": 0.20, "friction_wet": 0.12, "density": 8000},
}

# ============== API 端点 ==============

@app.get("/")
async def root():
    return {
        "name": "建筑认知Agent API (简化版)",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/health",
            "/api/agent/process",
            "/api/constraint/check-drill",
            "/api/spatial/query",
            "/api/walls",
            "/api/rooms",
        ]
    }

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "mode": "simplified",
        "data_source": "local"
    }

@app.post("/api/agent/process")
async def process_command(req: CommandRequest):
    """处理自然语言指令"""
    cmd = req.command.lower()
    room_id = req.room_id or "bedroom"

    # 钻孔任务
    if "钻" in cmd or "孔" in cmd:
        import re
        wall_match = re.search(r'([东南西北])墙', cmd)
        wall = wall_match.group(1) if wall_match else "东"
        wall_key = {"东": "east", "西": "west", "南": "south", "北": "north"}.get(wall, "east")

        wall_data = WALLS.get(wall_key, {})
        is_safe = not wall_data.get("load_bearing", False)

        return {
            "task_type": "drill",
            "success": is_safe,
            "message": f"{'可以安全钻孔' if is_safe else '禁止钻孔：承重墙'}",
            "room": room_id,
            "drill_result": {
                "wall": wall_key,
                "safe": is_safe,
                "reason": wall_data.get("material", "未知") + (" (承重墙)" if wall_data.get("load_bearing") else ""),
                "depth_cm": 6 if is_safe else None,
                "tool": "冲击钻 + 6mm钻头" if is_safe else None,
                "warnings": ["避开窗框50cm", "确认无水管电线"] if is_safe else ["禁止钻孔！"],
            },
            "confidence": 0.95
        }

    # 清洁任务
    elif "清洁" in cmd or "打扫" in cmd or "擦" in cmd:
        materials = []
        if "淋浴" in cmd or "玻璃" in cmd:
            materials.append("钢化玻璃")
        if "卫生间" in cmd or "浴室" in cmd:
            materials.append("瓷砖")
        if "卧室" in cmd or "地板" in cmd:
            materials.append("实木地板")

        if not materials:
            materials = ["瓷砖"]

        return {
            "task_type": "clean",
            "success": True,
            "message": f"清洁任务分析完成，识别材质：{', '.join(materials)}",
            "room": room_id,
            "physics_analysis": {
                "materials": [{"name": m, **MATERIALS.get(m, {})} for m in materials],
                "safety_notes": ["湿区注意防滑", "力度控制<5N"] if "玻璃" in materials else [],
            },
            "steps": [
                "安全准备：检查地面摩擦系数",
                "材质识别：确认表面类型",
                "工具选择：根据材质选择清洁工具",
                "执行清洁：按规范操作",
                "完成确认：检查清洁效果"
            ],
            "confidence": 0.90
        }

    # 搬运任务
    elif "搬" in cmd or "移动" in cmd:
        return {
            "task_type": "move",
            "success": True,
            "message": "搬运路径规划完成",
            "room": room_id,
            "steps": [
                "识别物体位置和尺寸",
                "规划搬运路径",
                "避开障碍物",
                "执行搬运",
                "确认放置位置"
            ],
            "confidence": 0.85
        }

    # 未知任务
    else:
        return {
            "task_type": "unknown",
            "success": False,
            "message": f"未识别的任务类型：{req.command}",
            "room": room_id,
            "confidence": 0.5
        }

@app.post("/api/constraint/check-drill")
async def check_drill(req: DrillRequest):
    """钻孔约束检查"""
    wall_data = WALLS.get(req.wall, {})
    is_safe = not wall_data.get("load_bearing", False)

    return {
        "wall": req.wall,
        "safe": is_safe,
        "reason": wall_data.get("material", "未知") + (" (承重墙)" if wall_data.get("load_bearing") else ""),
        "depth_cm": req.depth_cm if is_safe else None,
        "warnings": ["避开窗框50cm", "确认无水管电线"] if is_safe else ["禁止钻孔！承重墙"],
        "wall_data": wall_data
    }

@app.post("/api/spatial/query")
async def spatial_query(req: SpatialQuery):
    """空间查询"""
    room_data = ROOMS.get(req.room_id, {})

    return {
        "room_id": req.room_id,
        "room_data": room_data,
        "query_type": req.query_type,
        "result": "查询完成"
    }

@app.get("/api/walls")
async def get_walls():
    """获取所有墙体信息"""
    return {"walls": WALLS}

@app.get("/api/rooms")
async def get_rooms():
    """获取所有房间信息"""
    return {"rooms": ROOMS}

@app.get("/api/materials")
async def get_materials():
    """获取材质物理参数"""
    return {"materials": MATERIALS}

# ============== 启动服务器 ==============

if __name__ == "__main__":
    print("[Agent API] 启动简化版服务器...")
    print("[Agent API] 端口: 5002")
    print("[Agent API] 访问: http://localhost:5002")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5002,
        log_level="info"
    )
