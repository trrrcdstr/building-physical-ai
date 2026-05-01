/**
 * NeuralInferencePanel.tsx
 *
 * 神经网络推理面板 — 接入真实推理服务器 (port 5000)
 *
 * 功能：
 * 1. 健康检查 + 服务器状态
 * 2. 场景图谱可视化（门/窗沿墙面排列）
 * 3. 空间关系推理（同房间 vs 不同房间）
 * 4. 批量关系预测（显示所有相邻对）
 * 5. 3D 场景集成：选择门对象 → 推理关系
 */

import React, { useState, useEffect, useCallback } from 'react'
import { API_ENDPOINTS } from '../config/api'
import './NeuralInferencePanel.css'

// ════════════════════════════════════════════════
//  类型
// ════════════════════════════════════════════════

interface HealthStatus {
  status: string
  spatial_encoder: boolean
  physics_mlp: boolean
  scene_nodes: number
  models: Record<string, string>
}

interface SceneInfo {
  num_nodes: number
  node_types: string[]
  node_names: string[]
  positions: [number, number, number][]
  features_dim: number
}

interface RelationResult {
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

interface Props {
  selectedDoorId?: number
  onSelectDoor?: (id: number) => void
  onToggleRelations?: () => void
  showRelations?: boolean
}

type Tab = 'scene' | 'relation' | 'physics'

// ════════════════════════════════════════════════
//  组件
// ════════════════════════════════════════════════

export default function NeuralInferencePanel({
  selectedDoorId,
  onSelectDoor,
  onToggleRelations,
  showRelations,
}: Props) {
  const [tab, setTab] = useState<Tab>('scene')
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [scene, setScene] = useState<SceneInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setRefreshKey(p => p + 1), 30000)
    return () => clearInterval(id)
  }, [])

  // 关系推理
  const [nodeI, setNodeI] = useState(0)
  const [nodeJ, setNodeJ] = useState(1)
  const [relationResult, setRelationResult] = useState<RelationResult | null>(null)

  // 批量推理
  const [batchResults, setBatchResults] = useState<RelationResult[]>([])
  const [showBatch, setShowBatch] = useState(false)

  // ── 健康检查（30秒轮询） ─────────────────────────────
  useEffect(() => {
    fetch(API_ENDPOINTS.neural.health)
      .then(r => r.json())
      .then(data => setHealth(data as HealthStatus))
      .catch(() => setError('推理服务器未运行'))
  }, [refreshKey])

  // ── 加载场景（刷新触发） ─────────────────────────────
  const loadScene = useCallback(async () => {
    setLoading(true)
    try {
      // 优先从 v1 API 加载（更完整的场景数据）
      const r = await fetch(API_ENDPOINTS.scene.scene)
      const data = await r.json()
      if (data && data.nodes && data.nodes.length > 0) {
        // 转换为 NeuralInferencePanel 的 SceneInfo 格式
        const nodes = data.nodes as any[]
        setScene({
          num_nodes: nodes.length,
          node_types: nodes.map((n: any) => n.type || n.node_type || 'unknown'),
          node_names: nodes.map((n: any) => n.name || n.label || n.id || `Node-${n.id}`),
          positions: nodes.map((n: any) => n.position || [0, 0, 0]) as [number, number, number][],
          features_dim: data.embedding_dim || 120,
        })
      }
    } catch {
      // fallback: 从 v0 API 加载
      try {
        const r = await fetch(API_ENDPOINTS.neural.scene)
        const data = await r.json()
        if (data && data.positions) {
          const positions = data.positions as [number, number, number][]
          const n = positions.length
          setScene({
            num_nodes: n,
            node_types: data.types || Array(n).fill('door'),
            node_names: data.names || positions.map((_, i) => `Door-${i}`),
            positions,
            features_dim: 44,
          })
        }
      } catch {
        // 静默失败，不显示错误
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (health?.spatial_encoder) {
      loadScene()
    }
  }, [health, loadScene, refreshKey])

  // ── 推理单个关系 ─────────────────────────────────
  const runInference = useCallback(async (i?: number, j?: number) => {
    if (!scene) return
    const ni = i ?? nodeI
    const nj = j ?? nodeJ
    setLoading(true)
    try {
      const r = await fetch(API_ENDPOINTS.neural.relation, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_i: ni, node_j: nj }),
      })
      const data = await r.json()
      setRelationResult(data as RelationResult)
    } catch {
      setError('推理失败')
    } finally {
      setLoading(false)
    }
  }, [nodeI, nodeJ, scene])

  // ── 批量推理 ──────────────────────────────────────
  const runBatchInference = useCallback(async () => {
    if (!scene) return
    setLoading(true)
    setShowBatch(true)
    try {
      const pairs: [number, number][] = []
      const { positions, num_nodes } = scene
      for (let i = 0; i < num_nodes; i++) {
        for (let j = i + 1; j < num_nodes; j++) {
          const dx = positions[i][0] - positions[j][0]
          const dy = positions[i][1] - positions[j][1]
          const dz = positions[i][2] - positions[j][2]
          const dist = Math.sqrt(dx*dx + dy*dy + dz*dz)
          if (dist < 20) {
            pairs.push([i, j])
          }
        }
      }

      const r = await fetch(API_ENDPOINTS.neural.relationBatch, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pairs: pairs.map(([i, j]) => ({ node_i: i, node_j: j })) }),
      })
      const data = await r.json()
      setBatchResults((data.results || []) as RelationResult[])
    } catch {
      setError('批量推理失败')
    } finally {
      setLoading(false)
    }
  }, [scene])

  const serverOk = health?.spatial_encoder

  // ── 快捷测试数据 ─────────────────────────────────
  const quickTests = [
    [0, 1], [0, 5], [0, 10], [0, 20],
    [10, 50], [20, 80], [50, 100],
  ]

  return (
    <div className="neural-panel">
      {/* Tab 切换 */}
      <div className="neural-tabs">
        <button className={'ntab ' + (tab === 'scene' ? 'active' : '')} onClick={() => setTab('scene')}>
          🌐 场景图谱
        </button>
        <button className={'ntab ' + (tab === 'relation' ? 'active' : '')} onClick={() => setTab('relation')}>
          🔗 关系推理
        </button>
        <button className={'ntab ' + (tab === 'physics' ? 'active' : '')} onClick={() => setTab('physics')}>
          ⚛️ 物理预测
        </button>
      </div>

      {/* 服务器状态 */}
      <div className="server-status">
        <span className={'dot ' + (serverOk ? 'green' : 'red')} />
        <span className="status-text">
          {serverOk
            ? `NN服务器 ✅ SpatialEncoder (${health?.scene_nodes}节点 · ${health?.models?.SpatialEncoder || 'v1'})`
            : error || 'NN服务器 ❌ (port 5000)'}
        </span>
        {!serverOk && (
          <button className="retry-btn" onClick={() => fetch(`${API_BASE}/health`).then(r => r.json()).then(setHealth).catch(() => {})}>
            重试
          </button>
        )}
      </div>

      {/* ── 场景图谱 Tab ── */}
      {tab === 'scene' && (
        <div className="tab-content">
          <div className="section-title">🏗️ 建筑空间图谱（151门/窗沿墙分布）</div>
          {scene ? (
            <>
              <div className="stats-row">
                <div className="stat-card">
                  <div className="stat-num">{scene.num_nodes}</div>
                  <div className="stat-label">总对象</div>
                </div>
                <div className="stat-card">
                  <div className="stat-num door-color">{scene.node_types.filter(t => t === 'door').length}</div>
                  <div className="stat-label">门</div>
                </div>
                <div className="stat-card">
                  <div className="stat-num window-color">{scene.node_types.filter(t => t === 'window').length}</div>
                  <div className="stat-label">窗</div>
                </div>
                <div className="stat-card">
                  <div className="stat-num">{Math.max(...scene.positions.map(p => p[0]))}m</div>
                  <div className="stat-label">总长度</div>
                </div>
              </div>

              {/* 1D 空间可视化 */}
              <div className="scene-vis">
                <div className="vis-title">沿墙空间分布</div>
                <div className="vis-bar">
                  {scene.positions.map((pos, i) => (
                    <div
                      key={i}
                      className={'node-dot ' + scene.node_types[i]}
                      style={{ left: `${(pos[0] / 310) * 100}%` }}
                      title={`#${i} ${scene.node_names[i]} (${scene.node_types[i]}) @ X={pos[0].toFixed(1)}m`}
                      onClick={() => {
                        setNodeI(i)
                        setNodeJ(Math.min(i + 1, scene.num_nodes - 1))
                        onSelectDoor?.(i)
                        setTab('relation')
                      }}
                    />
                  ))}
                </div>
                <div className="vis-axis">
                  <span>0m</span><span>50m</span><span>100m</span>
                  <span>150m</span><span>200m</span><span>250m</span><span>300m</span>
                </div>
              </div>

              <div className="section-title mt">📊 批量关系推理</div>
              <button className="action-btn" onClick={runBatchInference} disabled={loading}>
                {loading ? '推理中...' : '🔍 推理所有相邻对(dist&lt;20m)'}
              </button>

              {showBatch && batchResults.length > 0 && (
                <div className="batch-results">
                  {(() => {
                    const same = batchResults.filter(r => r.relation === 'same_room')
                    const diff = batchResults.filter(r => r.relation === 'diff_room')
                    return (
                      <div className="batch-summary">
                        <div className="batch-stat same">✅ 同房间: {same.length}对</div>
                        <div className="batch-stat diff">🚫 不同: {diff.length}对</div>
                      </div>
                    )
                  })()}
                  <div className="batch-list">
                    {batchResults.slice(0, 15).map((r, i) => (
                      <div key={i} className={'pair-row ' + r.relation}>
                        <span className="pair-id">#{r.node_i}</span>
                        <span className="pair-arrow">↔</span>
                        <span className="pair-id">#{r.node_j}</span>
                        <span className="pair-type">{r.type_i}→{r.type_j}</span>
                        <span className="pair-dist">{r.distance_m}m</span>
                        <span className={'pair-rel ' + r.relation}>
                          {r.relation === 'same_room' ? '🟢同' : '🔴异'}
                          <span className="pair-conf">({(r.confidence * 100).toFixed(0)}%)</span>
                        </span>
                      </div>
                    ))}
                    {batchResults.length > 15 && (
                      <div className="batch-more">+ 还有 {batchResults.length - 15} 对...</div>
                    )}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="loading-state">
              {loading ? '加载场景数据...' : '连接推理服务器以查看场景图谱'}
            </div>
          )}
        </div>
      )}

      {/* ── 关系推理 Tab ── */}
      {tab === 'relation' && (
        <div className="tab-content">
          <div className="section-title">🔗 空间关系推理</div>
          <div className="model-info">
            <span className="badge blue">SpatialEncoder</span>
            <span className="badge green">Val Acc: 98.1%</span>
            <span className="badge">F1: 0.942</span>
          </div>

          {/* 3D场景控制 */}
          <div className="relation-3d-controls">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={showRelations ?? false}
                onChange={onToggleRelations}
              />
              <span>🔗 显示关系线（3D场景）</span>
            </label>
          </div>

          {/* 节点选择器 */}
          <div className="pair-selector">
            <div className="selector-group">
              <label>节点 A</label>
              <select value={nodeI} onChange={e => setNodeI(Number(e.target.value))}>
                {scene && scene.node_names.map((name, i) => (
                  <option key={i} value={i}>
                    #{i} {name} ({scene.node_types[i]})
                  </option>
                ))}
              </select>
            </div>
            <div className="pair-vs">↔</div>
            <div className="selector-group">
              <label>节点 B</label>
              <select value={nodeJ} onChange={e => setNodeJ(Number(e.target.value))}>
                {scene && scene.node_names.map((name, i) => (
                  <option key={i} value={i}>
                    #{i} {name} ({scene.node_types[i]})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button className="action-btn" onClick={() => runInference()} disabled={loading || !scene}>
            {loading ? '推理中...' : '🧠 推理空间关系'}
          </button>

          {/* 推理结果 */}
          {relationResult && (
            <div className="relation-result">
              <div className="result-header">
                <span className="result-names">
                  {relationResult.name_i} ↔ {relationResult.name_j}
                </span>
                <span className={'result-badge ' + relationResult.relation}>
                  {relationResult.relation === 'same_room' ? '🟢 同房间' : '🔴 不同房间'}
                </span>
              </div>

              <div className="result-metrics">
                <div className="metric">
                  <div className="metric-num">{relationResult.distance_m}m</div>
                  <div className="metric-label">实际距离</div>
                </div>
                <div className="metric">
                  <div className="metric-num">{(relationResult.predicted_prob * 100).toFixed(1)}%</div>
                  <div className="metric-label">同房间概率</div>
                </div>
                <div className="metric">
                  <div className="metric-num">{(relationResult.confidence * 100).toFixed(1)}%</div>
                  <div className="metric-label">置信度</div>
                </div>
              </div>

              <div className="result-positions">
                <div>📍 A: [{relationResult.position_i.map(v => v.toFixed(2)).join(', ')}]</div>
                <div>📍 B: [{relationResult.position_j.map(v => v.toFixed(2)).join(', ')}]</div>
              </div>

              <div className="result-model">
                模型: {relationResult.model} · 训练精度: {relationResult.accuracy}
              </div>
            </div>
          )}

          {/* 快捷测试 */}
          <div className="section-title mt">⚡ 快捷测试</div>
          <div className="quick-tests">
            {quickTests.map(([i, j]) => (
              <button key={`${i}-${j}`} className="quick-btn"
                onClick={() => { setNodeI(i); setNodeJ(j); runInference(i, j) }}>
                #{i} ↔ #{j}
              </button>
            ))}
          </div>

          {/* 选中门信息 */}
          {selectedDoorId !== undefined && (
            <div className="selected-door">
              <div className="section-title mt">🚪 选中对象</div>
              <div className="selected-door-info">
                #{selectedDoorId} {scene?.node_names[selectedDoorId] || ''}
                {' '}({scene?.node_types[selectedDoorId] || ''})
                {scene?.positions[selectedDoorId] && (
                  <span className="door-pos">
                    @ X={scene.positions[selectedDoorId][0].toFixed(1)}m
                  </span>
                )}
              </div>
              <div className="quick-tests">
                {[0, 1, 5, 10, 20, 50, 100].filter(x => x !== selectedDoorId).slice(0, 6).map(j => (
                  <button key={j} className="quick-btn"
                    onClick={() => { setNodeI(selectedDoorId); setNodeJ(j); runInference(selectedDoorId, j) }}>
                    vs #{j}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── 物理预测 Tab ── */}
      {tab === 'physics' && (
        <div className="tab-content">
          <div className="section-title">⚛️ 物理属性预测</div>
          <div className="model-info">
            <span className="badge blue">规则引擎</span>
            <span className="badge">PhysicsMLP 训练中</span>
          </div>

          <div className="physics-table">
            <div className="ph-row header">
              <span>类型</span><span>质量</span><span>摩擦</span><span>刚度</span><span>材质</span>
            </div>
            {[
              { type: '🚪 门 (door)', mass: '10-30kg', fric: '0.3-0.5', stiff: 'wood 10k', mat: 'wood' },
              { type: '🪟 窗 (window)', mass: '15-40kg', fric: '0.2-0.3', stiff: 'glass 70k', mat: 'glass' },
              { type: '🛋️ 沙发 (sofa)', mass: '30-80kg', fric: '0.5-0.6', stiff: 'fabric 100', mat: 'fabric' },
              { type: '🪑 桌子 (table)', mass: '20-60kg', fric: '0.4-0.5', stiff: 'wood 10k', mat: 'wood' },
              { type: '🗄️ 柜子 (cabinet)', mass: '40-100kg', fric: '0.4-0.5', stiff: 'wood 10k', mat: 'wood' },
              { type: '💡 灯具 (lamp)', mass: '2-8kg', fric: '0.3', stiff: 'metal 50k', mat: 'metal' },
            ].map(row => (
              <div key={row.type} className="ph-row">
                <span>{row.type}</span>
                <span>{row.mass}</span>
                <span>{row.fric}</span>
                <span>{row.stiff}</span>
                <span className={'badge ' + row.mat}>{row.mat}</span>
              </div>
            ))}
          </div>

          <div className="physics-note">
            <strong>💡 物理推断原理</strong>
            <p>质量 = 体积 × 密度 × 经验系数</p>
            <p>摩擦/刚度 = 材质类型映射</p>
            <p>NN 模型 PhysicsMLP 正在训练中</p>
          </div>
        </div>
      )}
    </div>
  )
}
