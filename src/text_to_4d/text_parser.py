"""
文本→场景描述解析器

将自然语言描述转换为结构化场景表示
"""

from dataclasses import dataclass
from typing import List, Optional
import json
import re


@dataclass
class Object:
    """场景中的物体"""
    type: str           # person, sofa, table, cup, etc.
    position: str       # relative position description
    action: Optional[str] = None  # current action
    attributes: dict = None       # additional attributes


@dataclass 
class Relation:
    """物体间关系"""
    subject: str        # subject object id
    relation: str       # spatial/temporal relation
    object: str         # object id


@dataclass
class Action:
    """时序动作"""
    actor: str          # actor object id
    action: str         # action type
    start_time: float   # start time in seconds
    end_time: float     # end time in seconds
    parameters: dict = None  # action parameters


@dataclass
class SceneDescription:
    """完整的场景描述"""
    room: str                   # room type
    objects: List[Object]       # objects in scene
    relations: List[Relation]   # object relations
    actions: List[Action]       # temporal actions
    duration: float             # total duration in seconds
    style: str = "modern"       # design style
    lighting: str = "natural"   # lighting condition


class TextToSceneParser:
    """
    文本→场景描述解析器
    
    示例:
        parser = TextToSceneParser()
        scene = parser.parse("客厅里有人在沙发上喝茶")
        # scene.room = "客厅"
        # scene.objects = [Object(type="person", position="on_sofa"), ...]
    """
    
    # 房间类型映射
    ROOM_TYPES = {
        "客厅": "living_room",
        "卧室": "bedroom", 
        "厨房": "kitchen",
        "餐厅": "dining_room",
        "书房": "study",
        "卫生间": "bathroom",
        "阳台": "balcony",
        "花园": "garden",
        "园林": "landscape",
    }
    
    # 物体类型映射
    OBJECT_TYPES = {
        "人": "person",
        "沙发": "sofa",
        "桌子": "table",
        "椅子": "chair",
        "床": "bed",
        "柜": "cabinet",
        "灯": "lamp",
        "电视": "tv",
        "茶": "tea",
        "杯": "cup",
        "书": "book",
        "花": "flower",
        "树": "tree",
    }
    
    # 动作映射
    ACTION_TYPES = {
        "坐": "sit",
        "站": "stand",
        "走": "walk",
        "喝茶": "drink_tea",
        "看书": "read",
        "睡觉": "sleep",
        "做饭": "cook",
        "浇水": "water",
    }
    
    def __init__(self, llm_client=None):
        """
        初始化解析器
        
        Args:
            llm_client: LLM客户端（可选，用于复杂场景解析）
        """
        self.llm_client = llm_client
    
    def parse(self, text: str) -> SceneDescription:
        """
        解析文本为场景描述
        
        Args:
            text: 自然语言描述，如"客厅里有人在沙发上喝茶"
            
        Returns:
            SceneDescription: 结构化场景描述
        """
        # 1. 提取房间类型
        room = self._extract_room(text)
        
        # 2. 提取物体
        objects = self._extract_objects(text)
        
        # 3. 提取关系
        relations = self._extract_relations(text, objects)
        
        # 4. 提取动作
        actions = self._extract_actions(text, objects)
        
        # 5. 估计时长
        duration = self._estimate_duration(actions)
        
        return SceneDescription(
            room=room,
            objects=objects,
            relations=relations,
            actions=actions,
            duration=duration
        )
    
    def _extract_room(self, text: str) -> str:
        """提取房间类型"""
        for cn, en in self.ROOM_TYPES.items():
            if cn in text:
                return en
        return "unknown"
    
    def _extract_objects(self, text: str) -> List[Object]:
        """提取物体"""
        objects = []
        
        for cn, en in self.OBJECT_TYPES.items():
            if cn in text:
                # 简单位置推断
                position = self._infer_position(text, cn)
                objects.append(Object(
                    type=en,
                    position=position,
                    attributes={"original_text": cn}
                ))
        
        return objects
    
    def _infer_position(self, text: str, obj: str) -> str:
        """推断物体位置"""
        # 简单规则：查找"在XX上/里/旁边"模式
        patterns = [
            rf"在(.{{1,10}}){obj}",
            rf"{obj}在(.{{1,10}})",
            rf"(.{{1,10}})上的{obj}",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return "unknown"
    
    def _extract_relations(self, text: str, objects: List[Object]) -> List[Relation]:
        """提取物体间关系"""
        relations = []
        
        # 简单规则：人在沙发上 → person on sofa
        if "在" in text and "上" in text:
            for i, obj1 in enumerate(objects):
                for j, obj2 in enumerate(objects):
                    if i != j:
                        if obj1.type == "person" and obj2.type == "sofa":
                            relations.append(Relation(
                                subject=f"obj_{i}",
                                relation="on",
                                object=f"obj_{j}"
                            ))
        
        return relations
    
    def _extract_actions(self, text: str, objects: List[Object]) -> List[Action]:
        """提取动作"""
        actions = []
        
        for cn, en in self.ACTION_TYPES.items():
            if cn in text:
                # 找到执行者（通常是"人"）
                actor_idx = next(
                    (i for i, o in enumerate(objects) if o.type == "person"),
                    0
                )
                actions.append(Action(
                    actor=f"obj_{actor_idx}",
                    action=en,
                    start_time=0.0,
                    end_time=3.0  # 默认3秒
                ))
        
        return actions
    
    def _estimate_duration(self, actions: List[Action]) -> float:
        """估计场景总时长"""
        if not actions:
            return 0.0
        return max(a.end_time for a in actions)
    
    def to_json(self, scene: SceneDescription) -> str:
        """转换为JSON格式"""
        return json.dumps({
            "room": scene.room,
            "objects": [
                {
                    "type": o.type,
                    "position": o.position,
                    "action": o.action,
                    "attributes": o.attributes
                }
                for o in scene.objects
            ],
            "relations": [
                {
                    "subject": r.subject,
                    "relation": r.relation,
                    "object": r.object
                }
                for r in scene.relations
            ],
            "actions": [
                {
                    "actor": a.actor,
                    "action": a.action,
                    "start_time": a.start_time,
                    "end_time": a.end_time
                }
                for a in scene.actions
            ],
            "duration": scene.duration
        }, ensure_ascii=False, indent=2)


# 测试
if __name__ == "__main__":
    parser = TextToSceneParser()
    
    # 测试用例
    test_cases = [
        "客厅里有人在沙发上喝茶",
        "卧室里有人在床上看书",
        "厨房里有人在做饭",
        "花园里有人在给花浇水",
    ]
    
    for text in test_cases:
        scene = parser.parse(text)
        print(f"\n输入: {text}")
        print(f"输出: {parser.to_json(scene)}")
