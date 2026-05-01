"""
完整建筑数据库扫描 -> 机器人训练数据生成器 V2
覆盖：家庭别墅 / 地产综合体 / 产业园 / 酒店场景 / 电气CAD / 南沙星河东悦湾 等
"""
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# ============================================================
# 配置
# ============================================================
DATA_ROOT = Path(r"C:\Users\Administrator\Desktop\建筑数据库")
OUT_DIR   = Path(r"C:\Users\Administrator\.qclaw\workspace\projects\building-physical-ai\data\training")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 场景类型定义
# ============================================================
SCENE_TYPES = {
    # 住宅类
    "家庭别墅": {
        "type": "residential_villa",
        "label": "家庭别墅",
        "subtypes": ["独栋", "联排", "双拼", "叠拼"],
        "rooms": ["客厅", "餐厅", "主卧", "次卧", "厨房", "卫生间", "书房", "阳台", "庭院"],
        "robot_tasks": ["清洁", "整理", "安防巡逻", "浇花", "取快递", "垃圾分类"],
    },
    "室内家居场景jpg": {
        "type": "residential_interior",
        "label": "家庭室内场景",
        "subtypes": ["客厅", "卧室", "餐厅", "厨房"],
        "rooms": ["客厅", "卧室", "餐厅", "厨房", "卫生间"],
        "robot_tasks": ["清洁地板", "整理沙发", "擦窗户", "洗碗", "浇花"],
    },

    # 商业类
    "地产综合体佛山恒大云东海": {
        "type": "commercial_complex",
        "label": "商业综合体",
        "subtypes": ["购物中心", "写字楼", "酒店", "公寓"],
        "rooms": ["商业区", "办公区", "餐饮区", "公共走廊", "停车场"],
        "robot_tasks": ["清洁走廊", "引导访客", "送餐", "安防巡逻", "设备巡检"],
    },
    "产业园": {
        "type": "industrial_park",
        "label": "产业园",
        "subtypes": ["办公楼", "研发中心", "厂房", "仓库"],
        "rooms": ["办公室", "会议室", "实验室", "仓库", "走廊"],
        "robot_tasks": ["清洁", "搬运物料", "巡逻检查", "环境监测", "设备巡检"],
    },
    "酒店场景": {
        "type": "hotel",
        "label": "酒店场景",
        "subtypes": ["客房", "大堂", "餐厅", "会议室", "健身房"],
        "rooms": ["客房", "大堂", "餐厅", "会议室", "走廊"],
        "robot_tasks": ["送物服务", "清洁房间", "引导客人", "布草搬运", "行李运输"],
    },

    # 工程类
    "电气CAD施工图": {
        "type": "electrical_engineering",
        "label": "电气施工图",
        "subtypes": ["照明", "动力", "弱电", "消防"],
        "rooms": ["配电室", "控制室", "设备间"],
        "robot_tasks": ["线路巡检", "设备检查", "故障诊断", "维护提醒"],
    },
    "南沙星河东悦湾": {
        "type": "residential_complex",
        "label": "住宅小区",
        "subtypes": ["高层住宅", "地下车库", "商业配套"],
        "rooms": ["公共走廊", "电梯厅", "地下车库", "花园"],
        "robot_tasks": ["清洁公共区域", "巡逻安保", "垃圾清运", "绿化维护"],
    },
}

# ============================================================
# 机器人动作模板
# ============================================================
ACTION_TEMPLATES = {
    "清洁": {
        "actions": ["navigate({room})", "deploy_tool(mop/vacuum)", "execute_path(zigzag)", "return_base()"],
        "risk": "LOW", "force_n": 5, "duration_min": 15
    },
    "整理": {
        "actions": ["navigate({room})", "identify_objects()", "pick_place_sequence()", "verify_order()"],
        "risk": "LOW", "force_n": 30, "duration_min": 10
    },
    "安防巡逻": {
        "actions": ["start_patrol_route()", "scan_environment()", "detect_anomaly()", "report_status()"],
        "risk": "LOW", "force_n": 0, "duration_min": 30
    },
    "浇花": {
        "actions": ["navigate(garden)", "pick_watering_can", "fill_water", "water_plants()", "return_tools()"],
        "risk": "LOW", "force_n": 15, "duration_min": 20
    },
    "取快递": {
        "actions": ["navigate(door)", "open_door", "pick_package()", "navigate({target_room})", "place_package()"],
        "risk": "MEDIUM", "force_n": 50, "duration_min": 5
    },
    "垃圾分类": {
        "actions": ["navigate(trash_area)", "scan_trash()", "classify_waste()", "sort_bins()", "report_fill()"],
        "risk": "LOW", "force_n": 20, "duration_min": 10
    },
    "引导访客": {
        "actions": ["greet(visitor)", "identify_destination()", "lead_path()", "notify_host()"],
        "risk": "LOW", "force_n": 0, "duration_min": 5
    },
    "送餐": {
        "actions": ["navigate(kitchen)", "pick_food_tray()", "navigate({target})", "place_tray()", "notify()"],
        "risk": "MEDIUM", "force_n": 15, "duration_min": 3
    },
    "送物服务": {
        "actions": ["pick_item({item})", "navigate({room})", "knock_door()", "hand_item()", "confirm_receipt()"],
        "risk": "LOW", "force_n": 20, "duration_min": 3
    },
    "搬运物料": {
        "actions": ["navigate(warehouse)", "pick_material()", "lift_safely()", "navigate({target})", "place_material()"],
        "risk": "HIGH", "force_n": 150, "duration_min": 10
    },
    "线路巡检": {
        "actions": ["navigate(electrical_room)", "scan_panels()", "read_meters()", "detect_anomaly()", "report()"],
        "risk": "MEDIUM", "force_n": 0, "duration_min": 20
    },
    "设备检查": {
        "actions": ["navigate({device})", "scan_device()", "check_parameters()", "log_status()"],
        "risk": "LOW", "force_n": 0, "duration_min": 5
    },
}

