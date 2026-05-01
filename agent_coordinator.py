"""
建筑认知主Agent协调器 v2
改进：任务分类增强、搬运能力补充、真实数据接入
"""
import sys, io, json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加技能路径
SKILLS_DIR = Path(r"C:\Program Files\QClaw\resources\openclaw\config\skills")
sys.path.insert(0, str(SKILLS_DIR / "building-spatial"))
sys.path.insert(0, str(SKILLS_DIR / "building-constraint"))
sys.path.insert(0, str(SKILLS_DIR / "robot-execution"))

from spatial_query_engine_v2 import SpatialQueryEngineV2
from constraint_engine import ConstraintEngine
from execution_engine import ExecutionEngine

# ============== 数据结构 ==============

@dataclass
class AgentResult:
    """子Agent结果"""
    agent: str
    success: bool
    result: Dict[str, Any]
    confidence: float

@dataclass
class TaskResult:
    """任务结果"""
    status: str  # success, warning, error
    summary: str
    subtask_results: List[AgentResult]
    execution_plan: Optional[Dict]
    risk_level: str
    suggestions: List[str]

# ============== 改进1：增强任务分类器 ==============

class TaskClassifier:
    """任务分类器（改进版）"""
    
    # 钻孔类关键词（扩展）
    DRILL_KEYWORDS = [
        '钻孔', '打孔', '开洞', '钻', '打眼', '开孔', 
        '钻一个', '钻个', '钻孔', '打个孔', '开个孔',
        '穿孔', '透孔', '钻孔作业', '钻孔操作'
    ]
    
    # 搬运类关键词
    MOVE_KEYWORDS = [
        '搬运', '移动', '搬', '挪', '移到', '搬到',
        '移动到', '搬运到', '挪到', '转移到'
    ]
    
    # 清洁类关键词
    CLEAN_KEYWORDS = [
        '清洁', '打扫', '擦拭', '清理', '洗', '拖',
        '扫地', '吸尘', '擦地', '拖地'
    ]
    
    # 检查类关键词
    INSPECT_KEYWORDS = [
        '检查', '巡检', '测量', '查看', '检查一下',
        '检测', '排查', '诊断'
    ]
    
    # 查询类关键词
    QUERY_KEYWORDS = [
        '在哪', '在哪里', '有多少', '什么位置', '多大', '多高', '多宽',
        '是什么', '有哪些', '怎么样'
    ]
    
    @classmethod
    def classify(cls, instruction: str) -> str:
        """分类任务"""
        instruction_lower = instruction.lower()
        
        # 钻孔任务优先检测（因为关键词较短，容易误判）
        for keyword in cls.DRILL_KEYWORDS:
            if keyword in instruction:
                return 'drill'
        
        # 搬运任务
        for keyword in cls.MOVE_KEYWORDS:
            if keyword in instruction:
                return 'move'
        
        # 清洁任务
        for keyword in cls.CLEAN_KEYWORDS:
            if keyword in instruction:
                return 'clean'
        
        # 检查任务
        for keyword in cls.INSPECT_KEYWORDS:
            if keyword in instruction:
                return 'inspect'
        
        # 查询任务
        for keyword in cls.QUERY_KEYWORDS:
            if keyword in instruction:
                return 'query'
        
        return 'unknown'

# ============== 改进2：墙体方向识别器 ==============

class WallDirectionExtractor:
    """墙体方向提取器"""
    
    DIRECTION_MAP = {
        '东': 'east', '东面': 'east', '东墙': 'east', '东侧': 'east',
        '西': 'west', '西面': 'west', '西墙': 'west', '西侧': 'west',
        '南': 'south', '南面': 'south', '南墙': 'south', '南侧': 'south',
        '北': 'north', '北面': 'north', '北墙': 'north', '北侧': 'north',
    }
    
    @classmethod
    def extract(cls, instruction: str) -> str:
        """提取墙体方向"""
        for keyword, direction in cls.DIRECTION_MAP.items():
            if keyword in instruction:
                return direction
        return 'unknown'

