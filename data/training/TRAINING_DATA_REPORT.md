# 训练数据生成报告

生成时间: 2026-04-21

---

## 📊 数据概览

| 数据集 | 数量 | 文件 |
|--------|------|------|
| **QA问答对** | 77条 | qa_pairs_v1.json |
| **合成场景** | 100个 | synthetic_scenes_v1.json |
| **合成任务** | 355个 | (包含在场景中) |

---

## 📝 QA问答对详情

### 分类统计

| 类别 | 数量 | 来源 |
|------|------|------|
| wall_type | 4 | CAD |
| wall_dimension | 4 | CAD |
| wall_material | 4 | CAD |
| drill_constraint | 4 | Rule |
| drill_parameter | 2 | Rule |
| pipe_location | 3 | CAD |
| object_location | 8 | VR |
| object_weight | 8 | VR |
| object_mobility | 8 | Rule |
| path_distance | 5 | CAD |
| path_time | 5 | Synthetic |
| room_area | 6 | CAD |
| room_floor | 6 | VR |
| room_window | 6 | VR |
| complex_task | 3 | Synthetic |

### 示例问答

```json
{
  "id": "qa_0013",
  "category": "drill_constraint",
  "question": "能在北墙钻孔吗？",
  "answer": "不能。北墙是承重墙，承重墙钻孔可能影响建筑结构安全。如确需钻孔，必须由专业结构工程师评估审批。",
  "source": "rule"
}
```

---

## 🏠 合成场景详情

### 任务类型分布

| 任务类型 | 数量 | 占比 |
|----------|------|------|
| drill (钻孔) | 155 | 43.7% |
| move (搬运) | 100 | 28.2% |
| clean (清洁) | 100 | 28.2% |

### 结果分布

| 结果 | 数量 | 占比 |
|------|------|------|
| success | 259 | 73.0% |
| failure | 65 | 18.3% |
| warning | 31 | 8.7% |

### 场景类型分布

- living_room (客厅)
- bedroom (卧室)
- study (书房)
- kitchen (厨房)
- bathroom (卫生间)
- dining_room (餐厅)
- office (办公室)
- hotel_room (酒店房间)

### 示例场景

```json
{
  "scene_id": "synthetic_0001",
  "scene_type": "bedroom",
  "room_area_m2": 15.3,
  "objects": [
    {"name": "床", "weight_kg": 82.5, "movable": false},
    {"name": "衣柜", "weight_kg": 95.2, "movable": false},
    {"name": "床头柜", "weight_kg": 12.3, "movable": true}
  ],
  "walls": {
    "north": {"type": "load_bearing", "thickness_cm": 24, "has_pipes": true},
    "south": {"type": "partition", "thickness_cm": 10, "has_pipes": false}
  },
  "tasks": [
    {
      "task_type": "drill",
      "instruction": "在北墙钻一个8mm的孔",
      "expected_result": "failure",
      "constraints": ["北墙是承重墙", "禁止钻孔"]
    }
  ]
}
```

---

## 🎯 数据用途

### 1. 模型训练

- **QA问答对** → 用于训练语义理解模型
- **合成场景** → 用于训练场景推理模型

### 2. 测试验证

- 正样本（success）→ 验证任务执行能力
- 负样本（failure）→ 验证约束检查能力
- 警告样本（warning）→ 验证风险提示能力

### 3. 数据增强

- 可通过调整生成参数扩展数据量
- 可添加更多场景类型和任务类型
- 可引入真实CAD/VR数据作为模板

---

## 📁 文件结构

```
data/training/
├── qa_pairs_v1.json           # QA问答对 (77条)
├── synthetic_scenes_v1.json   # 合成场景 (100个, 355任务)
└── TRAINING_DATA_REPORT.md    # 本报告
```

---

## 🔄 后续扩展

1. **接入真实数据**: 将CAD解析结果作为模板
2. **增加任务类型**: 添加检查、维修等任务
3. **多轮对话**: 生成任务执行过程中的对话
4. **失败案例**: 生成更多边界情况和失败案例
5. **多语言**: 支持中英文双语训练数据

---

_生成器: qa_pair_generator.py + synthetic_data_generator.py_
