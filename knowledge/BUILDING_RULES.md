# 建筑规范规则库

> 版本: v1.0
> 更新时间: 2026-04-21

---

## 📚 规范来源

| 规范名称 | 编号 | 适用范围 |
|----------|------|----------|
| 建筑设计防火规范 | GB 50016-2014 | 所有建筑 |
| 建筑抗震设计规范 | GB 50011-2010 | 抗震设防区 |
| 住宅设计规范 | GB 50096-2011 | 住宅建筑 |
| 建筑与市政工程无障碍通用规范 | GB 55019-2021 | 所有建筑 |
| 混凝土结构设计规范 | GB 50010-2010 | 混凝土结构 |
| 钢结构设计标准 | GB 50017-2017 | 钢结构 |
| 砌体结构设计规范 | GB 50003-2011 | 砌体结构 |

---

## 🔒 钻孔约束规则

### 1. 承重墙钻孔

```yaml
规则ID: DRILL_001
规则名称: 承重墙禁止钻孔
适用范围: 所有承重墙
约束条件:
  - wall_type == "load_bearing"
判定结果: 禁止
原因: 承重墙钻孔影响建筑结构安全
例外情况:
  - 经结构工程师评估审批
  - 钻孔直径小于20mm且不影响主筋
提示信息: "承重墙禁止钻孔，如确需操作请联系专业结构工程师"
```

### 2. 非承重墙钻孔

```yaml
规则ID: DRILL_002
规则名称: 非承重墙钻孔限制
适用范围: 非承重墙、隔墙
约束条件:
  - wall_type == "non_load_bearing" or wall_type == "partition"
  - drill_diameter <= max_diameter
  - drill_depth <= max_depth
参数限制:
  非承重墙:
    max_diameter: 100mm
    max_depth: 80mm
  隔墙:
    max_diameter: 150mm
    max_depth: 80mm
判定结果: 允许（需注意）
注意事项:
  - 建议使用探测仪确认墙内无隐蔽管线
  - 钻孔位置应避开墙体接缝
```

### 3. 管线安全距离

```yaml
规则ID: DRILL_003
规则名称: 钻孔管线安全距离
适用范围: 所有墙体
约束条件:
  - distance_to_pipe >= safety_distance
安全距离要求:
  电气管线: 150mm
  水管: 100mm
  燃气管: 300mm
判定逻辑:
  IF 有管线 AND distance < safety_distance:
    RETURN 警告
  ELSE:
    RETURN 允许
```

### 4. 钻孔位置限制

```yaml
规则ID: DRILL_004
规则名称: 钻孔位置限制
适用范围: 所有墙体
禁止区域:
  - 梁柱节点区域（上下500mm）
  - 墙体转角区域（转角500mm范围内）
  - 门窗洞口边缘（200mm范围内）
  - 已有孔洞边缘（100mm范围内）
判定逻辑:
  IF 钻孔位置 IN 禁止区域:
    RETURN 禁止
  ELSE:
    RETURN 允许
```

---

## 🏠 搬运约束规则

### 1. 物体重量限制

```yaml
规则ID: MOVE_001
规则名称: 搬运重量限制
适用范围: 所有搬运任务
约束条件:
  单人搬运:
    max_weight: 25kg
    建议: 分步操作
  双人搬运:
    max_weight: 50kg
    建议: 协调配合
  机械搬运:
    max_weight: 无限制
    要求: 使用推车/叉车等工具
判定逻辑:
  IF weight <= 25:
    RETURN 单人可搬运
  ELIF weight <= 50:
    RETURN 需双人搬运
  ELSE:
    RETURN 需机械搬运
```

### 2. 路径通道限制

```yaml
规则ID: MOVE_002
规则名称: 搬运路径通道限制
适用范围: 所有搬运任务
通道要求:
  门洞净宽: >= 800mm
  走廊净宽: >= 1000mm
  楼梯净宽: >= 1100mm
  电梯轿厢: >= object_width + 100mm
判定逻辑:
  FOR EACH 路径段:
    IF 通道宽度 < 物体宽度 + 余量:
      RETURN 路径不通
  RETURN 路径可行
```

### 3. 地面承重限制

```yaml
规则ID: MOVE_003
规则名称: 地面承重限制
适用范围: 重物搬运
楼面荷载标准:
  住宅: 2.0 kN/m²
  办公: 2.0 kN/m²
  商场: 3.5 kN/m²
  仓库: 5.0 kN/m²
判定逻辑:
  actual_load = object_weight / contact_area
  IF actual_load > standard:
    RETURN 超载警告
  ELSE:
    RETURN 安全
```

---

## 🧹 清洁约束规则

### 1. 清洁区域限制

```yaml
规则ID: CLEAN_001
规则名称: 清洁区域限制
适用范围: 所有清洁任务
禁止清洁区域:
  - 电气设备内部
  - 高压线附近（2m内）
  - 正在运行的机械设备
  - 化学品存储区
判定逻辑:
  IF 清洁区域 IN 禁止区域:
    RETURN 禁止
  ELSE:
    RETURN 允许
```

### 2. 清洁工具限制

