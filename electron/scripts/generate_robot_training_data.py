"""
建筑数据 -> 机器人训练数据生成器
输入：CAD施工图(PDF/DWG) + 效果图(JPG)
输出：结构化训练样本 JSON
"""
import os
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime

# ============================================================
# 配置
# ============================================================
DATA_ROOT = Path(r"C:\Users\Administrator\Desktop\建筑数据库\家庭别墅")
OUT_DIR   = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\training")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 场景知识库（人工标注，基于文件名推断）
# ============================================================
SCENE_KNOWLEDGE = {
    "家庭场景": {
        "scene_type": "residential_interior",
        "label": "家庭室内",
        "rooms": ["客厅", "卧室", "餐厅", "厨房", "卫生间", "阳台"],
        "typical_objects": {
            "客厅": ["沙发", "茶几", "电视柜", "落地灯", "地毯", "窗帘"],
            "卧室": ["床", "衣柜", "床头柜", "梳妆台", "台灯"],
            "餐厅": ["餐桌", "餐椅", "餐边柜", "吊灯"],
            "厨房": ["橱柜", "冰箱", "洗碗机", "灶台", "抽油烟机"],
            "卫生间": ["马桶", "洗手盆", "淋浴房", "浴缸", "镜柜"],
            "阳台": ["洗衣机", "晾衣架", "绿植", "休闲椅"],
        },
        "robot_tasks": [
            {"task": "清洁地板", "action_seq": ["navigate_to_room", "deploy_mop", "sweep_path", "return_base"], "risk": "LOW"},
            {"task": "整理沙发", "action_seq": ["navigate_to_sofa", "pick_cushion", "place_cushion", "fold_blanket"], "risk": "LOW"},
            {"task": "浇花", "action_seq": ["pick_watering_can", "fill_water", "navigate_to_plant", "pour_water"], "risk": "LOW"},
            {"task": "取快递", "action_seq": ["navigate_to_door", "open_door", "pick_package", "place_package"], "risk": "MEDIUM"},
            {"task": "洗碗", "action_seq": ["collect_dishes", "navigate_to_sink", "wash_dishes", "place_rack"], "risk": "LOW"},
            {"task": "整理床铺", "action_seq": ["navigate_to_bedroom", "pull_sheet", "fold_quilt", "arrange_pillow"], "risk": "LOW"},
        ],
        "physics": {
            "floor_friction": 0.4,
            "ceiling_height_m": 2.8,
            "door_width_m": 0.9,
            "corridor_width_m": 1.2,
        }
    },
    "办公空间": {
        "scene_type": "office_interior",
        "label": "办公室内",
        "rooms": ["开放办公区", "会议室", "接待区", "茶水间", "卫生间"],
        "typical_objects": {
            "开放办公区": ["工位", "电脑", "椅子", "文件柜", "打印机"],
            "会议室": ["会议桌", "会议椅", "投影仪", "白板", "显示屏"],
            "接待区": ["前台", "沙发", "茶几", "绿植", "展示架"],
            "茶水间": ["咖啡机", "微波炉", "冰箱", "水槽", "储物柜"],
        },
        "robot_tasks": [
            {"task": "清洁办公区", "action_seq": ["navigate_to_office", "deploy_vacuum", "clean_path", "return_base"], "risk": "LOW"},
            {"task": "送文件", "action_seq": ["pick_document", "navigate_to_target", "hand_document", "return"], "risk": "LOW"},
            {"task": "倒垃圾", "action_seq": ["navigate_to_bin", "pick_bin", "navigate_to_trash", "empty_bin", "return_bin"], "risk": "LOW"},
            {"task": "引导访客", "action_seq": ["greet_visitor", "navigate_lead", "arrive_destination", "notify_host"], "risk": "LOW"},
        ],
        "physics": {
            "floor_friction": 0.5,
            "ceiling_height_m": 3.0,
            "door_width_m": 1.0,
            "corridor_width_m": 1.5,
        }
    },
}

