/**
 * usePhysicsInference.ts
 * 物理推理 Hook — 封装规则引擎 + 后续 NN 模型
 */
import { useState, useCallback } from 'react'

export interface PhysicsResult {
  mass_kg: number
  friction_static: number
  friction_dynamic: number
  stiffness_Nm: number
  surface_hardness: '硬' | '软' | '中'
  deformable: boolean
  material: string
  physics_confidence: number
  model: 'nn' | 'rule'
}

const MAT_DENSITY: Record<string, number> = {
  fabric: 0.35, wood: 0.65, metal: 7.8, glass: 2.5,
  ceramic: 2.4, stone: 2.7, plastic: 0.95, rubber: 1.1,
}

const MAT_FRICTION: Record<string, [number, number]> = {
  fabric: [0.6, 0.5], wood: [0.5, 0.4],
  metal: [0.3, 0.2], glass: [0.2, 0.15],
  ceramic: [0.3, 0.25], stone: [0.55, 0.45],
}

const CAT_MAP: Record<string, string> = {
  sofa: 'fabric', bed: 'fabric', chair: 'wood', table: 'wood',
  cabinet: 'wood', wardrobe: 'wood', tv: 'glass',
  refrigerator: 'metal', oven: 'metal', microwave: 'metal',
  toilet: 'ceramic', bathtub: 'ceramic', mirror: 'glass',
  'wall': 'stone', floor: 'stone', ceiling: 'stone',
  // IISFREE灯具材质
  lamp: 'metal', downlight: 'metal', track_light: 'aluminum',
  pendant_light: 'aluminum',
}

function inferMaterial(name: string, category: string): string {
  const s = (name + category).toLowerCase()
  for (const [key, val] of Object.entries(CAT_MAP)) {
    if (s.includes(key)) return val
  }
  return 'wood'
}

export function usePhysicsInference() {
  const [loading, setLoading] = useState(false)

  /** 根据对象几何和类别推断物理属性 */
  const infer = useCallback((
    name: string,
    category: string,
    bbox: { width: number; depth: number; height: number },
  ): PhysicsResult => {
    const { width: x, depth: z, height: y } = bbox
    const volume = x * z * y

    const mat = inferMaterial(name, category)
    const d = MAT_DENSITY[mat] ?? 0.65
    const [fs, fd] = MAT_FRICTION[mat] ?? [0.4, 0.3]

    const mass = Math.max(volume * d * 200, 0.5)

    const stiffMap: Record<string, number> = {
      metal: 50000, glass: 70000, ceramic: 60000,
      stone: 40000, wood: 10000, fabric: 100,
    }

    return {
      mass_kg: Math.round(mass * 10) / 10,
      friction_static: fs,
      friction_dynamic: Math.round(fs * fd * 1000) / 1000,
      stiffness_Nm: stiffMap[mat] ?? 10000,
      surface_hardness:
        ['metal', 'glass', 'ceramic', 'stone'].includes(mat) ? '硬' :
        mat === 'fabric' ? '软' : '中',
      deformable: mat === 'fabric',
      material: mat,
      physics_confidence: 0.75,
      model: 'rule',
    }
  }, [])

  return { infer, loading }
}
