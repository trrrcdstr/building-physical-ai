"""
建筑数据库 - 新数据整合
============================
新增项目：
1. 建筑结构项目
2. 黄总

数据模型：统一建筑对象结构
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path

# ============================================================
# 统一数据模型
# ============================================================

@dataclass
class BuildingProject:
    """建筑项目"""
    id: str
    name: str
    client: str
    project_type: str  # residential, villa, landscape, structure
    
    # 数据文件
    cad_files: List[str]
    render_images: List[str]
    structure_files: List[str]  # 结构图纸
    electrical_files: List[str]  # 电气图纸
    landscape_files: List[str]   # 景观图纸
    
    # 解析状态
    parsed: bool = False
    object_count: int = 0


@dataclass
class BuildingObject:
    """建筑对象"""
    id: str
    name: str
    type: str  # wall, floor, door, window, pillar, beam...
    category: str  # structure, electrical, landscape, utility
    
    # 几何
    position: List[float]
    dimensions: Dict[str, float]  # width, height, depth
    
    # 物理属性
    physics: Optional[Dict] = None
    
    # 关联
    project_id: str = ""
    floor: int = 0  # 楼层


# ============================================================
# 新增项目数据
# ============================================================

NEW_PROJECTS = [
    {
        "id": "proj-struct-001",
        "name": "奕锜自建房",
        "client": "奕锜",
        "project_type": "residential",
        "files": {
            "cad": ["自建房-施工结构图-KennyZ.pdf"],
            "structure": ["蓝图图纸.pdf"],
            "renders": []
        },
        "description": "自建房施工结构图，包含基础、梁柱、楼板等结构图纸"
    },
    {
        "id": "proj-huangzong-001",
        "name": "黄哥别墅",
        "client": "黄总",
        "project_type": "villa",
        "files": {
            "cad": ["2_黄哥别墅图2022-12-2.pdf", "黄哥别墅图地下室11.25-Model.pdf"],
            "renders": [
                "4fee63d865ed7bb7e6b9c47739110864.jpg",
                "67d3f84d3ebed7952c73fc91dbd3be46.jpg",
                "a9bb26297ac44c160b6fef9e06696e9d.jpg"
            ]
        },
        "description": "黄总别墅项目，包含地上和地下室图纸"
    },
    {
        "id": "proj-huangzong-002",
        "name": "观府壹号",
        "client": "黄总",
        "project_type": "landscape",
        "files": {
            "landscape": ["观府壹号黄总方案.pdf"]
        },
        "description": "观府壹号别墅花园景观方案设计，包含烧烤区、锦鲤池、假山跌水等"
    }
]


# ============================================================
# 建筑结构类型定义
# ============================================================

STRUCTURE_TYPES = {
    "foundation": {
        "name": "基础",
        "materials": ["钢筋混凝土", "砖石基础"],
        "physics": {"density": 2400, "stiffness": 30000}
    },
    "column": {
        "name": "柱子",
        "materials": ["钢筋混凝土柱", "钢结构柱"],
        "physics": {"density": 2500, "stiffness": 35000}
    },
    "beam": {
        "name": "梁",
        "materials": ["钢筋混凝土梁", "钢梁"],
        "physics": {"density": 2400, "stiffness": 30000}
    },
    "slab": {
        "name": "楼板",
        "materials": ["钢筋混凝土板", "预制板"],
        "physics": {"density": 2400, "stiffness": 28000}
    },
    "wall": {
        "name": "墙体",
        "materials": ["承重墙", "隔墙"],
        "physics": {"density": 1800, "stiffness": 25000}
    },
    "stair": {
        "name": "楼梯",
        "materials": ["钢筋混凝土"],
        "physics": {"density": 2400, "stiffness": 28000}
    }
}


# ============================================================
# 电气系统类型
# ============================================================

ELECTRICAL_TYPES = {
    "distribution_board": {
        "name": "配电箱",
        "voltage": 380,
        "circuits": []
    },
    "lighting_circuit": {
        "name": "照明回路",
        "voltage": 220,
        "wire": "BV 2.5mm²"
    },
    "power_circuit": {
        "name": "动力回路",
        "voltage": 380,
        "wire": "BV 4mm²"
    },
    "switch": {
        "name": "开关",
        "height": 1300,  # mm, 国标
        "type": "单开/双开/多开"
    },
    "outlet": {
        "name": "插座",
        "height": 300,  # mm, 普通插座
        "height_high": 1100  # mm, 空调/热水器
    }
}


# ============================================================
# 景观设计元素
# ============================================================

LANDSCAPE_TYPES = {
    "water_feature": {
        "name": "水景",
        "types": ["锦鲤池", "假山跌水", "喷泉", "溪流"],
        "physics": {
            "water_depth": 0.5,  # m
            "flow_rate": 0  # L/s
        }
    },
    "planting": {
        "name": "绿化种植",
        "types": ["乔木", "灌木", "地被", "草坪"],
        "maintenance": {
            "irrigation": True,
            "sunlight": "全日照/半阴/阴"
        }
    },
    "hardscape": {
        "name": "硬景",
        "types": ["亭子", "廊架", "景墙", "台阶", "栏杆"],
        "materials": ["石材", "木材", "金属", "混凝土"]
    },
    "lighting": {
        "name": "景观照明",
        "types": ["投光灯", "地埋灯", "水底灯", "庭院灯"],
        "voltage": 24  # 安全电压
    },
    "entrance": {
        "name": "出入口",
        "types": ["主入口", "次入口", "消防通道"]
    }
}


# ============================================================
# 空间分类
# ============================================================

SPACE_TYPES = {
    "indoor": {
        "name": "室内",
        "sub_spaces": ["客厅", "卧室", "厨房", "卫生间", "书房", "餐厅", "阳台"]
    },
    "basement": {
        "name": "地下室",
        "sub_spaces": ["车库", "储藏室", "影音室", "酒窖", "设备间"]
    },
    "landscape": {
        "name": "景观",
        "sub_spaces": ["花园", "庭院", "露台", "烧烤区", "泳池区"]
    }
}


# ============================================================
# 工具函数
# ============================================================

def get_project_files(base_path: str, project: Dict) -> Dict:
    """获取项目文件路径"""
    files = {
        "cad": [],
        "renders": [],
        "structure": [],
        "electrical": [],
        "landscape": []
    }
    
    for category, filenames in project.get("files", {}).items():
        for fname in filenames:
            fpath = Path(base_path) / fname
            if fpath.exists():
                files[category].append(str(fpath))
    
    return files


def create_building_object_from_pdf(obj_data: Dict, project_id: str) -> BuildingObject:
    """从PDF解析数据创建建筑对象"""
    return BuildingObject(
        id=obj_data.get("id", ""),
        name=obj_data.get("name", ""),
        type=obj_data.get("type", "wall"),
        category=obj_data.get("category", "structure"),
        position=obj_data.get("position", [0, 0, 0]),
        dimensions=obj_data.get("dimensions", {"width": 1, "height": 1, "depth": 1}),
        physics=obj_data.get("physics"),
        project_id=project_id,
        floor=obj_data.get("floor", 0)
    )


# ============================================================
# 数据统计
# ============================================================

DATA_STATS = {
    "total_projects": len(NEW_PROJECTS),
    "by_type": {
        "residential": 1,
        "villa": 2,
        "landscape": 1
    },
    "by_category": {
        "structure": 2,
        "electrical": 0,
        "landscape": 1
    }
}


if __name__ == "__main__":
    print("="*60)
    print("建筑数据库 - 新增项目数据")
    print("="*60)
    print()
    
    print("新增项目:")
    for p in NEW_PROJECTS:
        print(f"  - {p['name']} ({p['client']})")
        print(f"    类型: {p['project_type']}")
        print(f"    文件: {p['files']}")
        print()
    
    print("建筑结构类型:")
    for stype, info in STRUCTURE_TYPES.items():
        print(f"  {stype}: {info['name']}")
    
    print()
    print("景观元素:")
    for ltype, info in LANDSCAPE_TYPES.items():
        print(f"  {ltype}: {info['name']}")
    
    print()
    print("✅ 数据模型加载完成")
