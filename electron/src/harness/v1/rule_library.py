"""
L3 核心世界模型层 - 建筑空间规则库
预加载国家及地方建筑设计规范，实时检查动作的空间合规性
"""

from typing import Literal, Optional


# ─────────────────────────────────────────────
# 国家建筑标准规范库（关键条款）
# ─────────────────────────────────────────────
ARCHITECTURE_RULES = {
    # 无障碍设计规范
    "无障碍通道宽度": {
        "min_width_m": 1.2,
        "category": "无障碍",
        "standard": "GB 50763-2012",
        "description": "轮椅通道宽度不小于1.2m",
    },
    "无障碍坡道": {
        "max_slope": 0.083,
        "category": "无障碍",
        "standard": "GB 50763-2012",
        "description": "坡道最大坡度1:12",
    },
    "门净宽_单扇": {
        "min_width_m": 0.9,
        "category": "无障碍",
        "standard": "GB 50763-2012",
        "description": "门净宽不小于0.9m（单扇）",
    },
    "门净宽_双扇": {
        "min_width_m": 1.2,
        "category": "无障碍",
        "standard": "GB 50763-2012",
        "description": "门净宽不小于1.2m（双扇）",
    },
    # 消防安全
    "消防通道宽度": {
        "min_width_m": 4.0,
        "category": "消防",
        "standard": "GB 50016-2018",
        "description": "消防车道宽度不小于4m",
    },
    "疏散走道宽度": {
        "min_width_m": 1.4,
        "category": "消防",
        "standard": "GB 50016-2018",
        "description": "疏散走道净宽度不小于1.4m",
    },
    "消火栓间距": {
        "max_spacing_m": 30.0,
        "category": "消防",
        "standard": "GB 50016-2018",
        "description": "室内消火栓间距不大于30m",
    },
    # 楼梯设计
    "楼梯踏步高度": {
        "min_h_m": 0.135,
        "max_h_m": 0.18,
        "category": "楼梯",
        "standard": "GB 50096-2011",
        "description": "住宅楼梯踏步高度135-180mm",
    },
    "楼梯踏步宽度": {
        "min_w_m": 0.26,
        "max_w_m": 0.32,
        "category": "楼梯",
        "standard": "GB 50096-2011",
        "description": "楼梯踏步宽度260-320mm",
    },
    "楼梯扶手高度": {
        "min_h_m": 0.9,
        "category": "楼梯",
        "standard": "GB 50096-2011",
        "description": "楼梯扶手高度不小于0.9m",
    },
    # 净空高度
    "住宅净空": {
        "min_height_m": 2.8,
        "category": "净空",
        "standard": "GB 50096-2011",
        "description": "住宅层高不低于2.8m",
    },
    "走廊净空": {
        "min_height_m": 2.2,
        "category": "净空",
        "standard": "GB 50016-2018",
        "description": "走廊净高不低于2.2m",
    },
    # 卫生间
    "卫生间门宽": {
        "min_width_m": 0.8,
        "category": "卫生间",
        "standard": "GB 50096-2011",
        "description": "卫生间门净宽不小于0.8m",
    },
    # 厨房
    "操作台高度": {
        "standard_h_m": 0.8,
        "tolerance_m": 0.05,
        "category": "厨房",
        "standard": "GB 50096-2011",
        "description": "厨房操作台高度约0.8m",
    },
    # 阳台
    "阳台栏杆高度": {
        "min_h_m": 1.1,
        "category": "阳台",
        "standard": "GB 50096-2011",
        "description": "阳台栏杆高度不低于1.1m",
    },
    "阳台荷载": {
        "max_load_kg_m2": 250,
        "category": "阳台",
        "standard": "GB 50009-2012",
        "description": "阳台活荷载标准值250kg/m²",
    },
    # 栏杆间距
    "栏杆竖向间距": {
        "max_spacing_m": 0.11,
        "category": "安全",
        "standard": "GB 50096-2011",
        "description": "栏杆竖向杆件间距不大于110mm（防儿童攀爬）",
    },
    # 电梯
    "电梯井道净空": {
        "min_width_m": 1.4,
        "min_depth_m": 1.4,
        "category": "电梯",
        "standard": "GB 7588-2003",
        "description": "电梯井道最小净空尺寸",
    },
}

