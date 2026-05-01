"""
智能体集群系统

多智能体协作构建世界模型
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(name)s] %(message)s')
logger = logging.getLogger("AgentCluster")

# ==================== 数据结构定义 ====================

class AgentType(Enum):
    MASTER = "master"
    SPATIAL = "spatial"
    VISUAL = "visual"
    PHYSICS = "physics"
    LANDSCAPE = "landscape"

class TaskType(Enum):
    BUILD_WORLD_MODEL = "build_world_model"
    PARSE_CAD = "parse_cad"
    ANALYZE_VR = "analyze_vr"
    VALIDATE_OPERATION = "validate_operation"
    PLAN_PATH = "plan_path"

@dataclass
class AgentTask:
    """智能体任务"""
    task_id: str
    task_type: TaskType
    agent_type: AgentType
    input_data: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AgentMessage:
    """智能体间通信消息"""
    from_agent: AgentType
    to_agent: AgentType
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

# ==================== 基础智能体类 ====================

class BaseAgent:
    """智能体基类"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.name = f"{agent_type.value}_agent"
        self.capabilities: List[str] = []
        self.logger = logging.getLogger(self.name)
    
    def can_handle(self, task_type: TaskType) -> bool:
        """检查是否能处理该任务"""
        return task_type.value in self.capabilities
    
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """处理任务"""
        raise NotImplementedError

# ==================== 1. 🧠 建筑认知主智能体 ====================