# 客户项目知识（基于目录名）
CLIENT_PROJECTS = {
    "山水庭院": {
        "project_type": "villa_courtyard",
        "label": "山水庭院别墅",
        "style": "新中式",
        "area_sqm": 350,
        "floors": 3,
        "features": ["庭院", "水景", "假山", "廊道", "茶室"],
        "has_cad": False,
        "has_renderings": False,  # 只有链接文档
        "has_pdf_plan": True,
    },
    "从化别墅": {
        "project_type": "villa",
        "label": "从化别墅",
        "style": "现代简约",
        "area_sqm": 480,
        "floors": 3,
        "features": ["地下室", "游泳池", "车库", "露台"],
        "has_cad": False,
        "has_renderings": False,
        "has_pdf_plan": True,
    },
    "黄总": {
        "project_type": "villa",
        "label": "黄总别墅",
        "style": "现代轻奢",
        "area_sqm": 320,
        "floors": 3,
        "features": ["地下室", "露台", "庭院"],
        "has_cad": False,
        "has_renderings": True,
        "has_pdf_plan": True,
    },
    "李女士": {
        "project_type": "apartment",
        "label": "李女士公寓",
        "style": "现代简约",
        "area_sqm": 130,
        "floors": 1,
        "features": ["开放式厨房", "主卧套间", "阳台"],
        "has_cad": False,
        "has_renderings": True,
        "has_pdf_plan": True,
    },
    "覃总": {
        "project_type": "villa",
        "label": "覃总别墅",
        "style": "现代奢华",
        "area_sqm": 420,
        "floors": 4,
        "features": ["地下室", "电梯", "游泳池", "影音室"],
        "has_cad": False,
        "has_renderings": True,
        "has_pdf_plan": True,
    },
    "王总": {
        "project_type": "villa_garden",
        "label": "王总云涧花园",
        "style": "新中式园林",
        "area_sqm": 600,
        "floors": 3,
        "features": ["园林", "水景", "亭台", "廊道", "茶室"],
        "has_cad": False,
        "has_renderings": True,
        "has_pdf_plan": True,
    },
    "室内施工图": {
        "花月半岛": {"project_type": "apartment", "area_sqm": 120, "style": "现代简约"},
        "桔山湖":   {"project_type": "apartment", "area_sqm": 140, "style": "轻奢"},
        "鹿城":     {"project_type": "apartment", "area_sqm": 160, "style": "现代"},
        "万昌康城": {"project_type": "apartment", "area_sqm": 110, "style": "简约"},
    }
}

