# 时空光影模拟 + 虚实结合 技术架构

> **目标**：将"死气沉沉的3D模型"进化为"随时间/季节/朝向变化的4D物理世界"，并与真实场景精确融合

---

## 一、时空光影模拟（Temporal Lighting Simulation）

### 1.1 核心概念

从"静态3D渲染"进化到"时空4D动态环境"——太阳位置、光影角度、阴影长度都随真实时间变化。

```
静态3D模型                    时空4D世界
─────────────────             ────────────────────────────────
❌ 固定光源                    ✅ 太阳真实运动（根据GPS+时间）
❌ 永恒正午                    ✅ 清晨/正午/夕阳/夜晚
❌ 硬阴影                      ✅ 软阴影（云层散射）+ 硬阴影
❌ 固定相机                    ✅ 机器人视角（能动）
❌ 忽略光照影响                 ✅ 机器人需适应眩光/阴影/温感
```

### 1.2 技术实现路径

#### 工具链
| 层级 | 工具 | 用途 |
|------|------|------|
| 地理计算 | **SunCalc.js** | 根据经纬度+时间计算太阳高度角/方位角 |
| 3D渲染 | **Three.js** + `@react-three/fiber` | 实时阴影渲染、天空盒、HDR |
| 物理引擎 | **物理引擎层（L3）** | 光照角度 → 阴影投射 → 热成像预判 |
| 机器人感知 | **Harness L4** | 眩光适应、阴影感知、温感预判 |

#### 太阳计算核心（SunCalc）
```typescript
// SunCalc 输入
interface SunPosition {
  lat: number          // 纬度（来自CAD图纸或手动设定）
  lng: number          // 经度
  date: Date           // 当前时间
  altitude?: number     // 海拔（可选）
}

// SunCalc 输出
interface SunData {
  altitude: number      // 太阳高度角（°，地平线上方）
  azimuth: number       // 太阳方位角（°，北=0，顺时针）
  sunrise: Date         // 日出时间
  sunset: Date          // 日落时间
  solarNoon: Date        // 正午
  dawn: Date             // 黎明（民用曙暮光）
  dusk: Date             // 黄昏
  night: Date            // 夜晚开始
  dayLength: number      // 白昼时长（秒）
}
```

#### 动态阴影参数
```typescript
interface ShadowConfig {
  enabled: boolean
  type: 'hard' | 'soft'        // 硬阴影（正午）/ 软阴影（阴天）
  bias: number                  // 阴影偏移（防止瑕疵）
  mapSize: [number, number]     // 阴影贴图分辨率
  cameraNear: number            // 阴影相机近裁面
  cameraFar: number             // 阴影相机远裁面
  cameraMargin: number          // 相机范围扩展
}

// 根据太阳高度角调整阴影长度
function getShadowScale(altitude: number): number {
  // 太阳高度角 = 90°（正午）：阴影最短
  // 太阳高度角 = 0°（日出/日落）：阴影最长
  return 1 / Math.max(Math.sin(altitude * Math.PI / 180), 0.1)
}
```

### 1.3 机器人赋能（光影常识）

#### 能力1：眩光适应（Glare Adaptation）
```typescript
// 检测逆光场景
interface GlareDetector {
  checkGlare(
    cameraDir: Vector3,    // 机器人朝向
    sunAzimuth: number,    // 太阳方位角
    sunAltitude: number,   // 太阳高度角
    surfaceMaterial: string // 表面材质（玻璃幕墙反射强）
  ): GlareLevel  // none | mild | severe

  // 策略
  const GLARE_STRATEGIES = {
    mild:  { action: 'reduce_speed', factor: 0.7 },
    severe: { action: 'switch_to_ir', wait_seconds: 3 }
  }
}
```

#### 能力2：阴影感知（Shadow Understanding）
```typescript
// 理解影子不是悬崖
interface ShadowReasoning {
  // 输入
  shadowRegion: BoundingBox  // 影像区域
  currentTime: Date
  sunAzimuth: number
  sunAltitude: number
  surfaceType: string       // "floor" | "wall" | "ceiling"

  // 推理
  reasoning: `
    时间: 17:30, 朝向: 西
    太阳方位: 270°, 高度: 15°
    影像区域在物体东侧，长度2.3m
    → 这是下午夕阳投射的正常阴影
    → 区域可通行，建议减速20%
  `
}
```

