// Auto-generated from VR scan data - 2026-04-10
// Categorized: 室内(家庭别墅/商场/办公/酒店) / 园林(别墅园林/公园) / 建筑(写字楼/小区/商场综合体)

// 房间类型 → 颜色映射
export const ROOM_COLORS: Record<string, string> = {
  // 室内
  '客厅': '#E8D5B7',
  '餐厅': '#D4C4A8',
  '厨房': '#C8B89A',
  '主卧': '#B8C8D8',
  '次卧': '#C0C0C0',
  '儿童房': '#FFE4B5',
  '卫生间': '#B0D0D0',
  '玄关': '#D0C0B0',
  '阳台': '#A0B090',
  '书房': '#D8D0C0',
  '储藏': '#C0B8A0',
  '设备': '#A0A0A0',
  '楼梯': '#B8A888',
  '衣帽间': '#D8C8B8',
  '影音室': '#A0A0B8',
  '棋牌室': '#C8B8A0',
  '健身房': '#B8C0B0',
  '茶室': '#C8D0B8',
  '吧台': '#C0B090',
  '主卫': '#A8D8D8',
  '次卫': '#B0E0E0',
  '走廊': '#D0C8B8',
  '电梯厅': '#C8C0B0',
  // 园林
  '花园': '#90B870',
  '庭院': '#A0C080',
  '泳池': '#60A0D0',
  '草坪': '#80B060',
  '硬化铺装': '#C0B090',
  // 建筑
  '地下车库': '#607D8B',
  '大堂': '#D0C8B8',
  '办公区': '#E0E8F0',
  '会议室': '#D8E0E8',
  '商铺': '#F0E8D8',
  '其他': '#CCCCCC',
  'default': '#CCCCCC',
}

// 场景分类配置
export interface SceneConfig {
  id: string
  label: string
  description: string
  icon: string
  color: string
  tags: string[]
}

export const SCENE_CONFIGS: Record<string, SceneConfig> = {
  // 室内场景
  residence: {
    id: 'residence',
    label: '家庭别墅',
    description: '独栋/联排别墅，客厅/餐厅/卧室/书房/影音室',
    icon: '🏠',
    color: '#E8D5B7',
    tags: ['客厅', '餐厅', '厨房', '主卧', '次卧', '书房', '影音室', '茶室'],
  },
  mall: {
    id: 'mall',
    label: '商场',
    description: '购物中心，商铺/餐饮/影院/儿童区',
    icon: '🏬',
    color: '#F0E0D0',
    tags: ['商铺', '餐饮', '中庭', '电梯厅', '卫生间', '停车场'],
  },
  office: {
    id: 'office',
    label: '办公',
    description: '写字楼/办公空间，工位/会议室/茶水间/前台',
    icon: '🏢',
    color: '#E0E8F0',
    tags: ['办公区', '会议室', '茶水间', '卫生间', '走廊', '电梯厅'],
  },
  hotel: {
    id: 'hotel',
    label: '酒店',
    description: '酒店客房，大堂/餐厅/客房/健身房/泳池',
    icon: '🏨',
    color: '#F8F0E8',
    tags: ['大堂', '餐厅', '客房', '健身房', '泳池', '会议室'],
  },
  // 园林场景
  villa_garden: {
    id: 'villa_garden',
    label: '别墅园林',
    description: '别墅庭院，花园/泳池/凉亭/硬化铺装',
    icon: '🌳',
    color: '#90B870',
    tags: ['花园', '庭院', '泳池', '硬化铺装', '凉亭', '草坪'],
  },
  park: {
    id: 'park',
    label: '公园',
    description: '公共公园，绿化/步道/广场/儿童游乐',
    icon: '🌲',
    color: '#70A060',
    tags: ['绿化', '步道', '广场', '游乐设施', '草坪'],
  },
  // VR 场景
  vr_scene: {
    id: 'vr_scene',
    label: 'VR全景',
    description: 'VR全景场景查看',
    icon: '🎮',
    color: '#8b5cf6',
    tags: [],
  },

  // 效果图场景
  renderings: {
    id: 'renderings',
    label: '效果图库',
    description: '室内/室外/建筑效果图集，1043张场景数据',
    icon: '🖼️',
    color: '#f59e0b',
    tags: ['室内', '室外', '建筑', '家庭', '办公', '商业', '园林', '市政'],
  },

  // 建筑场景
  office_building: {
    id: 'office_building',
    label: '写字楼',
    description: '高层写字楼，标准层/地下车库/设备层',
    icon: '🏗️',
    color: '#C0C8D0',
    tags: ['标准层', '地下车库', '设备层', '电梯厅', '卫生间'],
  },
  residential: {
    id: 'residential',
    label: '小区',
    description: '住宅小区，楼栋/园林/会所/车库',
    icon: '🏘️',
    color: '#D8D0C8',
    tags: ['楼栋', '园林', '会所', '地下车库', '大堂'],
  },
  commercial_complex: {
    id: 'commercial_complex',
    label: '商场综合体',
    description: '商业综合体，购物/餐饮/办公/酒店多元业态',
    icon: '🌆',
    color: '#D0C0B0',
    tags: ['商铺', '餐饮', '办公', '酒店', '地下车库', '中庭'],
  },
}

// 分类场景数据
export const CATEGORY_SCENES = {
  interior: ['residence', 'mall', 'office', 'hotel', 'renderings'],
  landscape: ['villa_garden', 'park', 'renderings'],
  architecture: ['office_building', 'residential', 'commercial_complex', 'renderings'],
}

// 世界模型统计
export const worldModelStats = {
  totalVR: 80,
  totalRooms: 98,
  byCategory: {
    '客厅': 16, '餐厅': 13, '厨房': 13, '主卧': 12,
    '次卧': 5, '卫生间': 10, '书房': 4, '其他': 15,
  },
  byPlatform: { '3d66': 64, 'Justeasy': 15, '720yun': 1 },
  byDesigner: [
    { name: '杭州萧山金灿装饰', count: 42 },
    { name: '鸿盛设计', count: 10 },
    { name: '桔子空间', count: 7 },
    { name: '杭州鑫满天装饰', count: 5 },
    { name: '其他设计师', count: 16 },
  ],
  physicsTags: [
    '地面高差', '潮湿', '防水', '狭窄通道', '滑倒风险',
    '水渍', '入户', '楼梯', '台阶', '坡道',
  ],
}


// === 自动追加修复（2026-04-16） ===================
export const SCENE_KEY_NAMES: Record<string, string> = {
  "residence": "Home",
  "mall": "Mall",
  "office": "Office",
  "hotel": "Hotel",
  "villa_garden": "Villa",
  "park": "Park",
  "office_building": "Office Building",
  "residential": "Residential",
  "commercial_complex": "Commercial",
  "ns_basement": "Basement",
  "sample": "Sample",
  "renderings": "Renderings",
}

export const SCENE_CATEGORY_MAP: Record<string, string> = {
  "residence": "indoor",
  "mall": "indoor",
  "office": "indoor",
  "hotel": "indoor",
  "villa_garden": "outdoor",
  "park": "outdoor",
  "office_building": "building",
  "residential": "building",
  "commercial_complex": "building",
  "ns_basement": "building",
  "sample": "building",
  "renderings": "indoor",
}
// =======================================================
