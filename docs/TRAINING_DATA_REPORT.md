# 建筑物理AI - 机器人训练数据资产报告

**生成时间**: 2026-04-20 22:40 GMT+8

---

## 数据资产总览

| 类别 | 数量 | 大小 | 状态 |
|------|------|------|------|
| VR全景链接 | 709条 | 193KB | ✅ 已索引 |
| 建筑对象(门/窗) | 151个 | - | ✅ 有坐标 |
| 效果图 | 1027张 | ~500MB | ✅ 已分类 |
| CAD图纸(DWG) | 76个 | ~420MB | ⚠️ 待解析 |
| 室内场景JPG | 106张 | 94MB | ✅ 家庭+办公 |
| PDF施工图 | 12个 | 206MB | ✅ 可读取 |

---

## 本地建筑数据库详情

### 家庭别墅 (311MB, 123文件)
- **山水庭院**: 1 PDF平面图 + 1 DOCX效果图链接
- **从化别墅**: 2 PDF施工图 (53MB)
- **黄总**: 1 PDF + 4 JPG效果图
- **李女士**: 1 PDF + 11 JPG效果图
- **覃总**: 1 PDF + 11 JPG效果图
- **王总**: 1 PDF + 10 JPG效果图
- **室内施工图**: 4 DWG (花月半岛/桔山湖/鹿城/万昌康城)
- **室内家居场景JPG**: 69张 (家庭场景55张 + 办公空间14张)

### 地产综合体佛山恒大云东海 (191MB)
- 7个PDF文件

### 产业园
- 待扫描

### 酒店场景 (55MB)
- 4个PDF文件

### 电气CAD施工图 (47MB)
- 11个文件

### 南沙星河东悦湾 (9MB)
- 1个DWG文件

---

## 机器人训练样本统计

### 已生成样本 (V2)
- **总计**: 182条唯一样本
- **场景类型**: 7种 (住宅别墅/家庭室内/商业综合体/产业园/酒店/住宅小区/电气工程)
- **任务类型**: 28种 (清洁/巡逻/搬运/送餐/设备检查等)

### 样本分布
| 场景类型 | 样本数 |
|----------|--------|
| residential_villa (家庭别墅) | 54 |
| residential_interior (家庭室内) | 25 |
| commercial_complex (商业综合体) | 25 |
| industrial_park (产业园) | 25 |
| hotel (酒店) | 25 |
| residential_complex (住宅小区) | 16 |
| electrical_engineering (电气工程) | 12 |

---

## 训练数据文件

| 文件 | 大小 | 用途 |
|------|------|------|
| `data/training/robot_training_data.json` | 145KB | V1 166样本 |
| `data/training/robot_training_data_v2.json` | 122KB | V2 182样本 |
| `knowledge/VR_KNOWLEDGE.json` | 194KB | 709个VR链接 |
| `data/processed/building_objects.json` | - | 151个门/窗坐标 |
| `knowledge/LIGHTING_DATABASE.json` | 13KB | 灯具知识库 |
| `knowledge/CONSTRUCTION_STANDARDS.md` | 8KB | 施工规范 |

---

## 下一步训练路线

### 1. 短期（本周）
- [ ] 解析PDF施工图 → 提取房间布局/尺寸数据
- [ ] 扩展训练样本到 500+ 条
- [ ] 集成VR全景数据到训练集

### 2. 中期（下周）
- [ ] DWG文件解析（需要LibreCAD或手动导出DXF）
- [ ] 效果图图像特征提取（ResNet/ViT嵌入）
- [ ] 构建 VLA (Vision-Language-Action) 模型

### 3. 长期
- [ ] 真实机器人仿真测试
- [ ] 数据飞轮闭环
- [ ] 天使轮Demo完善

---

**文件位置**:
- 训练脚本: `scripts/generate_robot_training_data_v2.py`
- 输出目录: `data/training/`
- 源数据: `C:\Users\Administrator\Desktop\建筑数据库\`