#### 能力3：温感预判（Temperature Prediction）
```typescript
// 西晒区域温度预判
interface TempPredictor {
  // 不同朝向+时间 → 表面温度估算
  predictSurfaceTemp(
    orientation: 'north' | 'south' | 'east' | 'west',
    time: Date,
    material: 'glass' | 'concrete' | 'metal' | 'wood'
  ): { temp_celsius: number, risk: 'safe' | 'warm' | 'hot' | 'burn' }

  // 示例规则
  const WEST_SUMMER_5PM = {
    glass: { temp_celsius: 65, risk: 'burn' },
    concrete: { temp_celsius: 52, risk: 'hot' },
    metal: { temp_celsius: 70, risk: 'burn' }
  }
}
```

### 1.4 落地步骤

| 里程碑 | 内容 | 优先级 |
|--------|------|--------|
| **M1** | SunCalc.js 集成到前端，根据CAD已知坐标设定GPS，实现时间轴拖动 | 🔴 高 |
| **M2** | 实现冬至/夏至光线模拟，展示极低光照或强光灸晒 | 🔴 高 |
| **M3** | HDR天空盒 + 室内间接光照（光追探针） | 🟡 中 |
| **M4** | Harness层接入：眩光检测、阴影推理、温感预判 | 🔴 高 |

---

## 二、虚实结合（Virtual-Real Fusion）

### 2.1 核心概念

用3DGS（高斯泼溅）技术将真实场景"拍进"CAD骨架，实现毫米级精度的数字孪生。

```
传统CAD模型              数字孪生（CAD骨 + 实景皮）
─────────────────        ─────────────────────────────────
❌ 设计师假设的尺寸         ✅ 真实施工误差（如墙歪了3cm）
❌ 理想化的家具位置         ✅ 实际家具位置（可能有偏差）
❌ 静态快照                ✅ 可周期性更新（周更/月更）
❌ 不知道墙后有什么          ✅ 实景扫描可看到隐藏细节
```

### 2.2 技术实现路径

#### 工具链
| 层级 | 工具 | 用途 |
|------|------|------|
| 场景采集 | 全景相机（小红屋/理光THETA）| 原始实景数据 |
| 3DGS训练 | GaussianSplating3D | 从2D图像生成3D高斯点云 |
| 空间配准 | ICP + 特征点对齐 | 3DGS ↔ CAD 精确对齐 |
| 融合渲染 | Three.js + 透明混合 | "实景为皮，白模为骨" |

#### 配准算法
```typescript
interface ICPConfig {
  // 粗对齐（Coarse Alignment）
  coarse: {
    method: 'gps' | 'rtk' | 'qr_marker'  // GPS/RTK/QRMaker
    initialError: number                  // 初始误差 ~1m
  }

  // 精对齐（Fine Alignment）
  fine: {
    method: 'icp' | 'ransac' | 'elastic'  // ICP/ RANSAC /弹性注册
    targetError: number                    // 目标误差 <2cm
    maxIterations: number                  // 最大迭代次数
  }
}

// 对齐结果
interface AlignmentResult {
  rotation: [number, number, number, number]  // 四元数旋转
  translation: [number, number, number]        // 平移向量
  scale: number                                // 尺度因子
  residual_error: number                       // 残差（目标 <2cm）
  status: 'success' | 'warning' | 'failed'
}
```

