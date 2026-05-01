// 材质物理知识库 - 内置版本
export const MATERIAL_PHYSICS_DB: Record<string, {
  material_type: string;
  friction_dry: number;
  friction_wet: number;
  surface_density: number;
  max_force_n: number;
  max_speed_ms: number;
  drill_risk: 'low' | 'medium' | 'high';
  drill_risk_text: string;
  safe_tools: string[];
  warnings: string[];
  constraints: string[];
}> = {
  '玻璃': {
    material_type: '钢化玻璃',
    friction_dry: 0.35,
    friction_wet: 0.18,
    surface_density: 20.0,
    max_force_n: 5,
    max_speed_ms: 0.3,
    drill_risk: 'high',
    drill_risk_text: '高风险 - 钢化玻璃禁止钻孔',
    safe_tools: ['橡胶刮刀', '软海绵', '玻璃刮板'],
    warnings: ['边缘脆弱', '湿态摩擦降低49%', '冲击易碎裂'],
    constraints: ['力度<5N', '降速至0.3m/s', '禁止钻孔', '使用软质工具']
  },
  '瓷砖': {
    material_type: '瓷砖',
    friction_dry: 0.50,
    friction_wet: 0.35,
    surface_density: 24.0,
    max_force_n: 100,
    max_speed_ms: 0.5,
    drill_risk: 'medium',
    drill_risk_text: '中风险 - 注意避开接缝和防水层',
    safe_tools: ['电锤', '冲击钻', '玻璃钻头'],
    warnings: ['接缝处谨慎钻孔', '避免破坏防水层'],
    constraints: ['控制钻孔深度<30mm', '避开接缝区域']
  },
  '木材': {
    material_type: '实木地板',
    friction_dry: 0.45,
    friction_wet: 0.30,
    surface_density: 14.0,
    max_force_n: 50,
    max_speed_ms: 0.4,
    drill_risk: 'low',
    drill_risk_text: '低风险 - 实木地板钻孔安全',
    safe_tools: ['手电钻', '木工锯', '木工螺丝刀'],
    warnings: ['注意钉子位置', '避免开裂'],
    constraints: ['预钻小孔', '垂直施力']
  },
  '混凝土': {
    material_type: '混凝土',
    friction_dry: 0.55,
    friction_wet: 0.40,
    surface_density: 48.0,
    max_force_n: 200,
    max_speed_ms: 0.25,
    drill_risk: 'medium',
    drill_risk_text: '中风险 - 检查承重结构',
    safe_tools: ['电锤', '混凝土钻头', '冲击钻'],
    warnings: ['承重墙禁止破坏', '检查是否有管线'],
    constraints: ['确认非承重墙', '深度限制40mm']
  },
  '不锈钢': {
    material_type: '不锈钢',
    friction_dry: 0.25,
    friction_wet: 0.12,
    surface_density: 64.0,
    max_force_n: 150,
    max_speed_ms: 0.3,
    drill_risk: 'low',
    drill_risk_text: '低风险 - 不锈钢表面钻孔',
    safe_tools: ['电锤', '金属钻头', '润滑油'],
    warnings: ['边角锋利注意防护', '需充分冷却'],
    constraints: ['使用润滑剂', '边角打磨处理']
  },
  '金属': {
    material_type: '铝合金',
    friction_dry: 0.28,
    friction_wet: 0.15,
    surface_density: 27.0,
    max_force_n: 100,
    max_speed_ms: 0.3,
    drill_risk: 'low',
    drill_risk_text: '低风险 - 铝合金钻孔安全',
    safe_tools: ['冲击钻', '金属锯', '锉刀'],
    warnings: ['注意电气接地'],
    constraints: ['避免触电风险', '佩戴护目镜']
  },
  '石材': {
    material_type: '大理石',
    friction_dry: 0.45,
    friction_wet: 0.30,
    surface_density: 54.0,
    max_force_n: 100,
    max_speed_ms: 0.3,
    drill_risk: 'medium',
    drill_risk_text: '中风险 - 大理石钻孔需专业工具',
    safe_tools: ['石材切割机', '水平仪', '金刚石钻头'],
    warnings: ['接缝处谨慎钻孔', '需水冷'],
    constraints: ['使用水冷', '避免振动']
  }
};

export function inferMaterialFromTask(taskDescription: string): string {
  const text = taskDescription.toLowerCase();
  if (text.includes('玻璃') || text.includes('隔断') || text.includes('淋浴')) return '玻璃';
  if (text.includes('瓷砖') || text.includes('卫生间') || text.includes('浴室')) return '瓷砖';
  if (text.includes('木') || text.includes('地板') || text.includes('家具')) return '木材';
  if (text.includes('混凝土') || text.includes('水泥') || text.includes('墙面')) return '混凝土';
  if (text.includes('不锈钢') || text.includes('龙头') || text.includes('五金')) return '不锈钢';
  if (text.includes('金属') || text.includes('铝合金') || text.includes('门窗')) return '金属';
  if (text.includes('大理石') || text.includes('石材') || text.includes('台面')) return '石材';
  return '瓷砖'; // 默认
}
