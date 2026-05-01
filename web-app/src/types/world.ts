// 建筑物理AI世界模型 - 核心类型定义
// 分类体系：室内(家庭别墅/商场/办公/酒店) / 园林(别墅园林/公园) / 建筑(写字楼/小区/商场综合体)

export type SceneCategory = 'interior' | 'landscape' | 'architecture'
export type InteriorScene = 'residence' | 'mall' | 'office' | 'hotel'
export type LandscapeScene = 'villa_garden' | 'park'
export type ArchitectureScene = 'office_building' | 'residential' | 'commercial_complex'

export interface PhysicsProperties {
  mass?: number           // kg
  material?: string       // 材质：混凝土/木材/玻璃/金属
  friction?: number        // 摩擦系数 0-1
  stiffness?: number      // 刚度 MPa
  isStructural?: boolean   // 是否承重结构
  conductivity?: number    // 导电性
  thermalMass?: number     // 热质量
}

export interface RobotCapability {
  graspable: boolean       // 可抓取
  openable: boolean        // 可开启（门/抽屉/柜门）
  pathObstacle: boolean    // 路径障碍
  pushable: boolean        // 可推动
  climbable: boolean       // 可攀爬（楼梯/台阶）
}

export interface VRData {
  vr_id: number
  platform: '3d66' | 'Justeasy' | '720yun'
  designer: string
  title?: string
  room_name: string
  room_category: string    // 客厅/餐厅/主卧/卫生间等
  physics_tags: string[]   // 物理标签：地面高差/潮湿/狭窄通道等
}

export interface CADData {
  project: string
  floor?: string
  discipline?: string      // 建筑/电气/给排水/暖通/结构
  layer?: string
  source_file?: string
  scale?: string
}

export interface BuildingObject {
  id: string
  name: string
  type: 'wall' | 'floor' | 'ceiling' | 'door' | 'window' | 'furniture' | 'appliance' | 'stairs' | 'corridor' | 'landscape'
  
  // 几何属性（米）
  position: [number, number, number]
  rotation: [number, number, number]
  dimensions: { width: number; height: number; depth: number }
  
  // 物理世界模型
  physics: PhysicsProperties
  robot: RobotCapability
  
  // 数据来源
  vrData?: VRData
  cadData?: CADData
  
  // 场景分类
  sceneCategory?: SceneCategory
  sceneType?: string       // 'residence' | 'mall' | 'office' | 'hotel' | ...
}

export interface RobotTask {
  id: string
  name: string
  description: string
  targetRoom: string
  steps: string[]
  physicsKnowledge: string[]
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface WorldModelStats {
  totalVR: number
  totalRooms: number
  byCategory: Record<string, number>
  byPlatform: Record<string, number>
  byDesigner: Array<{ name: string; count: number }>
  physicsTags: string[]
}