#### 融合渲染策略
```typescript
// 双层渲染
interface FusionRenderer {
  // 层1：CAD白模（几何骨架，透明度可调）
  cadLayer: {
    visible: boolean
    opacity: number          // 0=全透明，1=全不透明
    color: string             // 默认白色
    wireframe: boolean        // 线框模式
  }

  // 层2：3DGS实景点云（纹理贴图）
  gsLayer: {
    visible: boolean
    opacity: number
    pointSize: number         // 点大小
  }

  // 融合模式
  blendMode: 'overlay' | 'difference' | 'multiply'
}

// 典型使用
const BIM_REVIEW = {
  cadLayer: { visible: true, opacity: 0.3 },
  gsLayer: { visible: true, opacity: 0.9 }
}

const CONSTRUCTION_CHECK = {
  cadLayer: { visible: true, opacity: 0.8 },
  gsLayer: { visible: true, opacity: 0.4 }
}
```

### 2.3 机器人赋能（虚实对齐）

#### 能力1：施工误差感知
```typescript
// CAD vs 实景偏差检测
interface DeviationDetector {
  // 对比CAD墙线与3DGS扫描点云
  detectDeviation(
    cadWalls: Line[],         // CAD墙线
    scanPoints: PointCloud,   // 3DGS扫描点
    tolerance: number = 0.02  // 容差2cm
  ): DeviationReport

  // 输出示例
  // {
  //   wall: "北墙",
  //   cadPosition: [0, 0, 0],
  //   actualPosition: [0.03, 0, 0],  // 歪了3cm
  //   deviation: 0.03,
  //   severity: "acceptable"         // 可接受偏差
  // }
}
```

#### 能力2：动态现状更新
```typescript
// 周期性扫描 → 变化检测
interface ChangeDetector {
  // 输入：旧3DGS模型 + 新拍摄
  detectChanges(
    oldModel: GaussianModel,
    newScan: GaussianModel,
    threshold: number = 0.5  // 变化阈值(m)
  ): ChangeReport

  // 检测类型
  type: 'obstacle_added' | 'obstacle_removed' | 'object_moved'
  region: BoundingBox
  description: string  // "检测到材料堆积，体积0.8m³"
}
```

### 2.4 落地步骤

| 里程碑 | 内容 | 优先级 |
|--------|------|--------|
| **M4** | 手动验证：用现有小红屋数据，手动标注4个角点坐标，验证3DGS+CAD对齐效果 | 🔴 高 |
| **M5** | 半自动对齐：开发自动化脚本，新上传视频 → 3DGS训练 → 特征点粗对齐 → 推送后台审核 | 🟡 中 |
| **M6** | 厘米级精度验证：目标配准误差<2cm，机器人路径规划验证 | 🔴 高 |
| **M7-M9** | 全自动管线：定期扫描 → 变化检测 → 自动更新世界模型拓扑 | 🟡 中 |

---

## 三、融合架构

```
物理世界模型（L1-L5）
┌─────────────────────────────────────────────────────────────┐
│ L5 应用层                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ 时空光影模拟 │  │ 虚实融合     │  │ 机器人任务规划        │ │
│  │ SunCalc+时间 │  │ 3DGS+CAD ICP│  │ 路径+动作序列        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                           ↓ ↓                                 │
│ L3 世界模型核心                                               │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ SpatialEncoder(98.1%) │ PhysicsMLP │ RelationTrans(100%)││
│  └──────────────────────────────────────────────────────────┘│
│                           ↓                                   │
│ L2 编码层                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ VR效果图  │  │ CAD施工图 │  │ 3DGS点云 │  │ 全景实景图   │ │
│  │ (2D图像)  │  │ (几何真值)│  │ (高斯表示)│  │ (全景相机)   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、实现优先级

| 优先级 | 任务 | 工作量 | 价值 |
|--------|------|--------|------|
| 🔴 P0 | SunCalc集成 + 时间轴UI | 2-3天 | 让现有Demo"活起来" |
| 🔴 P0 | HDR天空盒 | 1天 | 视觉效果立竿见影 |
| 🟡 P1 | 3DGS+CAD手动对齐验证 | 3-5天 | 验证技术路线 |
| 🟡 P1 | 眩光/阴影感知规则 | 2天 | Harness层护城河 |
| 🟢 P2 | ICP自动配准 | 5-7天 | 厘米级精度 |
| 🟢 P2 | 动态现状更新 | 5-7天 | 世界模型自进化 |