class MasterAgent(BaseAgent):
    """
    建筑认知主智能体
    
    职责: 总指挥，任务规划，智能体调度，结果融合
    """
    
    def __init__(self):
        super().__init__(AgentType.MASTER)
        self.capabilities = [
            "task_planning",
            "intent_understanding",
            "agent_dispatch",
            "result_fusion"
        ]
        
        # 初始化子智能体
        self.spatial_agent = None
        self.visual_agent = None
        self.physics_agent = None
        self.landscape_agent = None
        
        # 任务队列
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
    
    def register_agents(self, spatial, visual, physics, landscape):
        """注册子智能体"""
        self.spatial_agent = spatial
        self.visual_agent = visual
        self.physics_agent = physics
        self.landscape_agent = landscape
        self.logger.info("子智能体注册完成")
    
    def understand_intent(self, instruction: str) -> Dict[str, Any]:
        """理解用户意图"""
        instruction_lower = instruction.lower()
        
        # 意图识别（关键词匹配 - 支持中英文）
        intents = {
            "build_world_model": [
                "构建", "建立", "创建", "世界模型", "解析cad",
                "build", "create", "world model", "parse cad", "cad"
            ],
            "drill_operation": [
                "钻孔", "打孔", "开洞", "drill", "hole"
            ],
            "move_object": [
                "搬运", "移动", "搬", "move", "transport"
            ],
            "clean_area": [
                "清洁", "打扫", "清理", "clean"
            ],
            "query_info": [
                "查询", "什么", "哪里", "多少", "query", "what", "where"
            ]
        }
        
        detected_intent = None
        max_matches = 0
        
        for intent, keywords in intents.items():
            matches = sum(1 for kw in keywords if kw in instruction_lower)
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
        
        return {
            "intent": detected_intent or "unknown",
            "instruction": instruction,
            "confidence": min(0.9, 0.3 + max_matches * 0.2)
        }
    
    def decompose_tasks(self, intent: Dict) -> List[AgentTask]:
        """任务分解"""
        intent_type = intent["intent"]
        tasks = []
        
        if intent_type == "build_world_model":
            tasks = [
                AgentTask(
                    task_id="task_001",
                    task_type=TaskType.PARSE_CAD,
                    agent_type=AgentType.SPATIAL,
                    input_data={"source": "cad"}
                ),
                AgentTask(
                    task_id="task_002",
                    task_type=TaskType.ANALYZE_VR,
                    agent_type=AgentType.VISUAL,
                    input_data={"source": "vr"}
                ),
                AgentTask(
                    task_id="task_003",
                    task_type=TaskType.VALIDATE_OPERATION,
                    agent_type=AgentType.PHYSICS,
                    input_data={"operation": "init"}
                )
            ]
        
        elif intent_type == "drill_operation":
            tasks = [
                AgentTask(
                    task_id="task_001",
                    task_type=TaskType.PLAN_PATH,
                    agent_type=AgentType.SPATIAL,
                    input_data={"target": "wall"}
                ),
                AgentTask(
                    task_id="task_002",
                    task_type=TaskType.VALIDATE_OPERATION,
                    agent_type=AgentType.PHYSICS,
                    input_data={"operation": "drill"}
                )
            ]
        
        return tasks
    
    async def dispatch_agents(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """调度智能体执行任务"""
        results = {}
        
        for task in tasks:
            self.logger.info(f"调度任务: {task.task_id} → {task.agent_type.value}")
            
            agent = self._get_agent(task.agent_type)
            if agent:
                try:
                    result = await agent.process(task)
                    task.result = result
                    task.status = "completed"
                    results[task.task_id] = result
                except Exception as e:
                    task.status = "failed"
                    results[task.task_id] = {"error": str(e)}
            
            self.completed_tasks.append(task)
        
        return results
    
    def merge_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """融合各智能体结果"""
        world_model = {
            "spatial": {},
            "visual": {},
            "physics": {},
            "landscape": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "agent_count": 4,
                "task_count": len(self.completed_tasks)
            }
        }
        
        for task_id, result in results.items():
            if "error" not in result:
                # 根据任务类型分类结果
                if "spatial" in result:
                    world_model["spatial"] = result["spatial"]
                if "visual" in result:
                    world_model["visual"] = result["visual"]
                if "physics" in result:
                    world_model["physics"] = result["physics"]
                if "landscape" in result:
                    world_model["landscape"] = result["landscape"]
        
        return world_model
    
    async def process(self, instruction: str) -> Dict[str, Any]:
        """主处理流程"""
        self.logger.info(f"处理指令: {instruction}")
        
        # 1. 意图理解
        intent = self.understand_intent(instruction)
        self.logger.info(f"识别意图: {intent['intent']}")
        
        # 2. 任务分解
        tasks = self.decompose_tasks(intent)
        self.logger.info(f"分解任务: {len(tasks)} 个")
        
        # 3. 智能体调度
        results = await self.dispatch_agents(tasks)
        
        # 4. 结果融合
        world_model = self.merge_results(results)
        
        return {
            "intent": intent,
            "tasks": [t.__dict__ for t in self.completed_tasks],
            "world_model": world_model
        }
    
    def _get_agent(self, agent_type: AgentType):
        """获取智能体实例"""
        agents = {
            AgentType.SPATIAL: self.spatial_agent,
            AgentType.VISUAL: self.visual_agent,
            AgentType.PHYSICS: self.physics_agent,
            AgentType.LANDSCAPE: self.landscape_agent
        }
        return agents.get(agent_type)

# ==================== 2. 🗺️ 空间结构智能体 ====================