# ============== 改进3：物体定位器 ==============

class ObjectLocator:
    """物体定位器（为搬运任务提供支持）"""
    
    def __init__(self, spatial_engine):
        self.spatial_engine = spatial_engine
    
    def locate(self, object_name: str) -> Dict:
        """定位物体"""
        # 从空间引擎查询物体位置
        result = self.spatial_engine.query(f'{object_name}在哪')
        
        # 模拟位置数据（实际应从CAD解析结果获取）
        mock_positions = {
            '沙发': {'room': '客厅', 'x': 3.5, 'y': 2.0, 'z': 0.0},
            '桌子': {'room': '餐厅', 'x': 6.0, 'y': 4.0, 'z': 0.0},
            '床': {'room': '主卧', 'x': 8.0, 'y': 3.0, 'z': 0.0},
            '椅子': {'room': '书房', 'x': 10.0, 'y': 2.0, 'z': 0.0},
        }
        
        position = mock_positions.get(object_name, {'room': '未知', 'x': 0, 'y': 0, 'z': 0})
        
        return {
            'object': object_name,
            'position': position,
            'confidence': 0.85 if object_name in mock_positions else 0.3
        }
    
    def find_path(self, start: Dict, end: Dict) -> Dict:
        """规划路径（简化版A*）"""
        # 简化：返回直线路径
        path = [
            {'x': start['x'], 'y': start['y'], 'z': 0},
            {'x': (start['x'] + end['x']) / 2, 'y': (start['y'] + end['y']) / 2, 'z': 0},
            {'x': end['x'], 'y': end['y'], 'z': 0}
        ]
        
        distance = ((end['x'] - start['x'])**2 + (end['y'] - start['y'])**2)**0.5
        
        return {
            'path': path,
            'distance': round(distance, 2),
            'estimated_time': round(distance / 0.5, 1),  # 假设0.5m/s
            'obstacles': []
        }

# ============== 改进4：真实数据连接器 ==============

class RealDataConnector:
    """真实数据连接器（连接CAD解析结果）"""
    
    def __init__(self):
        self.building_objects = []
        self.scene_graph = {}
        self.walls = {}
        self.doors = []
        self.windows = []
        self.load_data()
    
    def load_data(self):
        """加载真实数据"""
        # 尝试加载building_objects.json
        data_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\building_objects.json")
        if data_path.exists():
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.building_objects = json.load(f)
                print(f"[数据连接器] 加载 {len(self.building_objects)} 个建筑对象")
            except Exception as e:
                print(f"[数据连接器] 加载building_objects失败: {e}")
        
        # 尝试加载场景图
        scene_path = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\clean\scene_graph_real.json")
        if scene_path.exists():
            try:
                with open(scene_path, 'r', encoding='utf-8') as f:
                    self.scene_graph = json.load(f)
                print(f"[数据连接器] 加载场景图: {len(self.scene_graph.get('nodes', []))} 节点")
            except Exception as e:
                print(f"[数据连接器] 加载场景图失败: {e}")
        
        # 提取墙体信息
        self._extract_walls()
    
    def _extract_walls(self):
        """从建筑对象中提取墙体"""
        for obj in self.building_objects:
            obj_type = obj.get('type', '').lower()
            if 'door' in obj_type:
                self.doors.append(obj)
            elif 'window' in obj_type:
                self.windows.append(obj)
        
        # 模拟墙体数据（实际应从CAD解析）
        self.walls = {
            'north': {'type': 'load_bearing', 'thickness': 24, 'material': 'concrete'},
            'south': {'type': 'non_load_bearing', 'thickness': 12, 'material': 'brick'},
            'east': {'type': 'partition', 'thickness': 10, 'material': 'gypsum'},
            'west': {'type': 'non_load_bearing', 'thickness': 15, 'material': 'aerated_concrete'},
        }
    
    def get_wall_info(self, wall_side: str) -> Optional[Dict]:
        """获取墙体信息"""
        return self.walls.get(wall_side.lower())
    
    def get_object_count(self) -> Dict:
        """获取对象统计"""
        return {
            'total': len(self.building_objects),
            'doors': len(self.doors),
            'windows': len(self.windows)
        }

