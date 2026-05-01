/**
 * useRelationInference.ts
 * 空间关系推理 Hook — 调用 Python Inference Server (端口5000)
 */
import { useState, useCallback } from 'react'
import { API_ENDPOINTS } from '../config/api'

export interface RelationResult {
  node_i: number
  node_j: number
  name_i: string
  name_j: string
  type_i: string
  type_j: string
  position_i: [number, number, number]
  position_j: [number, number, number]
  distance_m: number
  predicted_prob: number
  relation: 'same_room' | 'diff_room'
  confidence: number
  model: string
  accuracy: string
}

export interface SceneInfo {
  num_nodes: number
  node_types: string[]
  node_names: string[]
  positions: [number, number, number][]
  features_dim: number
}

export interface PhysicsResult {
  mass_kg: number
  friction: number
  stiffness_Nm: number
  material?: string
  model: string
}

interface HealthStatus {
  spatial_encoder: boolean
  physics_mlp: boolean
  scene_nodes: number
}

export function useRelationInference() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [scene, setScene] = useState<SceneInfo | null>(null)
  const [serverStatus, setServerStatus] = useState<HealthStatus | null>(null)

  /** 健康检查 */
  const checkHealth = useCallback(async () => {
    try {
      const r = await fetch(API_ENDPOINTS.neural.health)
      const data = await r.json()
      setServerStatus(data)
      return data as HealthStatus
    } catch (e) {
      setError('Inference server not running on port 5000')
      return null
    }
  }, [])

  /** 加载场景图谱 */
  const loadScene = useCallback(async () => {
    try {
      const r = await fetch(API_ENDPOINTS.neural.scene)
      const data = await r.json()
      setScene(data as SceneInfo)
      return data as SceneInfo
    } catch (e) {
      setError('Failed to load scene')
      return null
    }
  }, [])

  /** 预测两个节点的空间关系 */
  const predictRelation = useCallback(async (node_i: number, node_j: number): Promise<RelationResult | null> => {
    setLoading(true)
    setError(null)
    try {
      const r = await fetch(API_ENDPOINTS.neural.relation, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_i, node_j }),
      })
      const data = await r.json()
      if (data.error) {
        setError(data.error)
        return null
      }
      return data as RelationResult
    } catch (e) {
      setError('Failed to connect to inference server')
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  /** 批量预测（所有相邻对）*/
  const predictAllPairs = useCallback(async (threshold: number = 50): Promise<RelationResult[]> => {
    if (!scene) return []
    const results: RelationResult[] = []
    const { num_nodes, positions } = scene

    // 快速过滤：位置距离 > threshold 的跳过
    const closePairs: [number, number][] = []
    for (let i = 0; i < num_nodes; i++) {
      for (let j = i + 1; j < num_nodes; j++) {
        const dx = positions[i][0] - positions[j][0]
        const dy = positions[i][1] - positions[j][1]
        const dz = positions[i][2] - positions[j][2]
        const dist = Math.sqrt(dx*dx + dy*dy + dz*dz)
        if (dist < threshold) {
          closePairs.push([i, j])
        }
      }
    }

    setLoading(true)
    try {
      // 批量预测
      const r = await fetch(API_ENDPOINTS.neural.relationBatch, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pairs: closePairs.map(([i, j]) => ({ node_i: i, node_j: j })) }),
      })
      const data = await r.json()
      return (data.results || []) as RelationResult[]
    } catch (e) {
      setError('Batch prediction failed')
      return []
    } finally {
      setLoading(false)
    }
  }, [scene])

  /** 预测物理属性 */
  const predictPhysics = useCallback(async (bbox: { width: number; height: number; depth: number }, category: string): Promise<PhysicsResult | null> => {
    try {
      const r = await fetch(`${API_BASE}/physics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bbox, category }),
      })
      return await r.json() as PhysicsResult
    } catch (e) {
      // Fallback to rule-based
      return rulePhysics(bbox, category)
    }
  }, [])

  return {
    loading, error, scene, serverStatus,
    checkHealth, loadScene, predictRelation, predictAllPairs, predictPhysics,
  }
}

function rulePhysics(bbox: { width: number; height: number; depth: number }, category: string): PhysicsResult {
  const { width: x, height: y, depth: z } = bbox
  const volume = x * z * y
  const matMap: Record<string, string> = {
    sofa: 'fabric', bed: 'fabric', chair: 'wood', table: 'wood',
    cabinet: 'wood', wardrobe: 'wood', tv: 'glass', refrigerator: 'metal',
    oven: 'metal', toilet: 'ceramic', bathtub: 'ceramic',
    door: 'wood', window: 'glass', lamp: 'metal',
  }
  const mat = matMap[category.toLowerCase()] || 'wood'
  const dens: Record<string, number> = { fabric: 0.35, wood: 0.65, metal: 7.8, glass: 2.5, ceramic: 2.4, stone: 2.7 }
  const d = dens[mat] ?? 0.65
  const fric: Record<string, number> = { fabric: 0.6, wood: 0.5, metal: 0.3, glass: 0.2, ceramic: 0.3 }
  const fs = fric[mat] ?? 0.4
  const stiff: Record<string, number> = { metal: 50000, glass: 70000, ceramic: 60000, stone: 40000, wood: 10000, fabric: 100 }
  return {
    mass_kg: Math.round(Math.max(volume * d * 200, 0.5) * 10) / 10,
    friction: fs,
    stiffness_Nm: stiff[mat] ?? 10000,
    material: mat,
    model: 'rule',
  }
}