class SpatialAgent(BaseAgent):
    """
    空间结构智能体
    
    职责: CAD解析，几何计算，Block/Road层建模
    """
    
    def __init__(self, four_layer_api_url: str = "http://localhost:5003"):
        super().__init__(AgentType.SPATIAL)
        self.capabilities = [
            "parse_cad",
            "build_block",
            "build_road",
            "plan_path",
            "spatial_query"
        ]
        self.api_url = four_layer_api_url
        self.model = None
    
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """处理空间相关任务"""
        self.logger.info(f"处理任务: {task.task_type.value}")
        
        if task.task_type == TaskType.PARSE_CAD:
            return await self._parse_cad(task.input_data)
        elif task.task_type == TaskType.PLAN_PATH:
            return await self._plan_path(task.input_data)
        else:
            return {"error": f"未知任务类型: {task.task_type}"}
    
    async def _parse_cad(self, input_data: Dict) -> Dict[str, Any]:
        """解析CAD"""
        # 调用四层模型API
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/api/model/blocks") as resp:
                    blocks = await resp.json()
                
                async with session.get(f"{self.api_url}/api/model/stats") as resp:
                    stats = await resp.json()
            
            return {
                "spatial": {
                    "blocks": blocks.get("blocks", []),
                    "stats": stats
                }
            }
        except Exception as e:
            # 如果API不可用，返回模拟数据
            return {
                "spatial": {
                    "blocks": [
                        {"id": "block_001", "area_m2": 27.6, "function": "living_room"}
                    ],
                    "stats": {"total_blocks": 5, "total_area_m2": 31.5}
                }
            }
    
    async def _plan_path(self, input_data: Dict) -> Dict[str, Any]:
        """路径规划"""
        return {
            "spatial": {
                "path": ["start", "block_003", "target"],
                "distance_mm": 3500,
                "estimated_time_s": 15
            }
        }

# ==================== 3. 🖼️ 视觉语义智能体 ====================

class VisualAgent(BaseAgent):
    """
    视觉语义智能体
    
    职责: VR效果图解析，语义分割，Function/Object层建模
    """
    
    def __init__(self, vr_data_path: str = ""):
        super().__init__(AgentType.VISUAL)
        self.capabilities = [
            "analyze_vr",
            "detect_objects",
            "segment_functions",
            "classify_scene"
        ]
        self.vr_data_path = vr_data_path
    
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """处理视觉相关任务"""
        self.logger.info(f"处理任务: {task.task_type.value}")
        
        if task.task_type == TaskType.ANALYZE_VR:
            return await self._analyze_vr(task.input_data)
        else:
            return {"error": f"未知任务类型: {task.task_type}"}
    
    async def _analyze_vr(self, input_data: Dict) -> Dict[str, Any]:
        """分析VR效果图"""
        # 加载VR数据
        vr_data = self._load_vr_data()
        
        return {
            "visual": {
                "scene_type": "living_room",
                "objects": vr_data.get("objects", []),
                "functions": vr_data.get("functions", []),
                "confidence": 0.85
            }
        }
    
    def _load_vr_data(self) -> Dict:
        """加载VR数据"""
        # 从VR知识库加载数据
        vr_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\VR_KNOWLEDGE.json")
        
        if vr_path.exists():
            with open(vr_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    "objects": [
                        {"type": "sofa", "count": 1},
                        {"type": "coffee_table", "count": 1},
                        {"type": "tv", "count": 1}
                    ],
                    "functions": ["living_room", "dining"],
                    "vr_count": len(data) if isinstance(data, list) else 0
                }
        
        return {"objects": [], "functions": []}

# ==================== 4. ⚖️ 物理规则智能体 ====================

