"""
强化学习训练数据 - 建筑场景世界模型
=====================================
用于机器人深度强化学习训练的建筑场景数据集

来源项目：
1. 从化别墅 - 716.3㎡别墅精装修
2. 佛山恒大云东海 - 云涧花园别墅区
3. 恒创睿能综合楼 - 商业办公空间

目标：构建可泛化的建筑物理世界模型，供机器人自主决策
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np


# ============================================================
# 1. 从化别墅 - 详细施工数据
# ============================================================

CONGHUA_VILLA = {
    "id": "proj-conghua-villa",
    "name": "从化别墅装修施工工程",
    "location": "广州市从化区",
    "area": 716.3,  # 平方米
    "type": "独栋别墅",
    "floors": 3,
    
    # 施工工艺规范
    "specifications": {
        "隔墙": {
            "type": "轻钢龙骨石膏板隔墙",
            "thickness": 100,  # mm
            "steel_frame": "1.0mm厚轻钢龙骨",
            "board": "双层双面9.5mm石膏板",
            "insulation": "岩棉1200×600×50, 容重60kg/m³"
        },
        "木质处理": {
            "fireproofing": "防火涂料三遍",
            "anticorrosion": "聚氨脂防腐涂料二遍",
            "wood_beam": "40×30mm杉木方, 间距300mm"
        },
        "吊顶": {
            "inspection_hole": "暗装检修孔450×450mm",
            "requirement": "所有裸露木制品刷防火涂料三遍"
        },
        "乳胶漆": {
            "process": "贴自粘胶带条贴缝 → 满刮腻子三遍 → 打磨平整 → ICI五合一环保乳胶漆底漆一遍 → 面漆二遍"
        },
        "实木地板": {
            "layers": [
                "1:2.5水泥砂浆找平层20厚",
                "界面剂一道",
                "双层9厚多层板(防火涂料三度)",
                "50×50木龙骨(间距400mm, 防腐防火剂)",
                "实木地板"
            ],
            "tolerance": "缝隙<1mm, 表面平整偏差≤1mm"
        }
    },
    
    # 空间布局
    "spaces": {
        "garden": {
            "name": "花园",
            "area": "室外",
            "features": ["覆土", "绿植", "景观"]
        },
        "living": {
            "name": "客厅",
            "floor_area": 16000,  # mm x 1550mm 初步估算
            "features": ["挑高", "楼梯连通"]
        },
        "bedroom": {
            "name": "卧室",
            "typical_size": "5400×5700mm",
            "features": ["飘窗", "衣柜区"]
        },
        "kitchen": {
            "name": "厨房",
            "features": ["操作台", "橱柜"]
        },
        "bathroom": {
            "name": "卫生间",
            "features": ["淋浴", "洗漱", "马桶"]
        }
    },
    
    # 材料规格
    "materials": {
        "stone": ["大理石", "花岗岩", "人造石"],
        "tile": ["瓷砖", "马赛克"],
        "wood": ["实木地板", "复合地板", "木饰面"],
        "metal": ["铝合金", "不锈钢"],
        "glass": ["钢化玻璃", "艺术玻璃"]
    }
}


# ============================================================
# 2. 佛山恒大云东海 - 云涧花园别墅区
# ============================================================

HENGDA_YUNDONGHAI = {
    "id": "proj-hengda-yundonghai",
    "name": "云涧花园别墅区",
    "developer": "恒大集团",
    "location": "佛山恒大云东海",
    "type": "联排/独栋别墅区",
    
    # 户型类型
    "unit_types": {
        "B型": {
            "total_area": 224.65,  # m²
            "ground_floor": 103.18,  # 首层
            "second_floor": 66.79,   # 二层
            "third_floor": 54.68,    # 三层
            "units": ["25-27座", "29座", "31座", "33座", "35座", "37座", "39座", "41-42座", "44座", "46座", "48座", "50-51座", "70座", "72座", "74座", "76座", "78座", "80座", "82座", "84-85座", "87-89座", "90座", "92座", "94座", "96座", "99座", "103座", "107座", "111座", "115座"]
        },
        "B'型": {
            "total_area": 225.92,
            "ground_floor": 107.46,
            "second_floor": 65.82,
            "third_floor": 52.64,
            "units": ["12-24座", "52-61座", "101座", "105座", "109座", "113座", "117座"]
        },
        "C型": {
            "total_area": 149.89,
            "ground_floor": 88.32,
            "second_floor": 61.57,
            "units": ["28座", "30座", "32座", "34座", "36座", "38座", "40座", "43座", "45座", "47座", "49座", "65座", "100座", "104座", "108座", "112座", "116座"]
        },
        "C'型": {
            "total_area": 157.7,
            "ground_floor": 90.82,
            "second_floor": 66.88,
            "units": ["62-64座", "66-69座", "71座", "73座", "75座", "77座", "79座", "81座", "83座", "86座", "91座", "93座", "95座", "97-98座", "102座", "106座", "110座", "114座", "118座"]
        }
    },
    
    # 公共设施
    "common_areas": ["综合楼", "商业街"],
    
    # 典型房间尺寸
    "room_templates": {
        "客厅": {"min_area": 20, "max_area": 50},
        "卧室": {"min_area": 12, "max_area": 25},
        "厨房": {"min_area": 8, "max_area": 15},
        "卫生间": {"min_area": 4, "max_area": 10},
        "阳台": {"min_area": 5, "max_area": 15}
    }
}


# ============================================================
# 3. 恒创睿能综合楼 - 商业办公空间
# ============================================================

HENGCHUANG_RUINENG = {
    "id": "proj-hengchuang-ruineng",
    "name": "恒创睿能综合楼室内设计",
    "type": "商业办公综合体",
    "floors": 3,
    
    "spaces": {
        "1F": {
            "name": "一层",
            "zones": [
                {"name": "门厅", "area": "约100m²", "features": ["玻璃感应推拉门", "Logo背景墙"]},
                {"name": "展厅", "area": "约200m²", "features": ["岩板背景", "LED发光条", "烤漆玻璃"]},
                {"name": "大会议室", "area": "约80m²", "features": ["投影幕布", "透光灯膜", "墙布硬包"]},
                {"name": "卫生间", "features": ["防滑瓷砖", "成品隔断", "石材台面"]},
                {"name": "门头", "features": ["灰色铝板", "木纹铝通", "石材门套", "米色铝板"]}
            ]
        },
        "2F": {
            "name": "二层",
            "zones": [
                {"name": "开放办公区(方案一)", "features": ["木纹铝通隔断", "地胶板"]},
                {"name": "开放办公区(方案二)", "features": ["黑色拉丝不锈钢隔断", "方块地毯"]}
            ]
        },
        "3F": {
            "name": "三层",
            "zones": [
                {"name": "大会议室", "features": ["木饰面", "墙布硬包", "仿木地板地胶板"]},
                {"name": "接待室", "features": ["布艺帘+纱帘", "木饰面屏风"]}
            ]
        }
    },
    
    # 材料规格
    "materials": {
        "wall": ["白色乳胶漆", "木饰面（木纹转印）", "墙布硬包", "烤漆玻璃"],
        "floor": ["地胶板", "方块地毯", "防滑瓷砖（800×800, 400×800）", "仿木地板地胶板"],
        "ceiling": ["白色透光灯膜", "白色烤漆", "木纹铝通"],
        "metal": ["黑色拉丝不锈钢", "灰色铝板", "木纹铝通"],
        "stone": ["石材", "米黄色仿石漆", "岩板1200×2400"]
    }
}


# ============================================================
# 强化学习场景库 - 机器人任务定义
# ============================================================

RL_SCENARIOS = {
    # 清洁任务
    "cleaning": {
        "sweep_floor": {
            "task": "扫地",
            "applicable_spaces": ["客厅", "卧室", "书房", "办公室"],
            "floor_types": ["瓷砖", "木地板", "地毯", "地胶板"],
            "difficulty": 1,
            "steps": ["移动到起点", "识别地面垃圾", "规划清扫路径", "执行清扫", "避障"]
        },
        "mop_floor": {
            "task": "擦地",
            "applicable_spaces": ["厨房", "卫生间", "门厅"],
            "floor_types": ["瓷砖", "石材"],
            "difficulty": 2,
            "steps": ["准备拖把", "湿润拖把", "规划路径", "S型擦拭", "清洗拖把"]
        },
        "clean_bathroom": {
            "task": "卫生间清洁",
            "applicable_spaces": ["卫生间"],
            "difficulty": 3,
            "steps": ["清洁马桶", "擦洗漱台", "清镜子", "擦地", "消毒"]
        }
    },
    
    # 整理任务
    "organization": {
        "organize_shoes": {
            "task": "整理鞋子",
            "applicable_spaces": ["玄关", "入户花园"],
            "difficulty": 2,
            "objects": ["运动鞋", "皮鞋", "拖鞋", "雨靴"],
            "constraints": ["分类摆放", "方向一致", "不阻挡通道"]
        },
        "arrange_items": {
            "task": "物品归位",
            "applicable_spaces": ["客厅", "卧室", "书房"],
            "difficulty": 2,
            "objects": ["书籍", "遥控器", "摆件", "衣物"],
            "constraints": ["分类整理", "放回原位"]
        }
    },
    
    # 服务任务
    "service": {
        "serve_tea": {
            "task": "端茶送水",
            "applicable_spaces": ["客厅", "会议室"],
            "difficulty": 3,
            "objects": ["茶杯", "水壶", "托盘"],
            "constraints": ["平稳移动", "不洒出", "正确位置"]
        },
        "deliver_items": {
            "task": "物品传递",
            "applicable_spaces": ["所有空间"],
            "difficulty": 2,
            "objects": ["文件", "餐具", "快递"],
            "constraints": ["轻拿轻放", "确认签收"]
        }
    }
}


# ============================================================
# 物理世界模型 - 属性定义
# ============================================================

PHYSICS_PROPERTIES = {
    # 地面材质
    "flooring": {
        "瓷砖": {
            "friction_coeff": 0.4,
            "density": 2000,  # kg/m³
            "hardness": 0.8,
            "cleanable": True,
            "clean_method": "湿拖+清洁剂",
            "slippery_when_wet": True
        },
        "木地板": {
            "friction_coeff": 0.35,
            "density": 800,
            "hardness": 0.5,
            "cleanable": True,
            "clean_method": "干拖+微湿拖",
            "slippery_when_wet": True
        },
        "地毯": {
            "friction_coeff": 0.6,
            "density": 300,
            "hardness": 0.2,
            "cleanable": True,
            "clean_method": "吸尘器",
            "slippery_when_wet": False
        },
        "地胶板": {
            "friction_coeff": 0.45,
            "density": 1500,
            "hardness": 0.6,
            "cleanable": True,
            "clean_method": "湿拖",
            "slippery_when_wet": False
        }
    },
    
    # 家具
    "furniture": {
        "茶几": {
            "height": 450,  # mm
            "material": "玻璃/石材/木材",
            "graspable": True,
            "moveable": False,
            "obstacle": True
        },
        "沙发": {
            "height": 800,
            "material": "布料/皮革",
            "graspable": False,
            "moveable": False,
            "obstacle": True,
            "under_clearance": 100  # mm
        },
        "餐桌": {
            "height": 750,
            "material": "木材/石材/玻璃",
            "graspable": False,
            "moveable": True,
            "obstacle": True
        },
        "床": {
            "height": 500,
            "material": "木材+布料",
            "graspable": False,
            "moveable": False,
            "obstacle": True,
            "under_clearance": 0
        },
        "衣柜": {
            "height": 2200,
            "material": "木材",
            "graspable": False,
            "moveable": False,
            "obstacle": True
        },
        "橱柜": {
            "height": 850,  # 操作台高度
            "material": "木材+石材",
            "graspable": False,
            "moveable": False,
            "obstacle": True
        }
    },
    
    # 物体可抓取性
    "graspable_objects": {
        "茶杯": {"weight": 200, "size": "small", "fragile": True},
        "书本": {"weight": 500, "size": "medium", "fragile": False},
        "遥控器": {"weight": 150, "size": "small", "fragile": False},
        "摆件": {"weight": 300, "size": "small", "fragile": True},
        "花瓶": {"weight": 800, "size": "medium", "fragile": True},
        "鞋子": {"weight": 400, "size": "medium", "fragile": False}
    }
}


# ============================================================
# 动作空间定义 (Action Space)
# ============================================================

ACTION_SPACE = {
    "navigation": {
        "move_forward": {"distance": [0.1, 0.5, 1.0]},  # 米
        "move_backward": {"distance": [0.1, 0.5, 1.0]},
        "turn_left": {"angle": [15, 45, 90]},  # 度
        "turn_right": {"angle": [15, 45, 90]},
        "goto": {"target": "position"}
    },
    "manipulation": {
        "pick_up": {"object": "graspable_objects"},
        "place_down": {"location": "position"},
        "push": {"direction": "vector"},
        "pull": {"direction": "vector"},
        "open": {"object": "door/cabinet/drawer"},
        "close": {"object": "door/cabinet/drawer"}
    },
    "cleaning": {
        "vacuum": {"area": "region"},
        "mop": {"direction": "path"},
        "wipe": {"surface": "furniture_type"},
        "scrub": {"stain_level": "low/medium/high"}
    }
}


# ============================================================
# 状态空间定义 (State Space)
# ============================================================

STATE_SPACE = {
    "robot": {
        "position": {"type": "x, y, z", "range": [[0, 10], [0, 10], [0, 3]]},
        "orientation": {"type": "quaternion", "range": [-180, 180]},
        "velocity": {"type": "m/s", "range": [0, 1.5]},
        "gripper_state": {"type": "enum", "values": ["open", "closed", "partial"]},
        "battery_level": {"type": "percentage", "range": [0, 100]}
    },
    "environment": {
        "objects": {
            "type": "list",
            "schema": {
                "id": "string",
                "class": "string",
                "position": "x,y,z",
                "orientation": "quaternion",
                "state": "enum",
                "dirty": "boolean"
            }
        },
        "rooms": {
            "type": "graph",
            "nodes": "room_ids",
            "edges": "connectivity"
        }
    },
    "task": {
        "goal": "description",
        "progress": "percentage",
        "subtasks": "list",
        "constraints": "list"
    }
}


# ========================================================= >
# 奖励函数定义 (Reward Function)
# ============================================================

REWARD_FUNCTIONS = {
    "cleaning": {
        "per_step": -0.01,  # 每步惩罚
        "dirt_removed": 1.0,  # 每清除一点污渍
        "time_penalty": -0.001,  # 时间惩罚
        "collision_penalty": -1.0,  # 碰撞惩罚
        "task_completion": 10.0  # 任务完成奖励
    },
    "organization": {
        "per_step": -0.01,
        "item_placed": 2.0,  # 每正确放置一个物品
        "wrong_location": -0.5,  # 放错位置
        "collision_penalty": -1.0,
        "task_completion": 15.0
    },
    "navigation": {
        "per_step": -0.005,
        "distance_to_goal": -0.1,  # 距离目标越近越好
        "collision_penalty": -0.5,
        "goal_reached": 5.0
    }
}


# ============================================================
# 训练数据统计
# ============================================================

DATASET_STATS = {
    "total_projects": 3,
    "projects": [
        {"id": "conghua", "type": "villa", "area": 716.3, "spaces": 8},
        {"id": "hengda", "type": "villa_cluster", "units": 118, "unit_types": 4},
        {"id": "hengchuang", "type": "commercial", "floors": 3, "zones": 12}
    ],
    
    "scenarios": {
        "cleaning": len(RL_SCENARIOS["cleaning"]),
        "organization": len(RL_SCENARIOS["organization"]),
        "service": len(RL_SCENARIOS["service"])
    },
    
    "physics_params": {
        "flooring_types": len(PHYSICS_PROPERTIES["flooring"]),
        "furniture_types": len(PHYSICS_PROPERTIES["furniture"]),
        "graspable_objects": len(PHYSICS_PROPERTIES["graspable_objects"])
    },
    
    "action_space_size": sum([
        len(ACTION_SPACE["navigation"]),
        len(ACTION_SPACE["manipulation"]),
        len(ACTION_SPACE["cleaning"])
    ])
}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("="*60)
    print("RL Training Dataset - Building World Model")
    print("="*60)
    print()
    print("Projects:")
    for p in DATASET_STATS["projects"]:
        print("  - {}: {}".format(p["id"], p["type"]))
    print()
    print("RL Scenarios:")
    for cat, scenes in RL_SCENARIOS.items():
        print("  {}: {} scenarios".format(cat, len(scenes)))
    print()
    print("Physics Properties:")
    print("  Flooring: {} types".format(DATASET_STATS["physics_params"]["flooring_types"]))
    print("  Furniture: {} types".format(DATASET_STATS["physics_params"]["furniture_types"]))
    print("  Graspable: {} types".format(DATASET_STATS["physics_params"]["graspable_objects"]))
    print()
    print("Action Space Size:", DATASET_STATS["action_space_size"])
    print()
    print("[OK] Dataset ready for robot RL training")