# ─────────────────────────────────────────────
# 家具安全距离规范
# ─────────────────────────────────────────────
FURNITURE_CLEARANCES = {
    "轮椅通行": 1.2,
    "病床通道": 1.5,
    "厨房操作": 1.2,
    "餐桌通行": 0.9,
    "沙发茶几": 0.45,
    "床侧通行": 0.6,
    "书架取书": 0.9,
    "衣柜开门": 0.6,
    "冰箱门开": 0.8,
    "马桶旁边": 0.45,
    "洗手台前": 0.6,
    "门后通行": 0.6,
    "走廊会车": 1.2,
    "楼梯扶手": 0.1,
}


class RuleLibrary:
    """
    建筑规则库：预加载国家规范，提供合规性检查接口
    """

    def __init__(self):
        self.rules = ARCHITECTURE_RULES
        self.clearances = FURNITURE_CLEARANCES
        print(f"[RuleLibrary] Loaded {len(self.rules)} architecture rules")
        print(f"[RuleLibrary] Loaded {len(self.clearances)} furniture clearances")

    def check_rule(
        self,
        rule_name: str,
        measured_value: float,
    ) -> dict:
        """
        检查单个规则
        rule_name: 规则名称
        measured_value: 实测值（米）
        """
        rule = self.rules.get(rule_name)
        if rule is None:
            return {"pass": False, "error": f"Unknown rule: {rule_name}"}

        min_val = rule.get("min_width_m") or rule.get("min_h_m") or rule.get("min_height_m")
        max_val = (rule.get("max_slope") or rule.get("max_spacing_m")
                   or rule.get("max_h_m") or rule.get("max_w_m"))

        if min_val is not None:
            ok = measured_value >= min_val
            diff = measured_value - min_val
        elif max_val is not None:
            ok = measured_value <= max_val
            diff = max_val - measured_value
        else:
            ok = True
            diff = 0.0

        return {
            "pass": ok,
            "rule_name": rule_name,
            "measured_value_m": round(measured_value, 3),
            "threshold_m": round(min_val or max_val, 3),
            "diff_m": round(diff, 3),
            "standard": rule.get("standard", ""),
            "category": rule.get("category", "通用"),
            "description": rule["description"],
            "status": "PASS 符合" if ok else "FAIL 不符合",
        }

    def check_clearance(
        self,
        clearance_type: str,
        actual_distance: float,
    ) -> dict:
        """检查家具安全距离"""
        required = self.clearances.get(clearance_type, 0.6)
        ok = actual_distance >= required
        return {
            "pass": ok,
            "clearance_type": clearance_type,
            "actual_distance_m": round(actual_distance, 3),
            "required_m": required,
            "status": "PASS 符合" if ok else "FAIL 不符合",
        }

    def check_multiple_clearances(
        self,
        measurements: dict[str, float],
    ) -> list[dict]:
        """批量检查多个距离"""
        results = []
        for clearance_type, distance in measurements.items():
            results.append(self.check_clearance(clearance_type, distance))
        return results

    def list_rules(self, category: Optional[str] = None) -> list[dict]:
        """列出规则库"""
        rules = []
        for name, rule in self.rules.items():
            if category is None or rule.get("category") == category:
                rules.append({"name": name, **rule})
        return rules

    def suggest_clearance(self, scene_description: str) -> list[dict]:
        """根据场景推荐安全距离"""
        return [
            {"type": k, "min_distance_m": v, "scene": scene_description}
            for k, v in self.clearances.items()
        ]

    def validate_scene_plan(
        self,
        plan: dict,
    ) -> dict:
        """
        验证动作计划的整体合规性
        """
        all_pass = True
        checks = []

        for action in plan.get("action_sequence", []):
            # 自动规则检查
            for rule_name, rule in self.rules.items():
                if rule_name == "无障碍通道宽度" and action.get("path_width"):
                    r = self.check_rule(rule_name, action["path_width"])
                    if not r["pass"]:
                        all_pass = False
                    checks.append(r)

        return {
            "all_pass": all_pass,
            "checks": checks,
            "failed_count": sum(1 for c in checks if not c["pass"]),
        }