class PhysicsAgent(BaseAgent):
    """
    物理规则智能体
    
    职责: 规范解读，物理属性映射，安全约束验证
    """
    
    def __init__(self):
        super().__init__(AgentType.PHYSICS)
        self.capabilities = [
            "validate_operation",
            "check_wall_type",
            "check_pipe_location",
            "apply_physics_rules"
        ]
        self.materials = self._load_materials()
        self.rules = self._load_rules()
    
    def _load_materials(self) -> Dict:
        """加载材料属性"""
        mat_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\MATERIAL_PROPERTIES.json")
        
        if mat_path.exists():
            with open(mat_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("materials", {})
        
        return {}
    
    def _load_rules(self) -> Dict:
        """加载建筑规则"""
        rules_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\knowledge\BUILDING_RULES.json")
        
        if rules_path.exists():
            with open(rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("rules", {})
        
        return {}
    
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """处理物理规则相关任务"""
        self.logger.info(f"处理任务: {task.task_type.value}")
        
        if task.task_type == TaskType.VALIDATE_OPERATION:
            return await self._validate_operation(task.input_data)
        else:
            return {"error": f"未知任务类型: {task.task_type}"}
    
    async def _validate_operation(self, input_data: Dict) -> Dict[str, Any]:
        """验证操作安全性"""
        operation = input_data.get("operation", "unknown")
        
        if operation == "init":
            # 初始化时返回规则摘要
            return {
                "physics": {
                    "materials_count": len(self.materials),
                    "rules_count": len(self.rules),
                    "status": "ready"
                }
            }
        
        # 钻孔验证
        if operation == "drill":
            return self._validate_drill(input_data)
        
        return {"physics": {"allowed": True, "warnings": []}}
    
    def _validate_drill(self, params: Dict) -> Dict[str, Any]:
        """验证钻孔操作"""
        wall_type = params.get("wall_type", "unknown")
        
        # 规则检查
        allowed = True
        warnings = []
        
        if wall_type == "load_bearing":
            allowed = False
            warnings.append("承重墙禁止钻孔")
        
        return {
            "physics": {
                "allowed": allowed,
                "warnings": warnings,
                "risk_level": "high" if not allowed else "low"
            }
        }

# ==================== 5. 🌳 园林景观智能体 ====================

class LandscapeAgent(BaseAgent):
    """
    园林景观智能体
    
    职责: 地形分析，植物配置，室外空间建模
    """
    
    def __init__(self):
        super().__init__(AgentType.LANDSCAPE)
        self.capabilities = [
            "analyze_terrain",
            "identify_vegetation",
            "extract_paths",
            "outdoor_modeling"
        ]
    
    async def process(self, task: AgentTask) -> Dict[str, Any]:
        """处理园林相关任务"""
        self.logger.info(f"处理任务: {task.task_type.value}")
        
        # 返回园林场景数据
        return {
            "landscape": {
                "terrain": {"type": "flat", "slope_deg": 0},
                "vegetation": [
                    {"type": "tree", "count": 5},
                    {"type": "shrub", "count": 12}
                ],
                "paths": [
                    {"type": "walkway", "width_m": 1.5}
                ]
            }
        }

# ==================== 智能体集群管理器 ====================

class AgentCluster:
    """智能体集群管理器"""
    
    def __init__(self):
        # 创建所有智能体
        self.master = MasterAgent()
        self.spatial = SpatialAgent()
        self.visual = VisualAgent()
        self.physics = PhysicsAgent()
        self.landscape = LandscapeAgent()
        
        # 注册智能体
        self.master.register_agents(
            self.spatial,
            self.visual,
            self.physics,
            self.landscape
        )
        
        self.logger = logging.getLogger("AgentCluster")
        self.logger.info("智能体集群初始化完成")
    
    async def process(self, instruction: str) -> Dict[str, Any]:
        """处理用户指令"""
        return await self.master.process(instruction)
    
    def get_status(self) -> Dict[str, Any]:
        """获取集群状态"""
        return {
            "agents": {
                "master": {"status": "ready", "tasks_completed": len(self.master.completed_tasks)},
                "spatial": {"status": "ready"},
                "visual": {"status": "ready"},
                "physics": {"status": "ready", "materials": len(self.physics.materials)},
                "landscape": {"status": "ready"}
            },
            "timestamp": datetime.now().isoformat()
        }

# ==================== API接口 ====================

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="智能体集群 API", version="1.0.0")

# 全局集群实例
cluster = AgentCluster()

class ProcessRequest(BaseModel):
    instruction: str

@app.get("/")
async def root():
    return {
        "name": "智能体集群 API",
        "version": "1.0.0",
        "agents": ["master", "spatial", "visual", "physics", "landscape"]
    }

@app.get("/status")
async def get_status():
    return cluster.get_status()

@app.post("/process")
async def process_instruction(request: ProcessRequest):
    result = await cluster.process(request.instruction)
    return result

if __name__ == "__main__":
    import uvicorn
    
    print("[智能体集群] 启动服务: http://localhost:5004")
    uvicorn.run(app, host="localhost", port=5004)
