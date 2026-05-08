"""
建筑认知Agent API Server v2.0
增强版：完整物理常识输出
- 材质摩擦系数（干/湿）
- 机器人操作约束（力度/速度/碰撞阈值）
- 安全分析 + 承重墙检测
- 6个预设任务专项优化
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import re

# ════════════════════════════════════════════════════════════
#  材质物理数据库（核心护城河数据）
# ════════════════════════════════════════════════════════════

MATERIAL_PHYSICS: Dict[str, Dict] = {
    # ── 玻璃类 ────────────────────────────────────────────
    "钢化玻璃": {
        "category": "glass",
        "density_kg_m3": 2500,
        "friction_dry": 0.35,
        "friction_wet": 0.18,          # 淋浴后μ_wet显著降低
        "friction_wet_range": "0.18–0.35",
        "hardness_mohs": 6.5,
        "elastic_modulus_gpa": 72,
        "compressive_strength_mpa": 200,
        "collision_threshold_j": 50,    # 8mm钢化玻璃冲击阈值50J
        "thermal_expansion": 9e-6,
        "robot_cleaning": {
            "force_n": {"min": 0.5, "max": 5.0, "optimal": 2.0},  # 清洁压力
            "speed_m_s": {"max": 0.15, "optimal": 0.08},          # 擦拭速度
            "tool": "软纤维布 + 中性清洁剂",
            "technique": "S型擦拭路径，避免画圈",
            "temperature_limit_c": 60,
        },
        "safety_notes": [
            "碰撞能量必须 <50J，否则玻璃碎裂",
            "湿摩擦系数低（0.18），机器人需防滑设计",
            "避免使用含氨/醇的清洁剂，会腐蚀玻璃表面",
        ],
    },

    # ── 瓷砖类 ────────────────────────────────────────────
    "瓷砖": {
        "category": "ceramic",
        "density_kg_m3": 2300,
        "friction_dry": 0.40,
        "friction_wet": 0.20,
        "friction_wet_range": "0.20–0.40",
        "hardness_mohs": 6.0,
        "elastic_modulus_gpa": 50,
        "compressive_strength_mpa": 150,
        "robot_cleaning": {
            "force_n": {"min": 1.0, "max": 8.0, "optimal": 3.0},
            "speed_m_s": {"max": 0.20, "optimal": 0.10},
            "tool": "硬毛刷 + pH中性清洁剂",
            "technique": "直线往复，缝隙处加强",
        },
        "safety_notes": [
            "湿区摩擦系数从0.40降至0.20，防滑风险高",
            "瓷砖接缝处高度差可达2mm，注意足式机器人越障",
            "碱性清洁剂会损伤瓷砖釉面",
        ],
    },

    # ── 实木地板 ──────────────────────────────────────────
    "实木地板": {
        "category": "wood",
        "density_kg_m3": 700,
        "friction_dry": 0.40,
        "friction_wet": 0.25,
        "friction_wet_range": "0.25–0.40",
        "hardness_mohs": 2.5,
        "elastic_modulus_gpa": 12,
        "compressive_strength_mpa": 40,
        "water_absorption_pct": 8,       # 实木吸水率8%
        "robot_cleaning": {
            "force_n": {"min": 0.3, "max": 3.0, "optimal": 1.0},
            "speed_m_s": {"max": 0.25, "optimal": 0.12},
            "tool": "微纤维布 + 专用木地板清洁剂",
            "technique": "单向擦拭，顺木纹方向",
            "humidity_limit_pct": 45,     # 湿度>45%实木地板易变形
        },
        "safety_notes": [
            "实木硬度低（Mohs 2.5），清洁力度必须<3N避免划伤",
            "湿度>45%地板膨胀，>65%发霉",
            "湿拖把含水量<30%，严禁大量液体泼洒",
            "拖地机器人需配备微纤维布而非硬刷",
        ],
    },

    # ── 不锈钢 ────────────────────────────────────────────
    "不锈钢台面": {
        "category": "metal",
        "density_kg_m3": 8000,
        "material": "304不锈钢",
        "friction_dry": 0.20,
        "friction_wet": 0.12,
        "friction_wet_range": "0.12–0.20",
        "hardness_mohs": 5.5,
        "elastic_modulus_gpa": 193,
        "compressive_strength_mpa": 500,
        "thermal_conductivity_w_mk": 16,
        "robot_cleaning": {
            "force_n": {"min": 0.5, "max": 4.0, "optimal": 1.5},
            "speed_m_s": {"max": 0.20, "optimal": 0.10},
            "tool": "柔软海绵 + 中性去油清洁剂",
            "technique": "单向擦拭，避免水渍残留",
            "polish_stroke": "最后用干布抛光",
        },
        "safety_notes": [
            "湿摩擦系数极低（0.12），表面油污未清理前机器人可能打滑",
            "不锈钢台面边缘锋利（切割R角<1mm），需检测碰撞",
            "强酸/强碱清洁剂会腐蚀钝化膜，选用中性pH",
        ],
    },

    # ── 混凝土墙体 ────────────────────────────────────────
    "混凝土墙体": {
        "category": "masonry",
        "density_kg_m3": 2400,
        "friction_dry": 0.60,
        "friction_wet": 0.45,
        "hardness_mohs": 5.0,
        "compressive_strength_mpa": 30,   # C30混凝土
        "drill": {
            "torque_nm": {"min": 15, "max": 25, "optimal": 20},
            "rpm": {"min": 800, "max": 1200, "optimal": 1000},
            "feed_rate_mm_min": {"min": 30, "max": 60, "optimal": 45},
            "drill_bit": "冲击钻 + 6mm硬质合金钻头",
            "dust_extraction": "必须开启吸尘",
            "max_depth_mm": {"non_structural": 40, "anchor": 30},
        },
        "safety_notes": [
            "混凝土是非匀质材料，钻孔时需避开骨料（石子）",
            "承重墙（剪力墙）禁止钻孔",
            "梁/柱区域禁止钻孔，会破坏结构完整性",
        ],
    },

    # ── 普通砖墙 ─────────────────────────────────────────
    "砖墙": {
        "category": "masonry",
        "density_kg_m3": 1800,
        "friction_dry": 0.50,
        "friction_wet": 0.35,
        "hardness_mohs": 4.0,
        "compressive_strength_mpa": 10,   # MU10砖
        "drill": {
            "torque_nm": {"min": 10, "max": 18, "optimal": 14},
            "rpm": {"min": 600, "max": 900, "optimal": 750},
            "feed_rate_mm_min": {"min": 40, "max": 80, "optimal": 60},
            "drill_bit": "冲击钻 + 6mm普通钻头",
            "dust_extraction": "建议开启吸尘",
            "max_depth_mm": {"non_structural": 50, "anchor": 35},
        },
        "safety_notes": [
            "砖墙可钻孔，但需避开门窗上方过梁区域",
            "砖缝处强度较低，膨胀螺栓需打在砖体上",
        ],
    },

    # ── 石膏板 ───────────────────────────────────────────
    "石膏板": {
        "category": "board",
        "density_kg_m3": 900,
        "friction_dry": 0.40,
        "friction_wet": 0.30,
        "compressive_strength_mpa": 5,
        "drill": {
            "torque_nm": {"min": 3, "max": 8, "optimal": 5},
            "rpm": {"min": 400, "max": 600, "optimal": 500},
            "drill_bit": "木工钻 + 6mm，快速穿透",
            "max_depth_mm": {"max": 30, "note": "石膏板总厚度通常12-15mm"},
        },
        "safety_notes": [
            "石膏板承重能力极低（<5kg单点悬挂）",
            "必须使用专门的石膏板膨胀螺栓（蝶形膨胀）",
            "禁止悬挂重型物体",
        ],
    },

    # ── 木质家具 ──────────────────────────────────────────
    "木质家具": {
        "category": "wood_furniture",
        "density_kg_m3": 650,             # 中密度纤维板
        "friction_dry": 0.35,
        "friction_wet": 0.25,
        "hardness_mohs": 2.0,
        "weight_kg_range": "5–50kg",       # 床头柜典型重量
        "robot_move": {
            "grasp_force_n": {"min": 15, "max": 40, "optimal": 25},
            "lifting_speed_m_s": {"max": 0.15, "optimal": 0.08},
            "clearance_mm": 50,            # 移动时与家具最小间隙
            "path_planning": "优先直线，墙角处需旋转避障",
        },
        "safety_notes": [
            "木质家具表面硬度低，抓取力>40N会造成压痕",
            "移动时注意地面材质，实木地板上拖拽摩擦系数0.35",
            "搬运路径需清理地面障碍物（拖鞋/地毯）",
            "确认地面承重能力，地毯+家具可能超载",
        ],
    },
}

# ════════════════════════════════════════════════════════════
#  墙体数据
# ════════════════════════════════════════════════════════════

WALLS = {
    "north": {
        "label": "北墙",
        "load_bearing": True,      # 承重墙
        "material": "混凝土墙体",
        "thickness_cm": 24,
        "reinforcement": "有钢筋",
        "drill_allowed": False,
        "reason": "承重墙（剪力墙），禁止钻孔",
    },
    "east": {
        "label": "东墙",
        "load_bearing": False,
        "material": "砖墙",
        "thickness_cm": 12,
        "has_window": True,
        "window_clearance_cm": 50,   # 距窗框至少50cm
        "drill_allowed": True,
        "max_depth_mm": 35,
    },
    "south": {
        "label": "南墙",
        "load_bearing": False,
        "material": "砖墙",
        "thickness_cm": 12,
        "drill_allowed": True,
        "max_depth_mm": 35,
    },
    "west": {
        "label": "西墙",
        "load_bearing": False,
        "material": "砖墙",
        "thickness_cm": 12,
        "drill_allowed": True,
        "max_depth_mm": 35,
    },
}

# ════════════════════════════════════════════════════════════
#  房间/场景数据
# ════════════════════════════════════════════════════════════

ROOMS = {
    "shower_room": {
        "name": "淋浴房",
        "area_m2": 2.1,
        "type": "wet_room",
        "wet": True,
        "adjacent": ["master_bathroom"],
        "materials": ["钢化玻璃", "瓷砖"],
        "floor_material": "瓷砖",
        "wall_material": "瓷砖",
        "special": "玻璃隔断",
    },
    "master_bathroom": {
        "name": "主卧卫生间",
        "area_m2": 8.5,
        "type": "wet_room",
        "wet": True,
        "adjacent": ["bedroom"],
        "materials": ["瓷砖", "不锈钢台面"],
    },
    "bedroom": {
        "name": "主卧",
        "area_m2": 20.0,
        "type": "dry_room",
        "wet": False,
        "adjacent": ["master_bathroom", "study"],
        "materials": ["实木地板"],
        "floor_material": "实木地板",
    },
    "kitchen": {
        "name": "厨房",
        "area_m2": 12.0,
        "type": "wet_room",
        "wet": True,
        "adjacent": ["dining_room"],
        "materials": ["瓷砖", "不锈钢台面"],
        "floor_material": "瓷砖",
        "counter_material": "不锈钢台面",
    },
}

# ════════════════════════════════════════════════════════════
#  任务→材质映射（6个预设任务）
# ════════════════════════════════════════════════════════════

TASK_PHYSICS_PROFILES: Dict[str, Dict] = {
    # ── 任务1：清洁淋浴房玻璃隔断 ───────────────────────
    "clean_shower_glass": {
        "task_name": "清洁淋浴房玻璃隔断",
        "target_object": "钢化玻璃隔断",
        "primary_material": "钢化玻璃",
        "secondary_materials": ["瓷砖（地面/墙面）"],
        "physics_analysis": {
            "primary": MATERIAL_PHYSICS["钢化玻璃"],
            "floor": MATERIAL_PHYSICS["瓷砖"],
        },
        "operation_constraints": {
            "cleaning_force_n": {"min": 0.5, "max": 5.0, "optimal": 2.0},
            "cleaning_speed_m_s": {"max": 0.15, "optimal": 0.08},
            "water_splash_risk": "high",         # 淋浴后水渍溅射
            "thermal_shock_risk": "medium",      # 冷热水交替导致热应力
            "slip_risk_level": "high",           # 湿区防滑是核心
            "robot_traction": "需履带式或加大摩擦底盘",
        },
        "steps": [
            {"step": 1, "action": "预处理", "detail": "穿戴防滑套筒（底盘摩擦系数μ≥0.6），用干布擦拭表面水渍", "duration_s": 30},
            {"step": 2, "action": "喷洒清洁剂", "detail": "中性玻璃清洁剂（pH 6-8），距玻璃30cm均匀喷洒", "duration_s": 15},
            {"step": 3, "action": "主清洁", "detail": "软纤维布，速度≤0.08m/s，S型路径，力度2N，清洁剂残留≤0.1mg/cm²", "duration_s": 120},
            {"step": 4, "action": "清水冲洗", "detail": "微量清水（<100ml），避免流入地面排水口以外区域", "duration_s": 30},
            {"step": 5, "action": "干燥抛光", "detail": "干燥鹿皮布，速度0.05m/s，玻璃透明度恢复到初始95%以上", "duration_s": 60},
        ],
        "quality_metrics": {
            "transparency_recovery": "≥95%",
            "water_streak_residue": "≤0.1mg/cm²",
            "cleaning_time_s": 255,
        },
    },

    # ── 任务2：东墙钻孔挂画 ──────────────────────────────
    "drill_east_wall_picture": {
        "task_name": "东墙钻孔挂画",
        "target_object": "东墙",
        "primary_material": "砖墙",
        "physics_analysis": {
            "wall": MATERIAL_PHYSICS["砖墙"],
        },
        "operation_constraints": {
            "torque_nm": {"optimal": 14},
            "rpm": {"optimal": 750},
            "feed_rate_mm_min": {"optimal": 60},
            "drill_bit": "6mm硬质合金钻头",
            "max_depth_mm": 35,
            "dust_extraction": "必须",
            "load_limit_kg": "3kg以下（轻质画框）",
        },
        "pre_checks": [
            "确认孔位距离窗框≥50cm（东墙有窗）",
            "使用钢筋探测仪确认避开钢筋（深度>20mm遇阻需停止）",
            "确认墙面无水管/电线（通常距墙面25mm以内走线）",
        ],
        "steps": [
            {"step": 1, "action": "定位标记", "detail": "水平仪确认画框水平，用铅笔标记孔位，误差≤2mm", "duration_s": 30},
            {"step": 2, "action": "钻孔准备", "detail": "戴上护目镜和口罩，接通吸尘器，设置冲击钻扭矩14Nm/750rpm", "duration_s": 20},
            {"step": 3, "action": "钻孔", "detail": "垂直墙面钻进，速率60mm/min，深度35mm，钻进过程检测振动异常", "duration_s": 40},
            {"step": 4, "action": "清孔", "detail": "用吸尘器彻底清除孔内粉尘（残留粉尘会导致膨胀螺栓松动）", "duration_s": 15},
            {"step": 5, "action": "安装膨胀螺栓", "detail": "6mm膨胀螺栓，敲入孔内，螺栓外露5mm", "duration_s": 15},
            {"step": 6, "action": "悬挂画框", "detail": "水平仪复核，挂上画框，画框重量<3kg", "duration_s": 20},
        ],
        "quality_metrics": {
            "hole_depth_mm": "35±2",
            "horizontal_error_mm": "≤2",
            "dust_residue_mg": "<50",
        },
    },

    # ── 任务3：北墙钻孔书架 ─────────────────────────────
    "drill_north_wall_shelf": {
        "task_name": "北墙钻孔安装书架",
        "target_object": "北墙",
        "primary_material": "混凝土墙体",
        "physics_analysis": {
            "wall": MATERIAL_PHYSICS["混凝土墙体"],
        },
        "operation_constraints": {
            "torque_nm": {"optimal": 20},
            "rpm": {"optimal": 1000},
            "drill_bit": "6mm硬质合金钻头（混凝土专用）",
            "max_depth_mm": 30,
            "dust_extraction": "必须",
        },
        "BLOCKED": True,
        "block_reason": "北墙是承重墙（剪力墙），严禁钻孔。承重墙破坏会导致结构安全隐患。",
        "block_code": "LOAD_BEARING_WALL_VIOLATION",
        "alternative": {
            "suggestion": "在东墙/西墙/南墙（非承重墙）安装书架",
            "wall_options": ["east: 砖墙，厚度12cm，可钻孔", "west: 砖墙，厚度12cm，可钻孔", "south: 砖墙，厚度12cm，可钻孔"],
            "bookshelf_weight_kg": "建议总重<15kg",
            "drill_params": "torque:14Nm, rpm:750, depth:35mm",
        },
    },

    # ── 任务4：清洁卧室实木地板 ─────────────────────────
    "clean_bedroom_floor": {
        "task_name": "清洁卧室实木地板",
        "target_object": "实木地板",
        "primary_material": "实木地板",
        "physics_analysis": {
            "floor": MATERIAL_PHYSICS["实木地板"],
        },
        "operation_constraints": {
            "cleaning_force_n": {"min": 0.3, "max": 3.0, "optimal": 1.0},
            "cleaning_speed_m_s": {"max": 0.25, "optimal": 0.12},
            "tool": "微纤维布（拖布机器人）或干布吸附式",
            "moisture_limit_pct": 30,          # 拖布含水量<30%
            "slip_risk": "medium",
            "floor_protection": "软质轮或布料包裹脚轮",
            "humidity_control": "室内湿度需维持在30-45%",
        },
        "steps": [
            {"step": 1, "action": "干拖预处理", "detail": "微纤维布干拖，吸附表面灰尘/毛发，速度0.15m/s", "duration_s": 90},
            {"step": 2, "action": "湿度检测", "detail": "用湿度仪检测地板含水率，需<8%方可进行湿拖", "duration_s": 10},
            {"step": 3, "action": "湿拖清洁", "detail": "微纤维布含水率<30%，力度1N，速度0.12m/s，顺木纹方向", "duration_s": 120},
            {"step": 4, "action": "局部处理", "detail": "顽固污渍用专用木地板清洁剂，点涂≤5ml，2分钟后擦净", "duration_s": 60},
            {"step": 5, "action": "干燥抛光", "detail": "干布快速抛光，速度0.08m/s，恢复光泽", "duration_s": 60},
        ],
        "quality_metrics": {
            "dust_removal_rate": "≥99%",
            "moisture_after_pct": "<8%",
            "scratch_risk": "low（力度<3N）",
        },
    },

    # ── 任务5：清洁厨房不锈钢台面 ──────────────────────
    "clean_kitchen_counter": {
        "task_name": "清洁厨房不锈钢台面",
        "target_object": "不锈钢台面",
        "primary_material": "不锈钢台面",
        "physics_analysis": {
            "counter": MATERIAL_PHYSICS["不锈钢台面"],
        },
        "operation_constraints": {
            "cleaning_force_n": {"min": 0.5, "max": 4.0, "optimal": 1.5},
            "cleaning_speed_m_s": {"max": 0.20, "optimal": 0.10},
            "tool": "柔软海绵 + 中性去油清洁剂（pH 6-8）",
            "griddle_surface_temp_c": "<40（台面温度需低于40°C才能清洁）",
            "slip_risk": "high",              # 湿态摩擦系数仅0.12
            "sharp_edge_risk": "medium",       # 台面边缘锋利
        },
        "steps": [
            {"step": 1, "action": "油污预判", "detail": "视觉识别油污区域，厚重油渍需预喷清洁剂静置2min", "duration_s": 15},
            {"step": 2, "action": "主清洁", "detail": "柔软海绵+中性清洁剂，力度1.5N，速度0.10m/s，单向擦拭", "duration_s": 90},
            {"step": 3, "action": "细节处理", "detail": "台面边缘/角落用软毛刷清理（力度<1N），水渍残留<0.5ml", "duration_s": 60},
            {"step": 4, "action": "清水擦拭", "detail": "清水湿润海绵擦拭，去除残留清洁剂（擦拭3遍）", "duration_s": 30},
            {"step": 5, "action": "干燥抛光", "detail": "干布快速抛光，恢复金属光泽，擦纹方向与原始纹路一致", "duration_s": 45},
        ],
        "quality_metrics": {
            "grease_removal": "≥98%",
            "water_streak_residue": "<0.5ml",
            "polish_luster": "恢复原始亮度≥90%",
        },
    },

    # ── 任务6：移动床头柜到窗边 ────────────────────────
    "move_bedside_table": {
        "task_name": "移动床头柜到窗边",
        "target_object": "木质床头柜",
        "primary_material": "木质家具",
        "secondary_context": {
            "floor": "实木地板",
            "floor_physics": MATERIAL_PHYSICS["实木地板"],
        },
        "physics_analysis": {
            "furniture": MATERIAL_PHYSICS["木质家具"],
        },
        "operation_constraints": {
            "grasp_force_n": {"min": 15, "max": 40, "optimal": 25},
            "lifting_speed_m_s": {"max": 0.15, "optimal": 0.08},
            "path_clearance_mm": 50,
            "estimated_weight_kg": "10-15kg（标准双人床头柜）",
            "ground_friction": "实木地板μ=0.40（干）/0.25（湿），拖拽阻力大",
        },
        "steps": [
            {"step": 1, "action": "环境扫描", "detail": "用激光雷达扫描地面（拖鞋/地毯/线缆），清除障碍物", "duration_s": 20},
            {"step": 2, "action": "抓取准备", "detail": "调整双臂构型，抓取力25N，接触面积≥20cm²（分散压力）", "duration_s": 15},
            {"step": 3, "action": "抬起床头柜", "detail": "缓慢抬起，速度0.08m/s，实时监测重心偏移<5cm", "duration_s": 15},
            {"step": 4, "action": "搬运路径", "detail": "抬高地面前行（不拖拽），速度0.10m/s，路径离墙30cm", "duration_s": 60},
            {"step": 5, "action": "放置就位", "detail": "先轻轻放下再精确定位，检测地面平整度，必要时调整脚轮", "duration_s": 20},
            {"step": 6, "action": "确认与清理", "detail": "视觉确认摆放位置，清理地面灰尘", "duration_s": 20},
        ],
        "quality_metrics": {
            "position_accuracy_mm": "±20",
            "floor_scratch_risk": "low（抓起移动，不拖拽）",
            "path_clearance_mm": "≥50",
        },
    },
}


# ════════════════════════════════════════════════════════════
#  FastAPI 应用
# ════════════════════════════════════════════════════════════

app = FastAPI(
    title="建筑认知Agent API v2.0",
    description="增强版Agent：完整物理常识 + 操作约束",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 请求模型 ──────────────────────────────────────────────

class CommandRequest(BaseModel):
    command: str
    room_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


# ─── 工具函数 ───────────────────────────────────────────────

def detect_task(command: str) -> str:
    """从命令文本识别任务类型（支持复合任务）"""
    cmd = command.lower()
    
    # ═════════════════════════════════════════════════════════
    #  复合任务识别（多动作序列）
    # ═════════════════════════════════════════════════════════
    # "去X拿Y" / "把Y从X拿到Z" / "去X洗Y拿到Z"
    if "去" in command and ("拿" in command or "取" in command or "洗" in command):
        return "compound_fetch"
    # "去X洗Y，拿到Z"
    if "洗" in command and "拿到" in command:
        return "compound_wash_and_deliver"
    # "检查X区域" / "巡检X"
    if "检查" in command or "巡检" in command:
        return "compound_inspect"
    # "打开X然后关闭Y"
    if "然后" in command or "再" in command:
        return "compound_sequence"
    
    # ═════════════════════════════════════════════════════════
    #  单任务识别
    # ═════════════════════════════════════════════════════════
    # 清洁类
    if "淋浴" in command and ("清洁" in command or "擦" in command or "洗" in command):
        return "clean_shower_glass"
    if "玻璃" in command and ("清洁" in command or "擦" in command):
        return "clean_shower_glass"
    if "卧室" in command and "地板" in command:
        return "clean_bedroom_floor"
    if "厨房" in command and ("台面" in command or "清洁" in command):
        return "clean_kitchen_counter"
    if "清洁" in command or "擦" in command or "打扫" in command:
        return "clean_generic"

    # 钻孔类
    if "北墙" in command and ("钻" in command or "孔" in command or "书架" in command):
        return "drill_north_wall_shelf"
    if "东墙" in command and ("钻" in command or "孔" in command or "挂画" in command):
        return "drill_east_wall_picture"
    if "钻" in command or "孔" in command:
        return "drill_generic"

    # 搬运类
    if "床头柜" in command or "移动" in command or "搬" in command:
        return "move_bedside_table"

    # 英文支持
    if any(k in cmd for k in ["clean", "wipe", "wash", "sweep"]):
        return "clean_generic"
    if any(k in cmd for k in ["drill", "hole", "screw"]):
        return "drill_generic"
    if any(k in cmd for k in ["move", "relocate", "carry", "lift"]):
        return "move_generic"

    return "unknown"


# ─── API 端点 ───────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "建筑认知Agent API v2.0",
        "version": "2.0.0",
        "status": "online",
        "features": ["材质物理分析", "操作约束输出", "承重墙检测", "6任务专项优化"],
    }


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "mode": "enhanced_physics",
    }


@app.post("/api/agent/process")
async def process_command(req: CommandRequest):
    """
    处理自然语言指令，返回完整物理分析
    每个任务输出：
    - 材质分析（摩擦/密度/硬度）
    - 机器人操作约束（力度/速度/碰撞阈值）
    - 安全提醒
    - 详细操作步骤（带时间估算）
    - 质量指标
    """
    cmd = command = req.command

    # 识别任务
    task = detect_task(command)

    # ── 任务1：清洁淋浴房玻璃隔断 ──────────────────────
    if task == "clean_shower_glass":
        profile = TASK_PHYSICS_PROFILES["clean_shower_glass"]
        glass = profile["physics_analysis"]["primary"]
        return {
            "task_type": "clean",
            "success": True,
            "task_id": "clean_shower_glass",
            "message": "✅ 淋浴房玻璃清洁任务分析完成",
            "physics": {
                "primary_material": "钢化玻璃",
                "category": glass["category"],
                "friction": {
                    "dry": glass["friction_dry"],
                    "wet": glass["friction_wet"],
                    "note": "淋浴后湿摩擦系数降低48%，机器人底盘防滑系数需≥0.6",
                },
                "collision_threshold_j": glass["collision_threshold_j"],
                "cleaning_constraints": glass["robot_cleaning"],
                "safety": glass["safety_notes"],
                "wet_risk": "high",
                "slip_risk": "high（湿区μ_wet=0.18）",
            },
            "operation": {
                "force_n": {"range": [0.5, 5.0], "optimal": 2.0},
                "speed_m_s": {"max": 0.15, "optimal": 0.08},
                "tool": "软纤维布 + 中性清洁剂",
                "technique": "S型擦拭，速度≤0.08m/s，力度2N",
                "temperature_limit_c": 60,
            },
            "steps": profile["steps"],
            "quality_metrics": profile["quality_metrics"],
            "confidence": 0.95,
        }

    # ── 任务2：东墙钻孔挂画 ─────────────────────────────
    elif task == "drill_east_wall_picture":
        profile = TASK_PHYSICS_PROFILES["drill_east_wall_picture"]
        wall = profile["physics_analysis"]["wall"]
        return {
            "task_type": "drill",
            "success": True,
            "task_id": "drill_east_wall_picture",
            "message": "✅ 东墙钻孔挂画任务分析完成",
            "wall_info": {
                "wall": "east",
                "label": "东墙",
                "material": "砖墙",
                "thickness_cm": 12,
                "drill_allowed": True,
                "max_depth_mm": 35,
            },
            "physics": {
                "wall_material": "砖墙",
                "density_kg_m3": wall["density_kg_m3"],
                "friction": {"dry": wall["friction_dry"], "wet": wall["friction_wet"]},
                "hardness_mohs": wall["hardness_mohs"],
                "compressive_strength_mpa": wall["compressive_strength_mpa"],
                "drill_parameters": wall["drill"],
                "safety": wall["safety_notes"],
            },
            "operation": {
                "torque_nm": {"optimal": 14, "range": [10, 18]},
                "rpm": {"optimal": 750, "range": [600, 900]},
                "drill_bit": "6mm硬质合金钻头",
                "max_depth_mm": 35,
                "dust_extraction": "必须开启",
            },
            "pre_checks": profile["pre_checks"],
            "steps": profile["steps"],
            "quality_metrics": profile["quality_metrics"],
            "confidence": 0.93,
        }

    # ── 任务3：北墙钻孔书架（承重墙，禁止）──────────────
    elif task == "drill_north_wall_shelf":
        profile = TASK_PHYSICS_PROFILES["drill_north_wall_shelf"]
        return {
            "task_type": "drill",
            "success": False,
            "task_id": "drill_north_wall_shelf",
            "message": "🚫 禁止钻孔：北墙为承重墙（剪力墙）",
            "block_reason": profile["block_reason"],
            "block_code": profile["block_code"],
            "wall_info": {
                "wall": "north",
                "label": "北墙",
                "material": "混凝土墙体",
                "thickness_cm": 24,
                "load_bearing": True,
                "reinforcement": "有钢筋",
                "drill_allowed": False,
            },
            "physics": {
                "wall_material": "混凝土墙体",
                "density_kg_m3": 2400,
                "compressive_strength_mpa": 30,
                "drill_risk": "钻孔破坏钢筋 = 结构安全隐患",
                "safety": ["严禁破坏承重墙", "剪力墙是建筑抗震核心构件", "违规钻孔违反《建筑法》第70条"],
            },
            "alternative": profile["alternative"],
            "confidence": 0.99,
        }

    # ── 任务4：清洁卧室实木地板 ─────────────────────────
    elif task == "clean_bedroom_floor":
        profile = TASK_PHYSICS_PROFILES["clean_bedroom_floor"]
        floor = profile["physics_analysis"]["floor"]
        return {
            "task_type": "clean",
            "success": True,
            "task_id": "clean_bedroom_floor",
            "message": "✅ 卧室实木地板清洁任务分析完成",
            "physics": {
                "primary_material": "实木地板",
                "category": floor["category"],
                "density_kg_m3": floor["density_kg_m3"],
                "friction": {
                    "dry": floor["friction_dry"],
                    "wet": floor["friction_wet"],
                    "note": "实木地板湿摩擦系数降低37%，清洁后需及时干燥",
                },
                "hardness_mohs": floor["hardness_mohs"],
                "water_absorption_pct": floor["water_absorption_pct"],
                "humidity_limit_pct": floor["robot_cleaning"]["humidity_limit_pct"],
                "safety": floor["safety_notes"],
                "scratch_risk": "high（Mohs 2.5，力度>3N即划伤）",
            },
            "operation": {
                "force_n": {"range": [0.3, 3.0], "optimal": 1.0},
                "speed_m_s": {"max": 0.25, "optimal": 0.12},
                "tool": "微纤维布（干湿两用）",
                "technique": "顺木纹方向，速度≤0.12m/s",
                "moisture_limit_pct": 30,
                "humidity_range": "30-45%（防变形/发霉）",
            },
            "steps": profile["steps"],
            "quality_metrics": profile["quality_metrics"],
            "confidence": 0.94,
        }

    # ── 任务5：清洁厨房不锈钢台面 ──────────────────────
    elif task == "clean_kitchen_counter":
        profile = TASK_PHYSICS_PROFILES["clean_kitchen_counter"]
        counter = profile["physics_analysis"]["counter"]
        return {
            "task_type": "clean",
            "success": True,
            "task_id": "clean_kitchen_counter",
            "message": "✅ 厨房不锈钢台面清洁任务分析完成",
            "physics": {
                "primary_material": "不锈钢台面",
                "material": counter["material"],
                "density_kg_m3": counter["density_kg_m3"],
                "friction": {
                    "dry": counter["friction_dry"],
                    "wet": counter["friction_wet"],
                    "note": "不锈钢湿摩擦系数仅0.12，油污未清理前机器人极易打滑",
                },
                "hardness_mohs": counter["hardness_mohs"],
                "thermal_conductivity_w_mk": counter["thermal_conductivity_w_mk"],
                "safety": counter["safety_notes"],
                "slip_risk": "high（湿态μ=0.12，极低）",
                "sharp_edge_risk": "medium（台面R角<1mm）",
            },
            "operation": {
                "force_n": {"range": [0.5, 4.0], "optimal": 1.5},
                "speed_m_s": {"max": 0.20, "optimal": 0.10},
                "tool": "柔软海绵 + 中性去油清洁剂（pH 6-8）",
                "technique": "单向擦拭，最后用干布抛光",
                "surface_temp_limit_c": 40,
            },
            "steps": profile["steps"],
            "quality_metrics": profile["quality_metrics"],
            "confidence": 0.93,
        }

    # ── 任务6：移动床头柜 ────────────────────────────────
    elif task == "move_bedside_table":
        profile = TASK_PHYSICS_PROFILES["move_bedside_table"]
        furniture = profile["physics_analysis"]["furniture"]
        floor = profile["secondary_context"]["floor_physics"]
        return {
            "task_type": "move",
            "success": True,
            "task_id": "move_bedside_table",
            "message": "✅ 床头柜搬运任务分析完成",
            "physics": {
                "furniture_material": "木质家具",
                "density_kg_m3": furniture["density_kg_m3"],
                "weight_kg_range": furniture["weight_kg_range"],
                "friction_dry": furniture["friction_dry"],
                "grasp_force_n": {"range": [15, 40], "optimal": 25},
                "safety": furniture["safety_notes"],
                "ground_context": {
                    "floor": "实木地板",
                    "floor_friction_dry": floor["friction_dry"],
                    "floor_friction_wet": floor["friction_wet"],
                    "note": "抬起搬运比拖拽好（实木地板拖拽摩擦阻力大且易划伤）",
                },
            },
            "operation": {
                "grasp_force_n": {"optimal": 25, "range": [15, 40]},
                "lifting_speed_m_s": {"max": 0.15, "optimal": 0.08},
                "clearance_mm": furniture["robot_move"]["clearance_mm"],
                "technique": "抬起搬运（不拖拽），路径离墙≥30cm",
                "floor_protection": "抓起移动，防止划伤地板",
            },
            "steps": profile["steps"],
            "quality_metrics": profile["quality_metrics"],
            "confidence": 0.91,
        }

    # ── 通用清洁任务 ───────────────────────────────────
    elif task == "clean_generic":
        return {
            "task_type": "clean",
            "success": True,
            "message": "✅ 清洁任务分析完成",
            "physics": {
                "materials": [
                    MATERIAL_PHYSICS["瓷砖"],
                    MATERIAL_PHYSICS["钢化玻璃"],
                ],
                "wet_risk": "中-高（湿区）",
                "slip_risk": "高（湿区地面）",
            },
            "steps": [
                {"step": 1, "action": "材质识别", "detail": "视觉+触觉识别表面材质类型", "duration_s": 10},
                {"step": 2, "action": "安全评估", "detail": "评估湿滑风险，配置防滑底盘", "duration_s": 15},
                {"step": 3, "action": "清洁执行", "detail": "按材质对应力度/速度执行清洁", "duration_s": 120},
                {"step": 4, "action": "效果检验", "detail": "视觉检查清洁效果，不合格区域重清洁", "duration_s": 30},
            ],
            "confidence": 0.85,
        }

    # ── 通用钻孔任务 ───────────────────────────────────
    elif task == "drill_generic":
        wall_match = re.search(r'([东南西北])墙', command)
        wall_key_map = {"东": "east", "西": "west", "南": "south", "北": "north"}
        wall_key = "east"
        if wall_match:
            wall_key = wall_key_map.get(wall_match.group(1), "east")
        wall_data = WALLS.get(wall_key, {})

        if wall_data.get("load_bearing", False):
            return {
                "task_type": "drill",
                "success": False,
                "message": f"🚫 禁止钻孔：{wall_data['label']}为承重墙",
                "wall_info": wall_data,
                "physics": {
                    "wall_material": wall_data["material"],
                    "safety": ["严禁破坏承重墙", "剪力墙是建筑抗震核心构件"],
                },
                "alternative": {
                    "suggestion": "在非承重墙（东墙/西墙/南墙）钻孔",
                },
                "confidence": 0.99,
            }
        else:
            mat = wall_data.get("material", "砖墙")
            mat_data = MATERIAL_PHYSICS.get(mat, MATERIAL_PHYSICS["砖墙"])
            return {
                "task_type": "drill",
                "success": True,
                "message": f"✅ {wall_data['label']}钻孔任务分析完成（{mat}）",
                "wall_info": wall_data,
                "physics": {
                    "wall_material": mat,
                    "drill_parameters": mat_data.get("drill", {}),
                    "safety": mat_data.get("safety_notes", []),
                },
                "operation": {
                    "torque_nm": mat_data.get("drill", {}).get("torque_nm", {}).get("optimal", 14),
                    "rpm": mat_data.get("drill", {}).get("rpm", {}).get("optimal", 750),
                    "max_depth_mm": wall_data.get("max_depth_mm", 35),
                },
                "steps": [
                    {"step": 1, "action": "预检", "detail": "确认墙体材质、避开钢筋/管线", "duration_s": 30},
                    {"step": 2, "action": "钻孔", "detail": "垂直钻进，速率60mm/min，深度35mm", "duration_s": 40},
                    {"step": 3, "action": "清孔", "detail": "吸尘器清除粉尘", "duration_s": 15},
                    {"step": 4, "action": "安装", "detail": "膨胀螺栓+挂件", "duration_s": 20},
                ],
                "confidence": 0.90,
            }

    # ── 通用搬运任务 ───────────────────────────────────
    elif task == "move_generic":
        return {
            "task_type": "move",
            "success": True,
            "message": "✅ 搬运任务分析完成",
            "physics": {
                "furniture_material": "木质家具",
                "grasp_force_n": {"range": [15, 40], "optimal": 25},
                "safety": ["力度>40N会在木质表面留下压痕", "抬起搬运优于拖拽"],
            },
            "steps": [
                {"step": 1, "action": "扫描", "detail": "激光雷达扫描地面障碍物", "duration_s": 20},
                {"step": 2, "action": "抓取", "detail": "抓取力25N，接触面积≥20cm²", "duration_s": 15},
                {"step": 3, "action": "搬运", "detail": "抬起移动，速度≤0.10m/s", "duration_s": 60},
                {"step": 4, "action": "就位", "detail": "精确放置，水平仪确认", "duration_s": 20},
            ],
            "confidence": 0.85,
        }

    # ═════════════════════════════════════════════════════════
    #  复合任务处理
    # ═════════════════════════════════════════════════════════
    elif task == "compound_wash_and_deliver":
        # 解析 "去厨房洗水果，拿到客厅茶几上"
        import re
        src_match = re.search(r"去(.+?)洗", command)
        obj_match = re.search(r"洗(.+?)，", command)
        dst_match = re.search(r"拿到(.+?)(上|$)", command)
        src = src_match.group(1) if src_match else "厨房"
        obj = obj_match.group(1) if obj_match else "物品"
        dst = dst_match.group(1) if dst_match else "目标位置"
        return {
            "task_type": "compound",
            "success": True,
            "message": f"✅ 复合任务解析完成：去{src}洗{obj}，拿到{dst}",
            "subtasks": [
                {"step": 1, "action": "导航", "target": src, "detail": f"移动到{src}", "duration_s": 30},
                {"step": 2, "action": "取物", "target": obj, "detail": f"识别并抓取{obj}", "duration_s": 15},
                {"step": 3, "action": "清洗", "target": obj, "detail": f"清洗{obj}（水流速度0.5L/min）", "duration_s": 45},
                {"step": 4, "action": "搬运", "target": dst, "detail": f"移动到{dst}", "duration_s": 30},
                {"step": 5, "action": "放置", "target": dst, "detail": f"放置在{dst}，力度<5N", "duration_s": 10},
            ],
            "physics": {
                "grasp_force_n": {"range": [5, 15], "optimal": 10, "note": "水果类物品力度需轻柔"},
                "water_flow_l_min": 0.5,
                "move_speed_m_s": 0.15,
                "place_force_n": 5,
            },
            "safety": ["水果表面光滑，抓取需吸盘或软夹爪", "清洗后表面湿滑，搬运需防跌落"],
            "confidence": 0.85,
        }
    
    elif task == "compound_fetch":
        # 解析 "去卧室拿手机" / "把书从书房拿到客厅"
        import re
        src_match = re.search(r"去(.+?)(拿|取)", command)
        obj_match = re.search(r"(拿|取)(.+?)(从|$)", command)
        dst_match = re.search(r"到(.+?)(上|$)", command)
        src = src_match.group(1) if src_match else "起点"
        obj = obj_match.group(2) if obj_match else "物品"
        dst = dst_match.group(1) if dst_match else "目标位置"
        return {
            "task_type": "compound",
            "success": True,
            "message": f"✅ 取物任务解析完成：从{src}取{obj}送到{dst}",
            "subtasks": [
                {"step": 1, "action": "导航", "target": src, "detail": f"移动到{src}", "duration_s": 25},
                {"step": 2, "action": "识别", "target": obj, "detail": f"视觉识别{obj}", "duration_s": 5},
                {"step": 3, "action": "抓取", "target": obj, "detail": f"抓取{obj}，力度10N", "duration_s": 10},
                {"step": 4, "action": "搬运", "target": dst, "detail": f"移动到{dst}", "duration_s": 30},
                {"step": 5, "action": "放置", "target": dst, "detail": f"放置在{dst}", "duration_s": 8},
            ],
            "physics": {"grasp_force_n": 10, "move_speed_m_s": 0.20},
            "confidence": 0.80,
        }
    
    elif task == "compound_inspect":
        return {
            "task_type": "compound",
            "success": True,
            "message": "✅ 巡检任务解析完成",
            "subtasks": [
                {"step": 1, "action": "扫描", "detail": "激光雷达扫描区域", "duration_s": 20},
                {"step": 2, "action": "检测", "detail": "视觉检测异常项", "duration_s": 30},
                {"step": 3, "action": "记录", "detail": "生成巡检报告", "duration_s": 10},
            ],
            "confidence": 0.75,
        }
    
    elif task == "compound_sequence":
        return {
            "task_type": "compound",
            "success": True,
            "message": "✅ 序列任务解析完成",
            "hint": "多步骤任务，需按顺序执行",
            "confidence": 0.70,
        }

    # ── 未知任务 ────────────────────────────────────────
    else:
        return {
            "task_type": "unknown",
            "success": False,
            "message": f"⚠️ 无法识别的任务类型：{command}",
            "hint": "支持：清洁（淋浴/地板/台面）、钻孔（东墙/北墙）、搬运（床头柜）、复合任务（去X洗Y拿到Z）",
            "confidence": 0.5,
        }


@app.post("/api/constraint/check-drill")
async def check_drill(wall: str = "east"):
    """钻孔约束检查"""
    wall_data = WALLS.get(wall, WALLS["east"])
    return {
        "wall": wall,
        "label": wall_data["label"],
        "drill_allowed": wall_data["drill_allowed"],
        "reason": wall_data.get("reason", "非承重墙，可以钻孔"),
        "wall_data": wall_data,
        "physics": MATERIAL_PHYSICS.get(wall_data["material"], {}),
    }


@app.get("/api/materials")
async def get_materials():
    """获取完整材质物理参数库"""
    return {"materials": MATERIAL_PHYSICS}


@app.get("/api/walls")
async def get_walls():
    """获取墙体数据"""
    return {"walls": WALLS}


@app.get("/api/tasks")
async def get_tasks():
    """获取所有预设任务物理档案"""
    return {
        "tasks": {k: {kk: vv for kk, vv in v.items() if kk != "physics_analysis"}
                  for k, v in TASK_PHYSICS_PROFILES.items()},
    }


# ════════════════════════════════════════════════════════════
#  启动
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("[Agent API v2.0] 启动增强版服务器...")
    print("[Agent API] 端口: 5002")
    print("[Agent API] 物理材质库: 8种材质")
    print("[Agent API] 预设任务: 6个专项优化")
    uvicorn.run(app, host="127.0.0.1", port=5002, log_level="info")