# ============== 主Agent ==============

class BuildingCognitiveAgent:
    """建筑认知主Agent（v2改进版）"""

    def __init__(self):
        self.spatial_engine = SpatialQueryEngineV2()
        self.constraint_engine = ConstraintEngine()
        self.execution_engine = ExecutionEngine()
        
        # 新增组件
        self.classifier = TaskClassifier()
        self.wall_extractor = WallDirectionExtractor()
        self.object_locator = ObjectLocator(self.spatial_engine)
        self.data_connector = RealDataConnector()
        
        print("[主Agent v2] 初始化完成")
        print(f"  - 数据统计: {self.data_connector.get_object_count()}")

    def process(self, instruction: str) -> TaskResult:
        """处理用户指令"""
        print(f"\n[主Agent] 收到指令: {instruction}")

        # 1. 任务类型识别（改进版）
        task_type = self.classifier.classify(instruction)
        print(f"[主Agent] 任务类型: {task_type}")

        # 2. 任务拆解
        subtasks = self._decompose_task(task_type, instruction)
        print(f"[主Agent] 子任务: {len(subtasks)}个")

        # 3. 执行子任务
        results = []
        for subtask in subtasks:
            agent = subtask['agent']
            action = subtask['action']
            params = subtask.get('params', {})

            print(f"[主Agent] 调用 {agent}.{action}")
            result = self._call_agent(agent, action, params)
            results.append(result)

            # 如果关键步骤失败，提前终止
            if not result.success and subtask.get('critical', False):
                error_msg = '操作被拒绝'
                if agent == 'constraint' and result.result.get('warnings'):
                    error_msg = result.result['warnings'][0]
                if result.result.get('suggestions'):
                    suggestions_list = result.result['suggestions']
                else:
                    suggestions_list = ['请检查输入参数', '联系技术支持']
                
                return TaskResult(
                    status='error',
                    summary=error_msg,
                    subtask_results=results,
                    execution_plan=None,
                    risk_level='high',
                    suggestions=suggestions_list
                )

        # 4. 整合结果
        status = 'success' if all(r.success for r in results) else 'warning'
        summary = self._generate_summary(results)
        risk_level = self._assess_risk(results)

        # 5. 生成执行方案
        exec_plan = None
        if task_type in ['drill', 'move', 'clean']:
            exec_params = self._extract_exec_params(results, task_type)
            exec_plan_obj = self.execution_engine.generate_plan(task_type, exec_params)
            exec_plan = {
                'steps': [asdict(s) for s in exec_plan_obj.steps],
                'tools': exec_plan_obj.tools,
                'safety': exec_plan_obj.safety,
                'estimated_time': exec_plan_obj.estimated_time
            }

        return TaskResult(
            status=status,
            summary=summary,
            subtask_results=results,
            execution_plan=exec_plan,
            risk_level=risk_level,
            suggestions=self._generate_suggestions(results)
        )

    def _decompose_task(self, task_type: str, instruction: str) -> List[Dict]:
        """任务拆解（改进版）"""
        if task_type == 'drill':
            wall_side = self.wall_extractor.extract(instruction)
            return [
                {'agent': 'spatial', 'action': 'locate_wall', 'params': {'instruction': instruction, 'wall_side': wall_side}, 'critical': True},
                {'agent': 'constraint', 'action': 'check_drill', 'params': {'instruction': instruction, 'wall_side': wall_side}, 'critical': True},
                {'agent': 'execution', 'action': 'generate_plan', 'params': {'task_type': 'drill'}, 'critical': False},
            ]
        elif task_type == 'move':
            # 提取物体名称和目标位置
            object_name = self._extract_object_name(instruction)
            target_location = self._extract_target_location(instruction)
            
            return [
                {'agent': 'spatial', 'action': 'locate_object', 'params': {'object_name': object_name}, 'critical': True},
                {'agent': 'spatial', 'action': 'locate_target', 'params': {'location': target_location}, 'critical': True},
                {'agent': 'spatial', 'action': 'find_path', 'params': {'instruction': instruction}, 'critical': False},
                {'agent': 'constraint', 'action': 'check_move', 'params': {'object_name': object_name}, 'critical': False},
                {'agent': 'execution', 'action': 'generate_plan', 'params': {'task_type': 'move'}, 'critical': False},
            ]
        else:
            return [
                {'agent': 'spatial', 'action': 'query', 'params': {'query': instruction}, 'critical': False},
            ]
    
    def _extract_object_name(self, instruction: str) -> str:
        """提取物体名称"""
        common_objects = ['沙发', '桌子', '床', '椅子', '柜子', '书架', '电视', '冰箱']
        for obj in common_objects:
            if obj in instruction:
                return obj
        return '未知物体'
    
    def _extract_target_location(self, instruction: str) -> str:
        """提取目标位置"""
        common_locations = ['卧室', '客厅', '书房', '厨房', '阳台', '卫生间']
        for loc in common_locations:
            if loc in instruction:
                return loc
        return '未知位置'

    def _call_agent(self, agent: str, action: str, params: Dict) -> AgentResult:
        """调用子Agent（改进版）"""
        try:
            if agent == 'spatial':
                if action == 'query':
                    result = self.spatial_engine.query(params.get('query', ''))
                    return AgentResult(
                        agent='空间理解',
                        success=True,
                        result={'answer': result.answer_text, 'data': result.spatial_data},
                        confidence=result.confidence
                    )
                elif action == 'locate_wall':
                    wall_side = params.get('wall_side', 'unknown')
                    result = self.spatial_engine.query(f'{wall_side}墙的位置')
                    return AgentResult(
                        agent='空间理解',
                        success=True,
                        result={'wall_side': wall_side, 'position': result.spatial_data},
                        confidence=0.85
                    )
                elif action == 'locate_object':
                    object_name = params.get('object_name', '未知物体')
                    location = self.object_locator.locate(object_name)
                    return AgentResult(
                        agent='空间理解',
                        success=True,
                        result={'object': object_name, 'position': location},
                        confidence=location['confidence']
                    )
                elif action == 'locate_target':
                    location = params.get('location', '未知位置')
                    # 模拟目标位置
                    mock_locations = {
                        '卧室': {'x': 8.0, 'y': 3.0, 'z': 0},
                        '客厅': {'x': 3.5, 'y': 2.0, 'z': 0},
                        '书房': {'x': 10.0, 'y': 2.0, 'z': 0},
                    }
                    pos = mock_locations.get(location, {'x': 5.0, 'y': 5.0, 'z': 0})
                    return AgentResult(
                        agent='空间理解',
                        success=True,
                        result={'location': location, 'position': pos},
                        confidence=0.85
                    )
                elif action == 'find_path':
                    # 从之前的结果中获取起点和终点
                    # 这里简化处理
                    start = {'x': 3.5, 'y': 2.0, 'z': 0}
                    end = {'x': 8.0, 'y': 3.0, 'z': 0}
                    path = self.object_locator.find_path(start, end)
                    return AgentResult(
                        agent='空间理解',
                        success=True,
                        result=path,
                        confidence=0.8
                    )

            elif agent == 'constraint':
                if action == 'check_drill':
                    instruction = params.get('instruction', '')
                    wall_side = params.get('wall_side', 'unknown')
                    
                    # 使用改进的墙体方向提取
                    if wall_side == 'unknown':
                        wall_side = self.wall_extractor.extract(instruction)
                    
                    diameter = 8  # 默认
                    depth = 5  # 默认

                    result = self.constraint_engine.check_drill(wall_side, diameter, depth)
                    return AgentResult(
                        agent='操作约束',
                        success=result.allowed,
                        result={'allowed': result.allowed, 'checks': result.checks, 'warnings': result.warnings, 'suggestions': result.suggestions},
                        confidence=0.9 if result.allowed else 0.95
                    )
                elif action == 'check_move':
                    object_name = params.get('object_name', '未知物体')
                    result = self.constraint_engine.check_move(object_name, [])
                    return AgentResult(
                        agent='操作约束',
                        success=result.allowed,
                        result={'allowed': result.allowed, 'checks': result.checks, 'warnings': result.warnings},
                        confidence=0.85
                    )

            elif agent == 'execution':
                if action == 'generate_plan':
                    task_type = params.get('task_type', 'drill')
                    plan = self.execution_engine.generate_plan(task_type, params)
                    return AgentResult(
                        agent='执行',
                        success=True,
                        result={'plan': asdict(plan)},
                        confidence=0.85
                    )

            return AgentResult(agent=agent, success=False, result={'error': '未知动作'}, confidence=0.0)

        except Exception as e:
            return AgentResult(agent=agent, success=False, result={'error': str(e)}, confidence=0.0)

    def _generate_summary(self, results: List[AgentResult]) -> str:
        """生成摘要"""
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)

        if success_count == total_count:
            return f'任务分析完成，所有{total_count}个子任务执行成功'
        else:
            return f'任务分析完成，{success_count}/{total_count}个子任务成功'

    def _assess_risk(self, results: List[AgentResult]) -> str:
        """风险评估"""
        for r in results:
            if r.agent == '操作约束' and not r.success:
                return 'high'
            if r.agent == '操作约束' and r.result.get('warnings'):
                return 'medium'
        return 'low'

    def _extract_exec_params(self, results: List[AgentResult], task_type: str) -> Dict:
        """提取执行参数"""
        params = {'diameter': 8, 'depth': 5, 'wall_side': 'east'}
        
        for r in results:
            if r.agent == '空间理解':
                if 'wall_side' in r.result:
                    params['wall_side'] = r.result['wall_side']
                if 'path' in r.result:
                    params['path'] = r.result['path']
                    params['distance'] = r.result.get('distance', 0)
            if r.agent == '操作约束':
                params['diameter'] = r.result.get('checks', {}).get('requested_diameter', 8)
                params['depth'] = r.result.get('checks', {}).get('requested_depth', 5)
        
        return params

    def _generate_suggestions(self, results: List[AgentResult]) -> List[str]:
        """生成建议"""
        suggestions = []
        for r in results:
            if r.agent == '操作约束' and r.result.get('suggestions'):
                suggestions.extend(r.result['suggestions'])
        if not suggestions:
            suggestions.append('任务可执行，请按方案操作')
        return suggestions[:5]

