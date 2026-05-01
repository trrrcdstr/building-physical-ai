// 材质物理属性数据库 - 来自 knowledge/material_physics_data.json
export const MATERIAL_PHYSICS: Record<string, {
  friction: number
  density: number
  thermalConductivity: number
  Young: number
  compressiveStrength: number
  color: string
  roughness: number
  safeTools: string[]
  warnings: string[]
}> = {
  '瓷砖': { friction: 0.50, density: 2400, thermalConductivity: 1.5, Young: 30000, compressiveStrength: 30, color: '#E8E0D8', roughness: 0.3, safeTools: ['电锤', '冲击钻'], warnings: ['避免破坏防水层'] },
  '实木地板': { friction: 0.45, density: 700, thermalConductivity: 0.15, Young: 11000, compressiveStrength: 40, color: '#C4A882', roughness: 0.6, safeTools: ['手电钻', '木工锯'], warnings: ['注意钉子位置'] },
  '混凝土': { friction: 0.55, density: 2400, thermalConductivity: 1.8, Young: 30000, compressiveStrength: 30, color: '#808080', roughness: 0.8, safeTools: ['电锤', '切割机'], warnings: ['承重墙禁止破坏'] },
  '钢化玻璃': { friction: 0.35, density: 2500, thermalConductivity: 1.2, Young: 72000, compressiveStrength: 120, color: '#88CCE0', roughness: 0.1, safeTools: ['玻璃吸盘', '软尺'], warnings: ['边缘脆弱，避免撞击'] },
  '大理石': { friction: 0.45, density: 2700, thermalConductivity: 2.9, Young: 55000, compressiveStrength: 100, color: '#F0EDE8', roughness: 0.25, safeTools: ['石材切割机', '水平仪'], warnings: ['接缝处谨慎钻孔'] },
  '石膏板': { friction: 0.30, density: 800, thermalConductivity: 0.25, Young: 2500, compressiveStrength: 5, color: '#FAF8F5', roughness: 0.7, safeTools: ['电动螺丝刀', '电钻'], warnings: ['承载力有限，禁止挂重物'] },
  '铝合金': { friction: 0.28, density: 2700, thermalConductivity: 160, Young: 70000, compressiveStrength: 200, color: '#C0C0C0', roughness: 0.2, safeTools: ['冲击钻', '金属锯'], warnings: ['注意电气接地'] },
  '不锈钢': { friction: 0.25, density: 8000, thermalConductivity: 16, Young: 200000, compressiveStrength: 520, color: '#D4D4D4', roughness: 0.15, safeTools: ['电锤', '抛光机'], warnings: ['边角锋利，注意防护'] },
  '铜': { friction: 0.30, density: 8500, thermalConductivity: 380, Young: 110000, compressiveStrength: 200, color: '#B87333', roughness: 0.2, safeTools: ['电烙铁', '手动工具'], warnings: ['导电，避免触电'] },
  '普通砖墙': { friction: 0.50, density: 1800, thermalConductivity: 0.8, Young: 15000, compressiveStrength: 10, color: '#C4917A', roughness: 0.7, safeTools: ['电锤', '冲击钻'], warnings: ['检查是否有管线'] },
  '承重混凝土墙': { friction: 0.60, density: 2500, thermalConductivity: 1.8, Young: 35000, compressiveStrength: 35, color: '#686868', roughness: 0.85, safeTools: [], warnings: ['结构安全，禁止破坏！'] },
  '卫生陶瓷': { friction: 0.38, density: 2400, thermalConductivity: 1.0, Young: 60000, compressiveStrength: 150, color: '#FFFFFF', roughness: 0.1, safeTools: ['橡胶锤', '水平尺'], warnings: ['表面光滑，小心磕碰'] },
  '黄铜': { friction: 0.25, density: 8500, thermalConductivity: 120, Young: 100000, compressiveStrength: 350, color: '#D4AF37', roughness: 0.15, safeTools: ['扳手', '螺丝刀'], warnings: ['合金，注意防腐'] },
}

export const OBJECT_PHYSICS_MAP: Record<string, {
  material: string
  thickness: number
  density: number
  friction: number
  Young: number
  compressiveStrength: number
  maxLoad: number
  drillDepth: number
  approachSpeed: number
}> = {
  'wall_brick': { material: '普通砖墙', thickness: 240, density: 1800, friction: 0.50, Young: 15000, compressiveStrength: 10, maxLoad: 50, drillDepth: 50, approachSpeed: 0.3 },
  'wall_concrete': { material: '混凝土', thickness: 200, density: 2400, friction: 0.55, Young: 30000, compressiveStrength: 30, maxLoad: 200, drillDepth: 40, approachSpeed: 0.25 },
  'wall_load_bearing': { material: '承重混凝土墙', thickness: 300, density: 2500, friction: 0.60, Young: 35000, compressiveStrength: 35, maxLoad: 999, drillDepth: 0, approachSpeed: 0 },
  'wall_partition': { material: '普通砖墙', thickness: 120, density: 1800, friction: 0.50, Young: 15000, compressiveStrength: 10, maxLoad: 30, drillDepth: 60, approachSpeed: 0.4 },
  'floor_tile': { material: '瓷砖', thickness: 10, density: 2400, friction: 0.50, Young: 30000, compressiveStrength: 30, maxLoad: 500, drillDepth: 30, approachSpeed: 0.5 },
  'floor_wood': { material: '实木地板', thickness: 18, density: 700, friction: 0.45, Young: 11000, compressiveStrength: 40, maxLoad: 200, drillDepth: 25, approachSpeed: 0.4 },
  'ceiling_drywall': { material: '石膏板', thickness: 12, density: 800, friction: 0.30, Young: 2500, compressiveStrength: 5, maxLoad: 5, drillDepth: 35, approachSpeed: 0.2 },
  'glass_window': { material: '钢化玻璃', thickness: 8, density: 2500, friction: 0.35, Young: 72000, compressiveStrength: 120, maxLoad: 50, drillDepth: 0, approachSpeed: 0 },
}

export function inferMaterialFromObject(obj: { type?: string; name?: string; material?: string }): string | null {
  const text = [obj.type, obj.name, obj.material].filter(Boolean).join(' ').toLowerCase()
  if (text.includes('砖') || text.includes('brick')) return '普通砖墙'
  if (text.includes('混凝土') || text.includes('concrete')) return '混凝土'
  if (text.includes('load') || text.includes('承重')) return '承重混凝土墙'
  if (text.includes('partition') || text.includes('隔墙')) return '普通砖墙'
  if (text.includes('tile') || text.includes('floor') && text.includes('瓷')) return '瓷砖'
  if (text.includes('wood') || text.includes('木') || text.includes('地板')) return '实木地板'
  if (text.includes('drywall') || text.includes('石膏') || text.includes('天花')) return '石膏板'
  if (text.includes('glass') || text.includes('玻璃')) return '钢化玻璃'
  return null
}