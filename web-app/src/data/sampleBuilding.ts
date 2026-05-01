// 示例建筑数据（单房间）
export const sampleBuilding = [
  // 地板
  {
    id: 'floor-1',
    name: '客厅地板',
    type: 'floor',
    position: [0, 0, 0],
    rotation: [0, 0, 0],
    dimensions: { width: 8, height: 0.2, depth: 6 },
    physics: {
      mass: 0,
      material: '混凝土',
      friction: 0.6,
      isStructural: true,
    },
  },
  
  // 墙体 - 后墙
  {
    id: 'wall-back',
    name: '后墙',
    type: 'wall',
    position: [0, 1.5, -3],
    rotation: [0, 0, 0],
    dimensions: { width: 8, height: 3, depth: 0.24 },
    physics: {
      mass: 2400,
      material: '砖混',
      stiffness: 25000,
      friction: 0.5,
      isStructural: true,
    },
  },
  
  // 墙体 - 左墙
  {
    id: 'wall-left',
    name: '左侧承重墙',
    type: 'wall',
    position: [-4, 1.5, 0],
    rotation: [0, Math.PI / 2, 0],
    dimensions: { width: 6, height: 3, depth: 0.24 },
    physics: {
      mass: 1800,
      material: '钢筋混凝土',
      stiffness: 30000,
      friction: 0.5,
      isStructural: true,
    },
  },
  
  // 墙体 - 右墙（有门）
  {
    id: 'wall-right',
    name: '右侧隔墙',
    type: 'wall',
    position: [4, 1.5, 0],
    rotation: [0, Math.PI / 2, 0],
    dimensions: { width: 6, height: 3, depth: 0.12 },
    physics: {
      mass: 900,
      material: '轻质砖',
      stiffness: 8000,
      friction: 0.4,
      isStructural: false,
    },
  },
  
  // 门
  {
    id: 'door-1',
    name: '客厅门',
    type: 'door',
    position: [4, 0, 1],
    rotation: [0, 0, 0],
    dimensions: { width: 0.9, height: 2.1, depth: 0.05 },
    physics: {
      mass: 25,
      material: '实木',
      stiffness: 12000,
      friction: 0.3,
    },
    function: {
      type: 'handle',
    },
    robotInteraction: {
      graspable: true,
      openable: true,
      pathObstacle: false,
    },
  },
  
  // 窗户
  {
    id: 'window-1',
    name: '客厅窗户',
    type: 'window',
    position: [0, 1.8, -3],
    rotation: [0, 0, 0],
    dimensions: { width: 1.5, height: 1.2, depth: 0.1 },
    physics: {
      mass: 15,
      material: '铝合金+玻璃',
      stiffness: 70000,
      friction: 0.2,
    },
  },
  
  // 开关
  {
    id: 'switch-1',
    name: '客厅灯开关',
    type: 'appliance',
    position: [-3.8, 1.3, 2],
    rotation: [0, Math.PI / 2, 0],
    dimensions: { width: 0.086, height: 0.086, depth: 0.01 },
    physics: {
      mass: 0.1,
      material: '塑料',
    },
    function: {
      type: 'switch',
      circuit: 'L1-客厅主灯',
      voltage: 220,
    },
    robotInteraction: {
      graspable: false,
      openable: false,
      pathObstacle: false,
    },
  },
  
  // 插座
  {
    id: 'outlet-1',
    name: '客厅插座',
    type: 'appliance',
    position: [0, 0.3, -2.76],
    rotation: [0, 0, 0],
    dimensions: { width: 0.086, height: 0.086, depth: 0.01 },
    physics: {
      mass: 0.05,
      material: '塑料',
      conductivity: 0.9,
    },
    function: {
      type: 'outlet',
      circuit: '插座回路-1',
      voltage: 220,
    },
    robotInteraction: {
      graspable: false,
      openable: false,
      pathObstacle: false,
    },
  },
]

// 任务定义
export const sampleTasks = [
  {
    id: 'task-door',
    name: '开门任务',
    description: '机器人理解门的物理属性，安全开门',
    targetObject: 'door-1',
    steps: [
      '识别门的位置和尺寸',
      '计算最佳抓取点',
      '施力开门（力矩 < 5Nm）',
      '检测门的开合状态',
    ],
    physicsKnowledge: [
      '门的质量: 25kg',
      '铰链摩擦系数: 0.1',
      '最大开启力矩: 5Nm',
      '门板厚度: 50mm',
    ],
  },
  {
    id: 'task-light',
    name: '开灯任务',
    description: '机器人理解电路布局，安全操作开关',
    targetObject: 'switch-1',
    steps: [
      '定位开关位置（高度1.3m）',
      '识别电路编号：L1-客厅主灯',
      '按压开关（压力 < 5N）',
      '检测灯光状态反馈',
    ],
    physicsKnowledge: [
      '开关高度: 1.3m（符合人体工学）',
      '电路电压: 220V AC',
      '按压行程: 3mm',
      '触发力: 2-5N',
    ],
  },
  {
    id: 'task-dishes',
    name: '洗碗任务',
    description: '理解水路和餐具物理属性',
    targetObject: 'outlet-1',
    steps: [
      '识别水槽位置',
      '理解水龙头操作方式',
      '抓取餐具（质量<500g）',
      '控制清洗力度',
    ],
    physicsKnowledge: [
      '水槽深度: 200mm',
      '水压: 0.3 MPa',
      '餐具质量: 100-500g',
      '摩擦系数: 陶瓷-橡胶 = 0.4',
    ],
  },
]