# ============== CLI入口 ==============

if __name__ == "__main__":
    print("=" * 60)
    print("建筑认知主Agent v2 - 改进版")
    print("=" * 60)

    agent = BuildingCognitiveAgent()

    # 测试案例
    test_cases = [
        "在东墙钻一个8mm的孔",
        "能不能在北墙钻孔",  # 应该被拒绝
        "把沙发搬到卧室",     # 搬运任务
        "在墙上打个孔",       # 应该识别为钻孔
        "移动沙发到书房",     # 搬运任务
    ]

    for instruction in test_cases:
        print(f"\n{'=' * 60}")
        result = agent.process(instruction)

        print(f"\n[结果]")
        print(f"状态: {result.status}")
        print(f"摘要: {result.summary}")
        print(f"风险: {result.risk_level}")

        print(f"\n[子任务结果]")
        for sr in result.subtask_results:
            status = "OK" if sr.success else "FAIL"
            print(f"  [{status}] {sr.agent}: 置信度 {sr.confidence:.0%}")

        if result.execution_plan:
            print(f"\n[执行方案]")
            print(f"  步骤数: {len(result.execution_plan['steps'])}")
            print(f"  预计时间: {result.execution_plan['estimated_time']}")
            print(f"  所需工具: {', '.join(t['name'] for t in result.execution_plan['tools'])}")

        print(f"\n[建议]")
        for s in result.suggestions:
            print(f"  - {s}")
