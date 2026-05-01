"""
珠海翠微旧村改造项目 - 世界模型数据
=====================================
项目：奥园14#地块1-4#栋户内及公区精装修工程
位置：珠海市翠微村
类型：大型住宅精装修项目（ Commercial Residential Renovation）

数据来源：
- 14地块交标样板房精装修施工图.zip
- 工程量清单（套内-安装、套内-装饰、公区汇总表）
- CAD图纸（DWG格式）
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


# ============================================================
# 项目基础信息
# ============================================================

PROJECT_INFO = {
    "id": "proj-zhuhai-cuiwei-001",
    "name": "珠海翠微旧村改造项目",
    "developer": "奥园集团",
    "location": "珠海市",
    "project_scope": "14#地块1-4#栋户内及公区精装修",
    
    "building_info": {
        "blocks": ["1#", "2#", "3#", "4#"],
        "unit_types": ["A", "B", "C", "D"],  # 多种户型
        "floors": "高层住宅"
    },
    
    "scope": {
        "indoor": "套内精装修",
        "common_area": "公区精装修"
    },
    
    "documents": {
        "cad_drawings": [
            "A1至A4标准层平面图.dwg",
            "D1至C1平面图.dwg",
            "D2至C2平面图.dwg",
            "C3D4至C4D3平面图.dwg",
            "机电综合图.dwg"
        ],
        "specifications": [
            "公区参考材料表——标准层R1.xls",
            "户内精装修工程量清单.xlsx"
        ]
    }
}


# ============================================================
# 空间类型定义
# ============================================================

SPACE_TYPES = {
    "entryway": {
        "name": "玄关",
        "sub_spaces": ["鞋柜区", "换鞋区"],
        "typical_area": "5-8 m²"
    },
    "living": {
        "name": "客厅",
        "sub_spaces": ["沙发区", "电视背景墙", "阳台连通"],
        "typical_area": "25-35 m²"
    },
    "dining": {
        "name": "餐厅",
        "sub_spaces": ["用餐区", "餐边柜"],
        "typical_area": "15-20 m²"
    },
    "kitchen": {
        "name": "厨房",
        "sub_spaces": ["烹饪区", "洗涤区", "储物区"],
        "typical_area": "8-12 m²",
        "special": "防雾筒灯、抽油烟机插座、净水器插座"
    },
    "bathroom": {
        "name": "卫生间",
        "sub_spaces": ["洗漱区", "淋浴区", "马桶区"],
        "typical_area": "5-8 m²",
        "special": "防溅水插座、镜灯"
    },
    "bedroom": {
        "name": "卧室",
        "sub_spaces": ["睡眠区", "衣柜区", "飘窗区"],
        "typical_area": "15-25 m²",
        "special": "木地板、窗台石"
    },
    "balcony": {
        "name": "阳台",
        "sub_spaces": ["洗衣区", "景观区"],
        "special": "吸顶灯、防溅水插座"
    },
    "corridor": {
        "name": "过道/走廊",
        "typical_area": "根据户型"
    }
}


# ============================================================
# 电气系统 - 强电部分
# ============================================================

ELECTRICAL_SYSTEM = {
    "category": "强电",
    "subsystem": "照明系统",
    
    "items": [
        {
            "id": "E001",
            "name": "吸顶灯（阳台）",
            "spec": "功率18W，色温4000K，光束角110°，LED",
            "mounting": "吸顶安装",
            "unit": "套",
            "total_quantity": 654,
            "unit_price": 100.62,
            "location": "阳台"
        },
        {
            "id": "E002",
            "name": "筒灯（玄关、主卧衣帽间、过道、洗漱区）",
            "spec": "功率9W，色温4000K，光束角36°，LED，开洞φ75mm",
            "mounting": "嵌入式安装",
            "unit": "套",
            "total_quantity": 3216,
            "unit_price": 79.81,
            "location": "玄关、过道、洗漱区"
        },
        {
            "id": "E003",
            "name": "防雾筒灯（卫生间、厨房）",
            "spec": "功率9W，色温4000K，光束角36°，LED，开洞φ75mm",
            "mounting": "嵌入式安装",
            "unit": "套",
            "total_quantity": 3196,
            "unit_price": 95.06,
            "location": "卫生间、厨房"
        },
        {
            "id": "E004",
            "name": "感应筒灯（玄关）",
            "spec": "功率9W，色温4000K，LED，感应控制",
            "mounting": "嵌入式安装",
            "unit": "套",
            "total_quantity": 600,
            "unit_price": 127.57,
            "location": "玄关"
        },
        {
            "id": "E005",
            "name": "灯泡（客餐厅、卧室）",
            "spec": "功率9W，色温4000K",
            "mounting": "明装",
            "unit": "套",
            "total_quantity": 3398,
            "unit_price": 56.24,
            "location": "客厅、餐厅、卧室"
        },
        {
            "id": "E006",
            "name": "T5灯管",
            "spec": "功率7-8W，色温4000K，LED",
            "mounting": "暗藏式",
            "unit": "m",
            "total_quantity": 8029,
            "unit_price": 57.01,
            "location": "灯槽"
        },
        {
            "id": "E007",
            "name": "LED灯带（柜体）",
            "spec": "LED光源",
            "mounting": "暗藏式",
            "unit": "m",
            "total_quantity": 6358.04,
            "unit_price": 57.01,
            "location": "柜体内部"
        }
    ]
}


ELECTRICAL_WIRING = {
    "category": "强电",
    "subsystem": "管线系统",
    
    "items": [
        {
            "id": "W001",
            "name": "金属软管",
            "spec": "管径综合",
            "unit": "m",
            "total_quantity": 3506,
            "unit_price": 8.74
        },
        {
            "id": "W002",
            "name": "电线配管",
            "spec": "PVC线管，管径及敷设方式综合",
            "unit": "m",
            "total_quantity": 224870.58,
            "unit_price": 9.9
        },
        {
            "id": "W003",
            "name": "配线",
            "spec": "BV-2.5mm²",
            "unit": "m",
            "total_quantity": 384648.7,
            "unit_price": 3.83
        },
        {
            "id": "W004",
            "name": "配线",
            "spec": "BV-4.0mm²",
            "unit": "m",
            "total_quantity": 177528.66,
            "unit_price": 5.38
        },
        {
            "id": "W005",
            "name": "接线盒",
            "spec": "86接线地盒/藏光壁灯接线MC",
            "unit": "个",
            "total_quantity": 5866,
            "unit_price": 7.24
        },
        {
            "id": "W006",
            "name": "凿(压)槽",
            "spec": "墙体开槽补槽",
            "unit": "m",
            "total_quantity": 56736,
            "unit_price": 17.94
        },
        {
            "id": "W007",
            "name": "打洞(孔)",
            "spec": "墙体打洞",
            "unit": "个",
            "total_quantity": 2906,
            "unit_price": 34.95
        }
    ]
}


ELECTRICAL_OUTLETS = {
    "category": "强电",
    "subsystem": "插座系统",
    
    "standard_spec": "86mm×86mm，星光灰，暗装",
    
    "items": [
        {"id": "OUT01", "name": "二三孔插座", "qty": 12682, "price": 24.79, "location": "客厅、卧室"},
        {"id": "OUT02", "name": "二三孔插座（带USB）", "qty": 2960, "price": 85.89, "location": "卧室床头"},
        {"id": "OUT03", "name": "带开关二三极插座", "qty": 1962, "price": 37.53, "location": "厨房操作台"},
        {"id": "OUT04", "name": "二三极防溅水插座", "qty": 2906, "price": 32.44, "location": "卫生间"},
        {"id": "OUT05", "name": "三极插座（抽油烟机）", "qty": 654, "price": 24.79, "location": "厨房"},
        {"id": "OUT06", "name": "三极插座（洗碗机）", "qty": 654, "price": 24.79, "location": "厨房"},
        {"id": "OUT07", "name": "三极插座（冰箱）", "qty": 654, "price": 24.79, "location": "厨房"},
        {"id": "OUT08", "name": "防溅水二三极插座（净水器）", "qty": 654, "price": 32.44, "location": "厨房水槽"},
        {"id": "OUT09", "name": "防溅水带开关三极插座（热水器）", "qty": 654, "price": 32.44, "location": "卫生间"},
        {"id": "OUT10", "name": "防溅水带开关三极插座（洗衣机）", "qty": 654, "price": 32.44, "location": "阳台"},
        {"id": "OUT11", "name": "电话插座", "qty": 654, "price": 44.66, "location": "客厅、主卧"}
    ]
}


# ============================================================
# 装饰系统 - 地面工程
# ============================================================

FLOORING_SYSTEM = {
    "category": "装饰",
    "subsystem": "地面工程",
    
    "rooms": {
        "entryway_living": {
            "name": "玄关、客餐厅",
            "items": [
                {
                    "id": "F001",
                    "name": "地面瓷砖",
                    "spec": "800*800mm瓷砖【CT-01】",
                    "layers": [
                        "800*800mm瓷砖面层",
                        "水泥砂浆粘接层",
                        "素水泥浆一道(内掺建筑胶)"
                    ],
                    "unit": "m²",
                    "unit_price": 164.03,
                    "labor": 55,
                    "material": 53.23
                },
                {
                    "id": "F002",
                    "name": "地面美缝",
                    "spec": "清理凹槽、打美缝剂、刮平、清理",
                    "unit": "m²",
                    "unit_price": 40.25,
                    "labor": 30
                },
                {
                    "id": "F003",
                    "name": "门槛石",
                    "spec": "20mm厚ST-01意大利灰门槛石，磨边",
                    "unit": "m²",
                    "unit_price": 636.09,
                    "labor": 125,
                    "material": 390
                },
                {
                    "id": "F004",
                    "name": "石材晶面处理",
                    "spec": "门槛石晶面处理",
                    "unit": "m²",
                    "unit_price": 69,
                    "labor": 45
                }
            ]
        },
        "bedroom": {
            "name": "卧室",
            "items": [
                {
                    "id": "F005",
                    "name": "木地板",
                    "spec": "12mm厚实木复合地板",
                    "layers": [
                        "实木复合地板面层(12厚)",
                        "专用防潮衬垫",
                        "水泥钉固定"
                    ],
                    "unit": "m²",
                    "unit_price": 239.72,
                    "labor": 60,
                    "material": 125
                },
                {
                    "id": "F006",
                    "name": "木地板地面水泥砂浆找平层",
                    "spec": "1:3水泥砂浆找平层",
                    "unit": "m²",
                    "unit_price": 55.22,
                    "labor": 21.6
                },
                {
                    "id": "F007",
                    "name": "金属收口",
                    "spec": "MT-01深灰色金属收口",
                    "unit": "m",
                    "unit_price": 30.94
                },
                {
                    "id": "F008",
                    "name": "窗台石",
                    "spec": "15mm厚ST-03白色人造石窗台板，40mm宽折边",
                    "unit": "m²",
                    "unit_price": 447.48,
                    "labor": 73,
                    "material": 281.25
                }
            ]
        }
    }
}


# ============================================================
# 装饰系统 - 天花工程
# ============================================================

CEILING_SYSTEM = {
    "category": "装饰",
    "subsystem": "天花工程",
    
    "items": [
        {
            "id": "C001",
            "name": "轻钢龙骨石膏板平面吊顶",
            "spec": "双层9.5mm厚纸面石膏板，C50系列轻钢龙骨",
            "calculation": "按水平投影面积计算",
            "unit": "m²",
            "unit_price": 144.69,
            "labor": 63.5,
            "material": 29.38
        },
        {
            "id": "C002",
            "name": "PVC护角条",
            "spec": "10mm宽PVC护角条",
            "unit": "m",
            "unit_price": 5.84
        },
        {
            "id": "C003",
            "name": "天花白色无机涂料",
            "spec": "无机涂料面漆两遍，封闭底漆一遍，刮腻子三遍+打磨",
            "color": "PT-01",
            "unit": "m²",
            "unit_price": 37.97,
            "labor": 23,
            "material": 7.52
        },
        {
            "id": "C004",
            "name": "灯槽（高420mm）",
            "spec": "单层9.5mm厚纸面石膏板，9mm厚夹板基层",
            "height": 420,
            "unit": "m",
            "unit_price": 101.75,
            "labor": 65,
            "material": 16.24
        },
        {
            "id": "C005",
            "name": "窗帘盒（高200mm）",
            "spec": "单层9mm纸面石膏板，15mm厚A级木质防火压力板，C50轻钢龙骨",
            "height": 200,
            "unit": "m",
            "unit_price": 85,
            "labor": 45.5,
            "material": 25.83
        },
        {
            "id": "C006",
            "name": "石膏板走边装饰线",
            "spec": "9mm玻镁板基层，9mm石膏板装饰线",
            "height": 500,
            "unit": "m",
            "unit_price": 66.11,
            "labor": 45.5,
            "material": 7.64
        }
    ]
}


# ============================================================
# 装饰系统 - 墙面工程
# ============================================================

WALL_SYSTEM = {
    "category": "装饰",
    "subsystem": "墙面工程",
    
    "items": [
        {
            "id": "WALL01",
            "name": "铝合金踢脚线",
            "spec": "30mm高MT-02铝合金踢脚线",
            "height": 30,
            "unit": "m",
            "unit_price": 25.27,
            "labor": 8,
            "material": 11.88
        },
        {
            "id": "WALL02",
            "name": "墙面白色无机涂料",
            "spec": "无机涂料面漆两遍，封闭底漆一遍，刮腻子三遍+打磨",
            "color": "PT-01",
            "unit": "m²",
            "unit_price": 37.97,
            "labor": 23,
            "material": 7.52
        }
    ]
}


# ============================================================
# 装饰系统 - 柜体工程
# ============================================================

CABINET_SYSTEM = {
    "category": "装饰",
    "subsystem": "柜体工程",
    
    "items": [
        {
            "id": "CAB01",
            "name": "入户玄关柜",
            "spec": "鞋柜，2.4m*2.4m*0.35m",
            "materials": [
                "内部三聚氰胺板",
                "PVC饰面板",
                "WD-01 PVC覆膜板",
                "MR01 清镜 5mm",
                "铝合金挂衣杆"
            ],
            "unit": "m²",
            "unit_price": 1704.3,
            "labor": 250,
            "material": 1182
        }
    ]
}


# ============================================================
# 材料清单 - 瓷砖体系
# ============================================================

TILE_SYSTEM = {
    "tiles": [
        {"code": "CT-01", "name": "800*800mm瓷砖", "location": "客餐厅地面"},
        {"code": "ST-01", "name": "意大利灰门槛石", "location": "门槛"},
        {"code": "ST-03", "name": "白色人造石窗台石", "location": "卧室窗台"}
    ],
    "finishes": [
        {"code": "PT-01", "name": "白色无机涂料", "location": "天花、墙面"},
        {"code": "MT-01", "name": "深灰色金属收口", "location": "地面"},
        {"code": "MT-02", "name": "铝合金踢脚线", "location": "墙面底部"}
    ]
}


# ============================================================
# 世界模型场景数据
# ============================================================

WORLD_MODEL_SCENE = {
    "project": PROJECT_INFO,
    
    "spaces": SPACE_TYPES,
    
    "building_objects": {
        # 电气系统
        "lighting": ELECTRICAL_SYSTEM,
        "wiring": ELECTRICAL_WIRING,
        "outlets": ELECTRICAL_OUTLETS,
        
        # 装饰系统
        "flooring": FLOORING_SYSTEM,
        "ceiling": CEILING_SYSTEM,
        "walls": WALL_SYSTEM,
        "cabinets": CABINET_SYSTEM,
        
        # 材料
        "materials": TILE_SYSTEM
    },
    
    "physics_properties": {
        "materials": {
            "瓷砖-CT-01": {"friction": 0.4, "density": 2000, "hardness": "high"},
            "木地板": {"friction": 0.3, "density": 800, "hardness": "medium"},
            "石材-ST-01": {"friction": 0.35, "density": 2700, "hardness": "very_high"},
            "石膏板": {"friction": 0.2, "density": 900, "hardness": "low"},
            "铝合金": {"friction": 0.15, "density": 2700, "hardness": "high"}
        },
        "furniture": {
            "玄关柜": {"height": 2400, "width": 2400, "depth": 350, "graspable": True},
            "木地板区域": {"height": 0, "area": "variable", "walkable": True, "slippery": False}
        }
    },
    
    "robot_tasks": {
        "cleaning": {
            "entryway": ["扫地", "擦地", "清灰"],
            "living": ["扫地", "擦地", "整理杂物"],
            "kitchen": ["擦台面", "擦瓷砖", "清油污"],
            "bathroom": ["擦台面", "清镜子", "擦地"]
        },
        "organization": {
            "shoes": ["识别鞋类", "归位放置"],
            "items": ["识别物品", "分类整理"]
        }
    }
}


# ============================================================
# 统计汇总
# ============================================================

STATS = {
    "total_units": 4,  # 4栋楼
    "unit_types": 4,   # 4种户型
    
    "electrical": {
        "lighting_total": sum(item["total_quantity"] for item in ELECTRICAL_SYSTEM["items"]),
        "wiring_meters": sum(item["total_quantity"] for item in ELECTRICAL_WIRING["items"]),
        "outlet_total": sum(item["qty"] for item in ELECTRICAL_OUTLETS["items"])
    },
    
    "materials": {
        "tiles_800": "大量",
        "wood_flooring": "大量",
        "drywall_sheets": "大量"
    }
}


if __name__ == "__main__":
    print("="*60)
    print("珠海翠微旧村改造项目 - 世界模型数据")
    print("="*60)
    print()
    print("项目:", PROJECT_INFO["name"])
    print("开发商:", PROJECT_INFO["developer"])
    print()
    print("电气系统统计:")
    print(f"  灯具总数: {STATS['electrical']['lighting_total']}")
    print(f"  管线总长: {STATS['electrical']['wiring_meters']:.0f}m")
    print(f"  插座总数: {STATS['electrical']['outlet_total']}")
    print()
    print("✅ 数据加载完成")
