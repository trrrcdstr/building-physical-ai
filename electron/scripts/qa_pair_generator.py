"""
训练数据生成器 - QA Pairs
将CAD图纸、VR效果图和物理规则整理成问答对

数据源：
1. CAD图纸 → 墙体位置、门窗位置、管线位置
2. VR效果图 → 房间布局、家具位置
3. 物理规则 → 钻孔约束、搬运约束

输出格式：
{
  "id": "qa_001",
  "category": "wall_type",
  "question": "东墙是什么类型的墙？",
  "answer": "东墙是隔墙，厚度10cm，材质为石膏板。",
  "metadata": {...}
}
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

# ============== 数据结构 ==============

@dataclass
class QAPair:
    """问答对"""
    id: str
    category: str  # wall_type, drill_constraint, object_location, path_planning
    question: str
    answer: str
    metadata: Dict[str, Any]
    source: str  # cad, vr, rule, synthetic

# ============== 知识库（模拟真实数据） ==============

# 墙体知识（来自CAD解析）
WALL_KNOWLEDGE = {
    "north": {
        "type": "load_bearing",
        "thickness_cm": 24,
        "material": "concrete",
        "has_pipes": True,
        "pipes": [
            {"type": "electrical", "depth_cm": 15, "from_floor_cm": 30},
            {"type": "water", "depth_cm": 10, "from_floor_cm": 50}
        ]
    },
    "south": {
        "type": "non_load_bearing",
        "thickness_cm": 12,
        "material": "brick",
        "has_pipes": True,
        "pipes": [
            {"type": "electrical", "depth_cm": 15, "from_floor_cm": 30}
        ]
    },
    "east": {
        "type": "partition",
        "thickness_cm": 10,
        "material": "gypsum",
        "has_pipes": False,
        "pipes": []
    },
    "west": {
        "type": "non_load_bearing",
        "thickness_cm": 15,
        "material": "aerated_concrete",
        "has_pipes": True,
        "pipes": [
            {"type": "electrical", "depth_cm": 15, "from_floor_cm": 30},
            {"type": "gas", "depth_cm": 30, "from_floor_cm": 120}
        ]
    }
}

# 物体知识（来自VR解析）
OBJECT_KNOWLEDGE = {
    "沙发": {"room": "客厅", "weight_kg": 45, "size": "large", "movable": True},
    "茶几": {"room": "客厅", "weight_kg": 15, "size": "medium", "movable": True},
    "床": {"room": "主卧", "weight_kg": 80, "size": "large", "movable": False},
    "书桌": {"room": "书房", "weight_kg": 25, "size": "medium", "movable": True},
    "冰箱": {"room": "厨房", "weight_kg": 60, "size": "large", "movable": True},
    "电视": {"room": "客厅", "weight_kg": 15, "size": "medium", "movable": True},
    "衣柜": {"room": "主卧", "weight_kg": 100, "size": "large", "movable": False},
    "餐桌": {"room": "餐厅", "weight_kg": 30, "size": "medium", "movable": True}
}

# 房间知识（来自VR/CAD）
ROOM_KNOWLEDGE = {
    "客厅": {"area_m2": 25, "floor": "瓷砖", "has_window": True},
    "主卧": {"area_m2": 18, "floor": "木地板", "has_window": True},
    "书房": {"area_m2": 12, "floor": "木地板", "has_window": True},
    "厨房": {"area_m2": 8, "floor": "瓷砖", "has_window": False},
    "餐厅": {"area_m2": 10, "floor": "瓷砖", "has_window": True},
    "卫生间": {"area_m2": 6, "floor": "瓷砖", "has_window": False}
}

# 钻孔规则（来自物理规则库）
DRILL_RULES = {
    "load_bearing": {
        "allowed": False,
        "reason": "承重墙钻孔可能影响建筑结构安全",
        "exception": "必须由专业结构工程师评估审批"
    },
    "non_load_bearing": {
        "allowed": True,
        "max_diameter_cm": 10,
        "max_depth_cm": 8,
        "warnings": ["建议使用探测仪确认墙内无隐蔽管线"]
    },
    "partition": {
        "allowed": True,
        "max_diameter_cm": 15,
        "max_depth_cm": 8,
        "warnings": ["隔墙较薄，注意钻孔深度"]
    }
}

# 管线安全距离
PIPE_SAFETY_DISTANCE = {
    "electrical": 15,  # cm
    "water": 10,
    "gas": 30
}

# ============== QA生成器 ==============

class QAPairGenerator:
    """问答对生成器"""
    
    def __init__(self):
        self.qa_pairs: List[QAPair] = []
        self.id_counter = 0
    
    def _generate_id(self) -> str:
        self.id_counter += 1
        return f"qa_{self.id_counter:04d}"
    
    # ============== 墙体类型问答 ==============
    
    def generate_wall_type_qa(self) -> List[QAPair]:
        """生成墙体类型问答"""
        pairs = []
        
        wall_names = {
            "north": "北墙", "south": "南墙", 
            "east": "东墙", "west": "西墙"
        }
        
        wall_types_cn = {
            "load_bearing": "承重墙",
            "non_load_bearing": "非承重墙",
            "partition": "隔墙"
        }
        
        for wall_id, wall_data in WALL_KNOWLEDGE.items():
            wall_name = wall_names[wall_id]
            wall_type_cn = wall_types_cn[wall_data["type"]]
            
            # Q1: 墙体类型
            q = f"{wall_name}是什么类型的墙？"
            a = f"{wall_name}是{wall_type_cn}，厚度{wall_data['thickness_cm']}cm，材质为{wall_data['material']}。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="wall_type",
                question=q,
                answer=a,
                metadata={"wall_id": wall_id, "wall_data": wall_data},
                source="cad"
            ))
            
            # Q2: 墙体厚度
            q = f"{wall_name}有多厚？"
            a = f"{wall_name}厚度为{wall_data['thickness_cm']}cm。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="wall_dimension",
                question=q,
                answer=a,
                metadata={"wall_id": wall_id},
                source="cad"
            ))
            
            # Q3: 墙体材质
            q = f"{wall_name}是什么材质的？"
            a = f"{wall_name}材质为{wall_data['material']}。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="wall_material",
                question=q,
                answer=a,
                metadata={"wall_id": wall_id},
                source="cad"
            ))
        
        return pairs
    
    # ============== 钻孔约束问答 ==============
    
    def generate_drill_constraint_qa(self) -> List[QAPair]:
        """生成钻孔约束问答"""
        pairs = []
        
        wall_names = {
            "north": "北墙", "south": "南墙",
            "east": "东墙", "west": "西墙"
        }
        
        for wall_id, wall_data in WALL_KNOWLEDGE.items():
            wall_name = wall_names[wall_id]
            rule = DRILL_RULES[wall_data["type"]]
            
            # Q1: 能否钻孔
            q = f"能在{wall_name}钻孔吗？"
            if not rule["allowed"]:
                a = f"不能。{wall_name}是承重墙，{rule['reason']}。如确需钻孔，{rule['exception']}。"
            else:
                a = f"可以。{wall_name}是{'非承重墙' if wall_data['type'] == 'non_load_bearing' else '隔墙'}，"
                a += f"最大钻孔直径{rule['max_diameter_cm']}cm，深度{rule['max_depth_cm']}cm。"
                if rule.get("warnings"):
                    a += f"注意：{rule['warnings'][0]}。"
            
            pairs.append(QAPair(
                id=self._generate_id(),
                category="drill_constraint",
                question=q,
                answer=a,
                metadata={"wall_id": wall_id, "allowed": rule["allowed"]},
                source="rule"
            ))
            
            # Q2: 钻孔参数限制
            if rule["allowed"]:
                q = f"{wall_name}最大能钻多大的孔？"
                a = f"{wall_name}最大钻孔直径{rule['max_diameter_cm']}cm，深度{rule['max_depth_cm']}cm。"
                pairs.append(QAPair(
                    id=self._generate_id(),
                    category="drill_parameter",
                    question=q,
                    answer=a,
                    metadata={"wall_id": wall_id},
                    source="rule"
                ))
            
            # Q3: 管线安全
            if wall_data["has_pipes"]:
                q = f"{wall_name}里有管线吗？"
                pipe_types = [p["type"] for p in wall_data["pipes"]]
                pipe_types_cn = {"electrical": "电线管", "water": "水管", "gas": "燃气管"}
                pipe_list = "、".join([pipe_types_cn.get(t, t) for t in pipe_types])
                a = f"是的，{wall_name}内有{pipe_list}。钻孔前请先使用探测仪定位管线位置。"
                pairs.append(QAPair(
                    id=self._generate_id(),
                    category="pipe_location",
                    question=q,
                    answer=a,
                    metadata={"wall_id": wall_id, "pipes": wall_data["pipes"]},
                    source="cad"
                ))
        
        return pairs
    
    # ============== 物体定位问答 ==============
    
    def generate_object_location_qa(self) -> List[QAPair]:
        """生成物体定位问答"""
        pairs = []
        
        for obj_name, obj_data in OBJECT_KNOWLEDGE.items():
            # Q1: 物体位置
            q = f"{obj_name}在哪个房间？"
            a = f"{obj_name}在{obj_data['room']}。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="object_location",
                question=q,
                answer=a,
                metadata={"object": obj_name, "room": obj_data['room']},
                source="vr"
            ))
            
            # Q2: 物体重量
            q = f"{obj_name}有多重？"
            a = f"{obj_name}重量约{obj_data['weight_kg']}kg。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="object_weight",
                question=q,
                answer=a,
                metadata={"object": obj_name, "weight": obj_data['weight_kg']},
                source="vr"
            ))
            
            # Q3: 能否移动
            movable_text = "可以" if obj_data["movable"] else "不建议"
            q = f"{obj_name}能移动吗？"
            a = f"{movable_text}移动{obj_name}。"
            if not obj_data["movable"]:
                a += f"因为{obj_name}较重（{obj_data['weight_kg']}kg）且体积大，建议使用专业搬运工具。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="object_mobility",
                question=q,
                answer=a,
                metadata={"object": obj_name, "movable": obj_data["movable"]},
                source="rule"
            ))
        
        return pairs
    
    # ============== 路径规划问答 ==============
    
    def generate_path_planning_qa(self) -> List[QAPair]:
        """生成路径规划问答"""
        pairs = []
        
        # 从客厅到其他房间
        rooms = list(ROOM_KNOWLEDGE.keys())
        distances = {
            ("客厅", "主卧"): 8.5,
            ("客厅", "书房"): 6.2,
            ("客厅", "厨房"): 4.0,
            ("客厅", "餐厅"): 3.5,
            ("客厅", "卫生间"): 5.8
        }
        
        for (start, end), dist in distances.items():
            # Q: 搬运距离
            q = f"从{start}到{end}有多远？"
            a = f"从{start}到{end}的直线距离约{dist}米。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="path_distance",
                question=q,
                answer=a,
                metadata={"start": start, "end": end, "distance": dist},
                source="cad"
            ))
            
            # Q: 搬运时间
            time_min = dist / 0.5  # 假设0.5m/s
            q = f"搬运物体从{start}到{end}需要多久？"
            a = f"从{start}到{end}约需{time_min:.1f}秒（假设移动速度0.5m/s）。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="path_time",
                question=q,
                answer=a,
                metadata={"start": start, "end": end, "time": time_min},
                source="synthetic"
            ))
        
        return pairs
    
    # ============== 房间信息问答 ==============
    
    def generate_room_info_qa(self) -> List[QAPair]:
        """生成房间信息问答"""
        pairs = []
        
        for room_name, room_data in ROOM_KNOWLEDGE.items():
            # Q1: 房间面积
            q = f"{room_name}有多大？"
            a = f"{room_name}面积约{room_data['area_m2']}平方米。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="room_area",
                question=q,
                answer=a,
                metadata={"room": room_name, "area": room_data['area_m2']},
                source="cad"
            ))
            
            # Q2: 地板材质
            q = f"{room_name}是什么地板？"
            a = f"{room_name}地板材质为{room_data['floor']}。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="room_floor",
                question=q,
                answer=a,
                metadata={"room": room_name, "floor": room_data['floor']},
                source="vr"
            ))
            
            # Q3: 有无窗户
            has_window = "有" if room_data["has_window"] else "没有"
            q = f"{room_name}有窗户吗？"
            a = f"{room_name}{has_window}窗户。"
            pairs.append(QAPair(
                id=self._generate_id(),
                category="room_window",
                question=q,
                answer=a,
                metadata={"room": room_name, "has_window": room_data['has_window']},
                source="vr"
            ))
        
        return pairs
    
    # ============== 组合任务问答 ==============
    
    def generate_complex_task_qa(self) -> List[QAPair]:
        """生成复杂任务问答（多步骤推理）"""
        pairs = []
        
        # 任务1: 搬运沙发
        q = "把沙发搬到主卧，需要怎么做？"
        a = "将沙发从客厅搬到主卧，步骤如下：\n"
        a += "1. 确认沙发重量约45kg，需要2人搬运\n"
        a += "2. 规划路径：客厅→走廊→主卧，距离约8.5米\n"
        a += "3. 搬运时间约17秒\n"
        a += "4. 注意事项：避免碰撞走廊墙壁，主卧地板为木地板需轻放"
        pairs.append(QAPair(
            id=self._generate_id(),
            category="complex_task",
            question=q,
            answer=a,
            metadata={"task": "move_sofa", "steps": 4},
            source="synthetic"
        ))
        
        # 任务2: 东墙钻孔
        q = "在东墙钻一个8mm的孔，需要注意什么？"
        a = "在东墙钻孔的步骤如下：\n"
        a += "1. 东墙是隔墙，厚度10cm，允许钻孔\n"
        a += "2. 最大钻孔直径15cm，深度8cm，8mm孔径符合要求\n"
        a += "3. 东墙内无管线，相对安全\n"
        a += "4. 建议钻孔深度控制在5cm以内（隔墙较薄）\n"
        a += "5. 准备工具：电钻、8mm钻头、护目镜"
        pairs.append(QAPair(
            id=self._generate_id(),
            category="complex_task",
            question=q,
            answer=a,
            metadata={"task": "drill_east_wall", "steps": 5},
            source="synthetic"
        ))
        
        # 任务3: 北墙钻孔（拒绝案例）
        q = "我想在北墙打一个孔挂电视，可以吗？"
        a = "不建议在北墙钻孔。原因如下：\n"
        a += "1. 北墙是承重墙，厚度24cm，材质为混凝土\n"
        a += "2. 承重墙钻孔可能影响建筑结构安全\n"
        a += "3. 北墙内有电线管和水管，钻孔有损坏风险\n"
        a += "建议：选择南墙或东墙挂电视，如必须在北墙操作，请联系专业结构工程师评估。"
        pairs.append(QAPair(
            id=self._generate_id(),
            category="complex_task",
            question=q,
            answer=a,
            metadata={"task": "drill_north_wall", "allowed": False},
            source="synthetic"
        ))
        
        return pairs
    
    # ============== 生成全部问答 ==============
    
    def generate_all(self) -> List[QAPair]:
        """生成全部问答对"""
        all_pairs = []
        
        print("[QA生成器] 开始生成问答对...")
        
        # 1. 墙体类型
        pairs = self.generate_wall_type_qa()
        all_pairs.extend(pairs)
        print(f"  - 墙体类型: {len(pairs)} 条")
        
        # 2. 钻孔约束
        pairs = self.generate_drill_constraint_qa()
        all_pairs.extend(pairs)
        print(f"  - 钻孔约束: {len(pairs)} 条")
        
        # 3. 物体定位
        pairs = self.generate_object_location_qa()
        all_pairs.extend(pairs)
        print(f"  - 物体定位: {len(pairs)} 条")
        
        # 4. 路径规划
        pairs = self.generate_path_planning_qa()
        all_pairs.extend(pairs)
        print(f"  - 路径规划: {len(pairs)} 条")
        
        # 5. 房间信息
        pairs = self.generate_room_info_qa()
        all_pairs.extend(pairs)
        print(f"  - 房间信息: {len(pairs)} 条")
        
        # 6. 复杂任务
        pairs = self.generate_complex_task_qa()
        all_pairs.extend(pairs)
        print(f"  - 复杂任务: {len(pairs)} 条")
        
        print(f"\n[QA生成器] 总计: {len(all_pairs)} 条问答对")
        
        return all_pairs
    
    def save_to_json(self, pairs: List[QAPair], output_path: str):
        """保存为JSON文件"""
        data = {
            "metadata": {
                "total": len(pairs),
                "categories": list(set(p.category for p in pairs)),
                "sources": list(set(p.source for p in pairs))
            },
            "qa_pairs": [asdict(p) for p in pairs]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[QA生成器] 已保存到: {output_path}")

# ============== 主函数 ==============

if __name__ == "__main__":
    generator = QAPairGenerator()
    qa_pairs = generator.generate_all()
    
    # 保存到文件
    output_dir = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\training")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "qa_pairs_v1.json"
    generator.save_to_json(qa_pairs, str(output_path))
    
    # 打印示例
    print("\n" + "=" * 60)
    print("示例问答对:")
    print("=" * 60)
    
    for i, qa in enumerate(qa_pairs[:5]):
        print(f"\n[{qa.id}] {qa.category}")
        print(f"Q: {qa.question}")
        print(f"A: {qa.answer}")