# ============================================================
# 机器人任务模板（通用）
# ============================================================
ROBOT_TASK_TEMPLATES = [
    # 清洁类
    {"intent": "清洁地板", "category": "cleaning",
     "actions": ["navigate({room})", "deploy_tool(mop)", "execute_path(zigzag)", "return_base()"],
     "constraints": ["floor_clear", "no_obstacles"], "risk": "LOW", "force_n": 5},
    {"intent": "吸尘", "category": "cleaning",
     "actions": ["navigate({room})", "deploy_tool(vacuum)", "execute_path(spiral)", "return_base()"],
     "constraints": ["floor_clear"], "risk": "LOW", "force_n": 3},
    {"intent": "擦窗户", "category": "cleaning",
     "actions": ["navigate(window)", "extend_arm(1.5m)", "apply_cleaner()", "wipe_motion(horizontal)"],
     "constraints": ["height_reachable", "stable_surface"], "risk": "MEDIUM", "force_n": 15},

    # 搬运类
    {"intent": "搬椅子", "category": "manipulation",
     "actions": ["navigate({object})", "grasp(chair_back)", "lift(0.1m)", "navigate({target})", "place()"],
     "constraints": ["weight_limit_10kg", "path_clear"], "risk": "LOW", "force_n": 80},
    {"intent": "移动沙发", "category": "manipulation",
     "actions": ["navigate(sofa)", "grasp(sofa_arm)", "push(direction)", "verify_position()"],
     "constraints": ["weight_limit_50kg", "floor_protection"], "risk": "HIGH", "force_n": 220},
    {"intent": "搬运箱子", "category": "manipulation",
     "actions": ["navigate({object})", "assess_weight()", "grasp(box)", "lift()", "navigate({target})", "place()"],
     "constraints": ["weight_limit_20kg"], "risk": "MEDIUM", "force_n": 120},

    # 服务类
    {"intent": "送水", "category": "service",
     "actions": ["navigate(kitchen)", "pick(water_bottle)", "navigate({target_person})", "hand_over()"],
     "constraints": ["liquid_stable", "path_clear"], "risk": "LOW", "force_n": 10},
    {"intent": "送餐", "category": "service",
     "actions": ["navigate(kitchen)", "pick(food_tray)", "navigate({target})", "place_tray()", "notify()"],
     "constraints": ["tray_balanced", "temperature_safe"], "risk": "MEDIUM", "force_n": 15},
    {"intent": "开门", "category": "interaction",
     "actions": ["navigate(door)", "grasp(handle)", "rotate(90deg)", "push/pull(door)", "hold_open()"],
     "constraints": ["door_unlocked"], "risk": "LOW", "force_n": 30},

    # 监控类
    {"intent": "巡逻检查", "category": "monitoring",
     "actions": ["execute_path(patrol_route)", "scan_environment()", "detect_anomaly()", "report()"],
     "constraints": ["path_accessible"], "risk": "LOW", "force_n": 0},
    {"intent": "检查漏水", "category": "monitoring",
     "actions": ["navigate(bathroom)", "scan_floor(moisture_sensor)", "check_pipes()", "report_status()"],
     "constraints": ["sensor_active"], "risk": "LOW", "force_n": 0},
]

# ============================================================
# 生成训练样本
# ============================================================
def make_sample_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]

def generate_scene_samples(scene_name: str, scene_info: dict, image_paths: list) -> list:
    """为一个场景生成训练样本"""
    samples = []

    for task in scene_info["robot_tasks"]:
        for room in scene_info["rooms"]:
            sample = {
                "id": make_sample_id(f"{scene_name}_{room}_{task['task']}"),
                "source": "local_data",
                "scene_type": scene_info["scene_type"],
                "scene_label": scene_info["label"],
                "room": room,
                "task": task["task"],
                "action_sequence": [a.replace("{room}", room) for a in task["action_seq"]],
                "risk_level": task["risk"],
                "physics": scene_info["physics"],
                "objects": scene_info["typical_objects"].get(room, []),
                "image_count": len(image_paths),
                "image_samples": [str(p).replace(str(DATA_ROOT), "").lstrip("\\") for p in image_paths[:3]],
                "created_at": datetime.now().isoformat(),
            }
            samples.append(sample)

    return samples

def generate_task_samples(project_name: str, project_info: dict) -> list:
    """为一个客户项目生成机器人任务样本"""
    samples = []

    for tmpl in ROBOT_TASK_TEMPLATES:
        sample = {
            "id": make_sample_id(f"{project_name}_{tmpl['intent']}"),
            "source": "local_project",
            "project": project_name,
            "project_type": project_info.get("project_type", "unknown"),
            "style": project_info.get("style", ""),
            "area_sqm": project_info.get("area_sqm", 0),
            "floors": project_info.get("floors", 1),
            "features": project_info.get("features", []),
            "intent": tmpl["intent"],
            "category": tmpl["category"],
            "action_sequence": tmpl["actions"],
            "constraints": tmpl["constraints"],
            "risk_level": tmpl["risk"],
            "required_force_n": tmpl["force_n"],
            "robot_capable": tmpl["force_n"] <= 200,  # 机器人最大200N
            "has_cad": project_info.get("has_cad", False),
            "has_renderings": project_info.get("has_renderings", False),
            "created_at": datetime.now().isoformat(),
        }
        samples.append(sample)

    return samples