# ============================================================
# 辅助函数
# ============================================================
def make_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]

def scan_directory(base_path: Path) -> dict:
    """扫描目录，返回文件统计"""
    stats = defaultdict(lambda: {"count": 0, "size_mb": 0, "files": []})

    for f in base_path.rglob("*"):
        if f.is_file():
            ext = f.suffix.lower()
            category = f.parent.name
            stats[category]["count"] += 1
            stats[category]["size_mb"] += f.stat().st_size / (1024 * 1024)
            stats[category]["files"].append(str(f))

    return dict(stats)

def generate_samples_from_scene(scene_name: str, scene_info: dict, file_stats: dict) -> list:
    """从场景生成训练样本"""
    samples = []

    for task_name in scene_info["robot_tasks"]:
        task_info = ACTION_TEMPLATES.get(task_name, ACTION_TEMPLATES["清洁"])

        for room in scene_info["rooms"]:
            sample = {
                "id": make_id(f"{scene_name}_{room}_{task_name}"),
                "source": "local_database",
                "scene_name": scene_name,
                "scene_type": scene_info["type"],
                "scene_label": scene_info["label"],
                "subtype": scene_info["subtypes"][0] if scene_info["subtypes"] else "",
                "room": room,
                "task": task_name,
                "action_sequence": [a.replace("{room}", room) for a in task_info["actions"]],
                "risk_level": task_info["risk"],
                "required_force_n": task_info["force_n"],
                "robot_capable": task_info["force_n"] <= 200,
                "duration_min": task_info["duration_min"],
                "created_at": datetime.now().isoformat(),
            }

            # 添加文件信息
            if scene_name in file_stats:
                sample["file_count"] = file_stats[scene_name]["count"]
                sample["file_size_mb"] = round(file_stats[scene_name]["size_mb"], 2)

            samples.append(sample)

    return samples

# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("完整建筑数据库扫描 -> 机器人训练数据生成器 V2")
    print("=" * 60)

    # 1. 扫描目录
    print("\n[1] 扫描建筑数据库...")
    file_stats = scan_directory(DATA_ROOT)

    total_files = sum(s["count"] for s in file_stats.values())
    total_mb = sum(s["size_mb"] for s in file_stats.values())
    print(f"  总计: {total_files} 文件, {total_mb:.1f} MB")
    print(f"  目录数: {len(file_stats)}")

    # 2. 生成训练样本
    print("\n[2] 生成训练样本...")
    all_samples = []

    for scene_name, scene_info in SCENE_TYPES.items():
        samples = generate_samples_from_scene(scene_name, scene_info, file_stats)
        all_samples.extend(samples)
        print(f"  {scene_name}: {len(samples)} 条样本")

    # 3. 去重
    seen = set()
    unique_samples = []
    for s in all_samples:
        if s["id"] not in seen:
            seen.add(s["id"])
            unique_samples.append(s)

    print(f"\n[DONE] 总计: {len(unique_samples)} 条唯一训练样本")

    # 4. 保存
    out_file = OUT_DIR / "robot_training_data_v2.json"
    output = {
        "meta": {
            "version": "2.0",
            "created_at": datetime.now().isoformat(),
            "total_samples": len(unique_samples),
            "source": str(DATA_ROOT),
            "file_stats": {k: {"count": v["count"], "size_mb": round(v["size_mb"], 2)} for k, v in file_stats.items()},
        },
        "scene_types": SCENE_TYPES,
        "action_templates": ACTION_TEMPLATES,
        "samples": unique_samples,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVED] {out_file}")
    print(f"  文件大小: {out_file.stat().st_size / 1024:.1f} KB")

    # 5. 统计
    cats = Counter(s["scene_type"] for s in unique_samples)
    print("\n[按场景类型统计]")
    for cat, cnt in cats.most_common():
        print(f"  {cat}: {cnt}")

    tasks = Counter(s["task"] for s in unique_samples)
    print("\n[按任务类型统计]")
    for task, cnt in tasks.most_common():
        print(f"  {task}: {cnt}")

    return unique_samples

if __name__ == "__main__":
    main()
