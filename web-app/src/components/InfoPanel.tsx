import { useState } from 'react'
import { useBuildingStore } from '../store/buildingStore'
import './InfoPanel.css'

// ─── 物理推理本地计算（无 API 时 fallback）───
function computePhysics(obj: any) {
  const bbox = obj?.dimensions ?? { width: 1, depth: 1, height: 1 }
  const { width: x, depth: z, height: y } = bbox
  const volume = x * z * y
  const cat = obj?.category ?? obj?.type ?? ''
  const name = obj?.name ?? ''

  // 材质推断
  const matMap: Record<string, string> = {
    sofa: 'fabric', bed: 'fabric', chair: 'wood',
    table: 'wood', cabinet: 'wood', wardrobe: 'wood',
    tv: 'glass', refrigerator: 'metal', oven: 'metal',
    toilet: 'ceramic', bathtub: 'ceramic', mirror: 'glass',
    'wall': 'stone', 'floor': 'stone', 'ceiling': 'stone',
  }
  let mat = 'composite'
  for (const [k, v] of Object.entries(matMap)) {
    if (name.includes(k) || cat.includes(k)) { mat = v; break }
  }

  const dens: Record<string, number> = {
    fabric: 0.35, wood: 0.65, metal: 7.8, glass: 2.5, ceramic: 2.4, stone: 2.7,
  }
  const fricS: Record<string, number> = {
    fabric: 0.6, wood: 0.5, metal: 0.3, glass: 0.2, ceramic: 0.3, stone: 0.55,
  }
  const d = dens[mat] ?? 0.65
  const fs = fricS[mat] ?? 0.4
  const mass = Math.max(volume * d * 200, 0.5)

  return {
    mass_kg: Math.round(mass * 10) / 10,
    friction_static: fs,
    friction_dynamic: Math.round(fs * 0.85 * 1000) / 1000,
    stiffness_Nm: mat === 'metal' ? 50000 : mat === 'glass' ? 70000 : mat === 'stone' ? 40000 : 10000,
    surface_hardness: ['metal', 'glass', 'ceramic', 'stone'].includes(mat) ? '硬' : mat === 'fabric' ? '软' : '中',
    deformable: mat === 'fabric',
    material: mat,
    physics_confidence: 0.75,
  }
}

type Tab = 'info' | 'physics' | 'world'