def generate_cad_samples(dwg_files: list) -> list:
    """为DWG施工图生成空间理解样本"""
    samples = []
    cad_projects = CLIENT_PROJECTS["室内施工图"]

    for dwg_path in dwg_files:
        name = Path(dwg_path).stem
        info = cad_projects.get(name, {"project_type": "apartment", "area_sqm": 120, "style": "现代"})

        # 生成空间推理样本
        for task in ROBOT_TASK_TEMPLATES:
            sample = {
                "id": make_sample_id(f"cad_{name}_{task['intent']}"),
                "source": "cad_drawing",
                "project": name,
                "file": str(dwg_path).replace(str(DATA_ROOT), "").lstrip("\\"),
                "project_type": info["project_type"],
                "area_sqm": info["area_sqm"],
                "style": info["style"],
                "intent": task["intent"],
                "category": task["category"],
                "action_sequence": task["actions"],
                "constraints": task["constraints"],
                "risk_level": task["risk"],
                "required_force_n": task["force_n"],
                "robot_capable": task["force_n"] <= 200,
                "spatial_reasoning": {
                    "needs_floor_plan": True,
                    "needs_room_detection": True,
                    "needs_obstacle_map": True,
                },
                "created_at": datetime.now().isoformat(),
            }
            samples.append(sample)

    return samples

# ============================================================
# 主流程
# ============================================================
def main():
    all_samples = []
    stats = {}

    print("=" * 60)
    print("建筑数据 -> 机器人训练数据生成器")
    print("=" * 60)

    # 1. 室内场景图片样本
    print("\n[1] 处理室内场景图片...")
    for scene_name, scene_info in SCENE_KNOWLEDGE.items():
        scene_dir = DATA_ROOT / "室内家居场景jpg" / scene_name
        if scene_dir.exists():
            images = list(scene_dir.glob("*.jpg")) + list(scene_dir.glob("*.png"))
            samples = generate_scene_samples(scene_name, scene_info, images)
            all_samples.extend(samples)
            stats[scene_name] = len(samples)
            print(f"  {scene_name}: {len(images)} 张图 -> {len(samples)} 条样本")

    # 2. 客户项目样本
    print("\n[2] 处理客户项目...")
    for client_name, project_info in CLIENT_PROJECTS.items():
        if client_name == "室内施工图":
            continue
        client_dir = DATA_ROOT / client_name
        if client_dir.exists():
            samples = generate_task_samples(client_name, project_info)
            all_samples.extend(samples)
            stats[client_name] = len(samples)
            print(f"  {client_name}: {len(samples)} 条样本")

    # 3. CAD施工图样本
    print("\n[3] 处理CAD施工图...")
    cad_dir = DATA_ROOT / "室内施工图"
    if cad_dir.exists():
        dwg_files = list(cad_dir.glob("*.dwg"))
        samples = generate_cad_samples(dwg_files)
        all_samples.extend(samples)
        stats["室内施工图"] = len(samples)
        print(f"  {len(dwg_files)} 个DWG -> {len(samples)} 条样本")

    # 4. 去重
    seen = set()
    unique_samples = []
    for s in all_samples:
        if s["id"] not in seen:
            seen.add(s["id"])
            unique_samples.append(s)

    print(f"\n[DONE] 总计: {len(unique_samples)} 条唯一训练样本")
    print(f"  去重前: {len(all_samples)}, 去重后: {len(unique_samples)}")

    # 5. 保存
    out_file = OUT_DIR / "robot_training_data.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "meta": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "total_samples": len(unique_samples),
                "source": "local_building_database",
                "data_root": str(DATA_ROOT),
                "stats": stats,
            },
            "samples": unique_samples,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVED] {out_file}")
    print(f"  文件大小: {out_file.stat().st_size / 1024:.1f} KB")

    # 6. 按类别统计
    from collections import Counter
    cats = Counter(s.get("category", s.get("scene_type", "unknown")) for s in unique_samples)
    print("\n[分类统计]")
    for cat, cnt in cats.most_common():
        print(f"  {cat}: {cnt}")

    return unique_samples

if __name__ == "__main__":
    main()