```yaml
规则ID: CLEAN_002
规则名称: 清洁工具限制
适用范围: 地板清洁
工具匹配:
  木地板:
    禁止: 大量水洗
    推荐: 干拖/微湿拖
  瓷砖:
    允许: 水洗
    推荐: 中性清洁剂
  石材:
    禁止: 酸性清洁剂
    推荐: 专用石材清洁剂
```

---

## 🏗️ 建筑构造规则

### 1. 门窗尺寸规则

```yaml
规则ID: OPENING_001
规则名称: 门窗洞口尺寸
适用范围: 门窗设计
门洞最小尺寸:
  入户门: 900mm x 2100mm
  卧室门: 800mm x 2100mm
  卫生间门: 700mm x 2100mm
窗洞最小尺寸:
  卧室窗: 600mm x 900mm
  客厅窗: 宽度 >= 房间进深/6
判定逻辑:
  IF 洞口尺寸 < 最小尺寸:
    RETURN 不符合规范
```

### 2. 房间面积规则

```yaml
规则ID: ROOM_001
规则名称: 房间最小面积
适用范围: 住宅设计
最小面积要求:
  卧室: 9m²（双人）, 5m²（单人）
  客厅: 12m²
  厨房: 4m²
  卫生间: 3m²
判定逻辑:
  IF 房间面积 < 最小面积:
    RETURN 不符合规范
```

### 3. 采光通风规则

```yaml
规则ID: ROOM_002
规则名称: 采光通风要求
适用范围: 住宅设计
窗地比要求:
  卧室、起居室: >= 1/7
  厨房: >= 1/7
  卫生间: >= 1/10
判定逻辑:
  window_ratio = window_area / floor_area
  IF window_ratio < 要求值:
    RETURN 采光不足
```

---

## 🔥 防火规则

### 1. 防火分区

```yaml
规则ID: FIRE_001
规则名称: 防火分区面积
适用范围: 建筑防火设计
最大允许面积:
  一级耐火等级:
    单层: 不限
    多层: 2500m²
    高层: 1500m²
  二级耐火等级:
    单层: 3000m²
    多层: 2000m²
判定逻辑:
  IF 分区面积 > 最大允许面积:
    RETURN 需增设防火墙
```

### 2. 疏散距离

```yaml
规则ID: FIRE_002
规则名称: 疏散距离限制
适用范围: 建筑防火设计
最大疏散距离:
  托幼建筑: 25m
  医疗建筑: 35m
  其他建筑: 40m
  设有喷淋: 可增加25%
判定逻辑:
  IF 实际距离 > 最大距离:
    RETURN 疏散距离超标
```

---

## 📐 结构规则

### 1. 混凝土保护层

```yaml
规则ID: STRUCT_001
规则名称: 混凝土保护层厚度
适用范围: 混凝土结构
保护层最小厚度:
  室内正常环境: 20mm
  室外环境: 25mm
  地下室: 30mm
  预制构件: 15mm
钻孔安全余量:
  钻孔深度 <= 保护层厚度 - 5mm
```

### 2. 钢筋间距

```yaml
规则ID: STRUCT_002
规则名称: 钢筋最小间距
适用范围: 混凝土结构
最小间距要求:
  梁纵向钢筋: 25mm 或 钢筋直径
  柱纵向钢筋: 50mm
  板受力钢筋: 70mm
判定逻辑:
  IF 钻孔可能切断钢筋:
    RETURN 禁止钻孔
```

---

## 🔧 规则查询接口

```python
# rule_query.py
class RuleQuery:
    """规则查询接口"""
    
    RULES = {
        "DRILL_001": {...},
        "DRILL_002": {...},
        # ...
    }
    
    @classmethod
    def check_drill(cls, wall_type: str, diameter: float, 
                    depth: float, has_pipes: bool) -> dict:
        """检查钻孔约束"""
        result = {
            "allowed": True,
            "rules_checked": [],
            "warnings": []
        }
        
        # 规则1: 承重墙
        if wall_type == "load_bearing":
            result["allowed"] = False
            result["rules_checked"].append("DRILL_001")
            result["warnings"].append("承重墙禁止钻孔")
            return result
        
        # 规则2: 尺寸限制
        max_diameter = 100 if wall_type == "non_load_bearing" else 150
        if diameter > max_diameter:
            result["allowed"] = False
            result["rules_checked"].append("DRILL_002")
            result["warnings"].append(f"钻孔直径{diameter}mm超过限制{max_diameter}mm")
        
        # 规则3: 管线安全
        if has_pipes:
            result["rules_checked"].append("DRILL_003")
            result["warnings"].append("墙内有管线，建议使用探测仪定位")
        
        return result
```

---

## 📋 规则完整性检查

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 钻孔规则 | ✅ | 4条规则 |
| 搬运规则 | ✅ | 3条规则 |
| 清洁规则 | ✅ | 2条规则 |
| 门窗规则 | ✅ | 1条规则 |
| 房间规则 | ✅ | 2条规则 |
| 防火规则 | ✅ | 2条规则 |
| 结构规则 | ✅ | 2条规则 |

---

_数据来源: 国家建筑规范 + 行业标准_