export default function InfoPanel() {
  const [tab, setTab] = useState<Tab>('info')
  const selectedObject = useBuildingStore((s) => s.selectedObject)

  const physics = selectedObject ? computePhysics(selectedObject) : null

  return (
    <div className="info-panel">
      {/* Tab 切换 */}
      <div className="info-tabs">
        <button
          className={'tab ' + (tab === 'info' ? 'active' : '')}
          onClick={() => setTab('info')}
        >
          📦 详情
        </button>
        <button
          className={'tab ' + (tab === 'physics' ? 'active' : '')}
          onClick={() => setTab('physics')}
        >
          ⚛️ 物理推理
        </button>
        <button
          className={'tab ' + (tab === 'world' ? 'active' : '')}
          onClick={() => setTab('world')}
        >
          🌍 世界模型
        </button>
      </div>

      {/* ── 详情 Tab ── */}
      {tab === 'info' && (
        <>
          {selectedObject ? (
            <div className="panel-content">
              <h3>📦 {selectedObject.name}</h3>

              {selectedObject.vrData && (
                <div className="section">
                  <h4>🖼️ VR全景</h4>
                  <div className="grid-2">
                    <span>VR编号</span><span>#{selectedObject.vrData.vr_id}</span>
                    <span>平台</span><span className="badge green">{selectedObject.vrData.platform}</span>
                    <span>设计师</span><span>{selectedObject.vrData.designer || '未知'}</span>
                    <span>房间</span><span>{selectedObject.vrData.room_name}</span>
                    <span>类别</span><span>{selectedObject.vrData.room_category}</span>
                  </div>
                  {selectedObject.vrData.physics_tags?.length > 0 && (
                    <div className="tag-list">
                      {selectedObject.vrData.physics_tags.slice(0, 6).map((t: string) => (
                        <span key={t} className="tag">{t}</span>
                      ))}
                    </div>
                  )}
                  <button
                    className="vr-btn"
                    onClick={() => {
                      const vr = selectedObject.vrData
                      if (!vr) return
                      const { platform, vr_id } = vr
                      if (platform === '3d66') window.open(`https://www.3d66.com/vr/index_detail_${vr_id}.html`, '_blank')
                      else if (platform === 'Justeasy') window.open(`https://www.justeasy.cn/vr/${vr_id}.html`, '_blank')
                      else window.open(`https://720yun.com/t/${vr_id}`, '_blank')
                    }}
                  >
                    🌐 打开VR全景
                  </button>
                </div>
              )}

              <div className="section">
                <h4>📐 几何属性</h4>
                <div className="grid-2">
                  <span>宽</span><span>{selectedObject.dimensions?.width}m</span>
                  <span>深</span><span>{selectedObject.dimensions?.depth}m</span>
                  <span>高</span><span>{selectedObject.dimensions?.height}m</span>
                  <span>类型</span><span>{selectedObject.type}</span>
                </div>
              </div>

              {selectedObject.physics && (
                <div className="section">
                  <h4>⚛️ 物理属性</h4>
                  <div className="grid-2">
                    {selectedObject.physics.mass && <><span>质量</span><span>{selectedObject.physics.mass} kg</span></>}
                    {selectedObject.physics.friction && <><span>摩擦</span><span>{selectedObject.physics.friction}</span></>}
                    {selectedObject.physics.stiffness && <><span>刚度</span><span>{selectedObject.physics.stiffness} MPa</span></>}
                    {selectedObject.physics.material && <><span>材质</span><span>{selectedObject.physics.material}</span></>}
                  </div>
                </div>
              )}

              {selectedObject.robot && (
                <div className="section">
                  <h4>🤖 机器人能力</h4>
                  <div className="cap-grid">
                    {Object.entries(selectedObject.robot).map(([k, v]) => (
                      <div key={k} className={'cap ' + (v ? 'ok' : 'no')}>
                        {String(v).startsWith('true') || v === true ? '✅' : '⚪'} {k}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="physics-note">
                <strong>💡 物理常识</strong>
                <p>此{selectedObject.type}的空间物理属性可用于机器人路径规划和力控交互。</p>
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">🏠</div>
              <div className="empty-title">点击3D场景中的任意房间</div>
              <div className="empty-desc">查看物理属性和VR数据</div>
            </div>
          )}
        </>
      )}

      {/* ── 物理推理 Tab ── */}
      {tab === 'physics' && (
        <div className="panel-content">
          <h3>⚛️ 神经网络物理推理</h3>

          {!selectedObject ? (
            <div className="empty-state">
              <div className="empty-icon">🧠</div>
              <div className="empty-title">选择对象以推理</div>
              <div className="empty-desc">点击房间获取物理属性预测</div>
            </div>
          ) : physics ? (
            <>
              <div className="section">
                <h4>📊 预测结果</h4>
                <div className="phys-cards">
                  <div className="phys-card">
                    <div className="phys-num" style={{ color: '#4CAF50' }}>{physics.mass_kg}</div>
                    <div className="phys-unit">kg</div>
                    <div className="phys-label">质量</div>
                  </div>
                  <div className="phys-card">
                    <div className="phys-num" style={{ color: '#2196F3' }}>{physics.friction_static}</div>
                    <div className="phys-unit"></div>
                    <div className="phys-label">静摩擦系数</div>
                  </div>
                  <div className="phys-card">
                    <div className="phys-num" style={{ color: '#9C27B0' }}>{Math.round(physics.stiffness_Nm / 1000)}k</div>
                    <div className="phys-unit">N/m</div>
                    <div className="phys-label">刚度</div>
                  </div>
                  <div className="phys-card">
                    <div className="phys-num" style={{ color: '#ff9800' }}>{physics.surface_hardness}</div>
                    <div className="phys-unit"></div>
                    <div className="phys-label">表面硬度</div>
                  </div>
                </div>
              </div>

              <div className="section">
                <h4>🔬 材质分析</h4>
                <div className="grid-2">
                  <span>推断材质</span>
                  <span className="badge blue">{physics.material}</span>
                  <span>动摩擦</span><span>{physics.friction_dynamic}</span>
                  <span>可变形</span>
                  <span style={{ color: physics.deformable ? '#f59e0b' : '#10b981' }}>
                    {physics.deformable ? '是 ⚠️' : '否 ✅'}
                  </span>
                  <span>置信度</span>
                  <span>{Math.round(physics.physics_confidence * 100)}%</span>
                </div>
                <div className="conf-bar">
                  <div className="conf-fill" style={{ width: `${physics.physics_confidence * 100}%` }} />
                </div>
              </div>

              <div className="section">
                <h4>🔮 推理来源</h4>
                <div className="source-list">
                  <div className="source-item">
                    <span className="source-dot blue" />
                    <span>几何特征：bbox × {selectedObject.dimensions?.width.toFixed(1)}×{selectedObject.dimensions?.depth.toFixed(1)}×{selectedObject.dimensions?.height.toFixed(1)}m</span>
                  </div>
                  <div className="source-item">
                    <span className="source-dot green" />
                    <span>材质推断：{physics.material} → 密度/摩擦/刚度</span>
                  </div>
                  <div className="source-item">
                    <span className="source-dot yellow" />
                    <span>知识库先验：VR 知识库 80 个场景统计</span>
                  </div>
                </div>
              </div>

              <div className="model-status">
                <span className="model-dot local" />
                当前：规则引擎 fallback<br/>
                <small>PyTorch 安装完成后自动切换 NN 模型</small>
              </div>
            </>
          ) : null}
        </div>
      )}

      {/* ── 世界模型 Tab ── */}
      {tab === 'world' && (
        <div className="panel-content">
          <h3>🌍 建筑物理世界模型</h3>

          <div className="section">
            <h4>🏗️ 系统架构</h4>
            <div className="arch-flow">
              <div className="arch-node">
                <div className="arch-icon">🖼️</div>
                <div className="arch-label">VR效果图</div>
              </div>
              <div className="arch-arrow">→</div>
              <div className="arch-node">
                <div className="arch-icon">📐</div>
                <div className="arch-label">CAD施工图</div>
              </div>
              <div className="arch-arrow">→</div>
              <div className="arch-node">
                <div className="arch-icon">🧠</div>
                <div className="arch-label">NN编码器</div>
              </div>
              <div className="arch-arrow">→</div>
              <div className="arch-node highlight">
                <div className="arch-icon">🌍</div>
                <div className="arch-label">世界模型</div>
              </div>
            </div>
          </div>

          <div className="section">
            <h4>📊 当前数据</h4>
            <div className="grid-2">
              <span>VR全景</span><span>80 个</span>
              <span>3D房间</span><span>98 个</span>
              <span>场景类型</span><span>6 种</span>
              <span>物理标签</span><span>10 种</span>
              <span>设计师</span><span>8 位</span>
              <span>NN模型</span><span>待训练</span>
            </div>
          </div>

          <div className="section">
            <h4>🎯 JEPA 世界模型</h4>
            <div className="jepa-steps">
              <div className="jepa-step">
                <div className="step-num">1</div>
                <div className="step-content">
                  <div className="step-title">Encoder 编码器</div>
                  <div className="step-desc">VR/CAD → 潜在表示 z</div>
                </div>
              </div>
              <div className="jepa-step">
                <div className="step-num">2</div>
                <div className="step-content">
                  <div className="step-title">Predictor 预测器</div>
                  <div className="step-desc">z_t + a_t → z_t+1</div>
                </div>
              </div>
              <div className="jepa-step">
                <div className="step-num">3</div>
                <div className="step-content">
                  <div className="step-title">Planner 规划器</div>
                  <div className="step-desc">MCTS / MPC 搜索最优行动</div>
                </div>
              </div>
            </div>
          </div>

          <div className="vision-box">
            <div className="vision-title">🌟 数字镜像世界</div>
            <div className="vision-text">
              VR效果图 + CAD数据 + 物理属性<br/>
              = 机器人物理世界模型<br/>
              → 让AI理解空间规则，走入人类世界
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
