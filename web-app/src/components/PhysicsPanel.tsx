import { useState, useEffect, useRef } from 'react'
import { useBuildingStore, SelectedGaussian } from '../store/buildingStore'
import { MATERIAL_PHYSICS, OBJECT_PHYSICS_MAP, inferMaterialFromObject } from '../shared/physicsData'
import './PhysicsPanel.css'

// ─── API 返回的物理属性类型 ───────────────────────────────────────
interface PhysicsQueryResult {
  object_type: string
  material: string
  friction_dry: number
  friction_wet: number
  density: number
  surface_density: number
  drill_safety: string
  drill_safety_level: number
  max_drill_depth_mm: number
  max_force_n: number
  safe_tools: string[]
  warnings: string[]
  position: number[]
  scene: string
}

// ─── 皮·骨·肉 三栏布局主面板 ───────────────────────────────────────
export default function PhysicsPanel() {
  const selectedObject = useBuildingStore(s => s.selectedObject)
  const selectedWall = useBuildingStore(s => s.selectedWall)
  const selectedGaussian = useBuildingStore(s => s.selectedGaussian)
  const activeScene = useBuildingStore(s => s.activeScene)
  const objects = useBuildingStore(s => s.objects)

  // 淡入动画状态
  const [fadeIn, setFadeIn] = useState(false)
  const prevSelectedRef = useRef<string | null>(null)

  useEffect(() => {
    const newId = selectedObject?.id ?? selectedWall?.roomId ?? selectedGaussian?.id ?? null
    if (newId !== prevSelectedRef.current) {
      setFadeIn(false)
      const t = setTimeout(() => setFadeIn(true), 20)
      prevSelectedRef.current = newId
      return () => clearTimeout(t)
    }
  }, [selectedObject?.id, selectedWall?.roomId, selectedGaussian?.id])

  const hasSelection = selectedObject !== null || selectedWall !== null || selectedGaussian !== null

  // 场景名称映射
  const sceneName = (() => {
    const s = activeScene
    if (s === 'residence' || s === 'residential') return '住宅别墅'
    if (s === 'mall' || s === 'commercial_complex') return '商业综合体'
    if (s === 'office' || s === 'office_building') return '办公建筑'
    if (s === 'hotel') return '酒店'
    if (s === 'villa_garden') return '别墅园林'
    if (s === 'park') return '公共公园'
    if (s === 'ns_basement') return '地下室/车位'
    if (s === 'vr_scene' || s === 'renderings') return 'VR场景'
    return String(s).replace(/_/g, ' ')
  })()

  // 选中对象名称
  const objectLabel = (() => {
    if (selectedGaussian) {
      const typeNames: Record<string, string> = {
        'floor_tile': '瓷砖地板',
        'wall_brick': '砖墙',
        'glass_window': '玻璃窗',
      }
      return typeNames[selectedGaussian.type] || selectedGaussian.type
    }
    if (selectedWall) {
      const wallNames: Record<string, string> = { north: '北墙', south: '南墙', east: '东墙', west: '西墙' }
      const wName = wallNames[selectedWall.wall] ?? selectedWall.wall
      return `${wName}${selectedWall.isLoadBearing ? '(承重)' : '(非承重)'}`
    }
    if (selectedObject) return selectedObject.name
    return '未选中'
  })()

  return (
    <div className="panel physics-panel">
      {/* 头部 */}
      <div className="panel-header">
        <span className="panel-title">🌍 物理世界面板</span>
        <span className="panel-tag cyan">肉层</span>
      </div>

      {/* 场景状态栏 */}
      <div className="physics-scene-bar">
        <span>🏠 {sceneName}</span>
        <span className="physics-scene-sep">|</span>
        <span className={hasSelection ? 'physics-obj-active' : 'physics-obj-empty'}>
          📌 {objectLabel}
        </span>
      </div>

      {/* 三栏主体 */}
      <div className={`physics-three-cols ${fadeIn ? 'fade-in' : ''}`}>
        {/* 🎨 皮栏 — 外观 */}
        <SkinColumn selectedObject={selectedObject} selectedGaussian={selectedGaussian} objects={objects} />

        {/* 🦴 骨栏 — 结构 */}
        <BoneColumn selectedObject={selectedObject} selectedWall={selectedWall} selectedGaussian={selectedGaussian} />

        {/* 🥩 肉栏 — 物理参数 */}
        <MeatColumn selectedObject={selectedObject} selectedWall={selectedWall} selectedGaussian={selectedGaussian} />
      </div>
    </div>
  )
}

// ─── 🎨 皮栏 ───────────────────────────────────────────
function SkinColumn({ selectedObject, selectedGaussian, objects }: {
  selectedObject: ReturnType<typeof useBuildingStore.getState>['selectedObject']
  selectedGaussian: SelectedGaussian | null
  objects: ReturnType<typeof useBuildingStore.getState>['objects']
}) {
  // Gaussian 点选中时显示颜色信息
  if (selectedGaussian) {
    const [r, g, b] = selectedGaussian.color
    const colorHex = `#${((r*255)|0).toString(16).padStart(2,'0')}${((g*255)|0).toString(16).padStart(2,'0')}${((b*255)|0).toString(16).padStart(2,'0')}`
    
    const typeNames: Record<string, string> = {
      'floor_tile': '瓷砖地板',
      'wall_brick': '砖墙',
      'glass_window': '玻璃窗',
    }
    
    return (
      <div className="physics-col skin-col">
        <div className="physics-col-header">
          <span>🎨</span>
          <span className="physics-col-title">皮</span>
        </div>

        {/* 颜色预览 */}
        <div className="skin-thumbnail">
          <div className="skin-thumb-placeholder" style={{ background: colorHex }}>
            <span style={{ fontSize: 12, color: (r + g + b) / 3 > 0.5 ? '#000' : '#fff' }}>
              G
            </span>
          </div>
          <div className="skin-thumb-title" style={{ fontSize: 9 }}>
            Gaussian Point
          </div>
        </div>

        {/* 属性 */}
        <div className="skin-meta">
          <div className="skin-meta-row">
            <span className="skin-meta-label">类型</span>
            <span className="skin-meta-value">{typeNames[selectedGaussian.type] || selectedGaussian.type}</span>
          </div>
          <div className="skin-meta-row">
            <span className="skin-meta-label">颜色</span>
            <span className="skin-meta-value">{colorHex}</span>
          </div>
          <div className="skin-meta-row">
            <span className="skin-meta-label">ID</span>
            <span className="skin-meta-value">{selectedGaussian.id}</span>
          </div>
        </div>
      </div>
    )
  }

  const rooms = objects.filter(o => !o.id.startsWith('parking-') && !o.id.startsWith('basement-'))
  const vrCount = new Set(rooms.map(r => r.vrData?.vr_id).filter(Boolean)).size
  const totalCount = rooms.length
  const platformCount = new Set(rooms.map(r => r.vrData?.platform).filter(Boolean)).size

  if (selectedObject?.vrData) {
    const vr = selectedObject.vrData
    return (
      <div className="physics-col skin-col">
        <div className="physics-col-header">
          <span>🎨</span>
          <span className="physics-col-title">皮</span>
        </div>

        {/* 效果图缩略图占位 */}
        <div className="skin-thumbnail">
          <div className="skin-thumb-placeholder">
            <span style={{ fontSize: 24 }}>🏠</span>
            <span style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
              {vr.platform.toUpperCase()}
            </span>
          </div>
          {vr.title && (
            <div className="skin-thumb-title">{vr.title}</div>
          )}
        </div>

        {/* 数据来源 */}
        <div className="skin-meta">
          <div className="skin-meta-row">
            <span className="skin-meta-label">场景</span>
            <span className="skin-meta-value">{vr.room_category}</span>
          </div>
          <div className="skin-meta-row">
            <span className="skin-meta-label">来源</span>
            <span className="skin-meta-value">{vr.platform} · {vr.designer}</span>
          </div>
          <div className="skin-meta-row">
            <span className="skin-meta-label">ID</span>
            <span className="skin-meta-value">VR{vr.vr_id}</span>
          </div>
          {vr.physics_tags && vr.physics_tags.length > 0 && (
            <div className="skin-tags">
              {vr.physics_tags.map(tag => (
                <span key={tag} className="physics-tag">{tag}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  // 无选中 → 场景统计
  return (
    <div className="physics-col skin-col">
      <div className="physics-col-header">
        <span>🎨</span>
        <span className="physics-col-title">皮</span>
      </div>
      <div className="skin-scene-stats">
        <div className="skin-stat-item">
          <div className="skin-stat-value">{totalCount}</div>
          <div className="skin-stat-label">房间数量</div>
        </div>
        <div className="skin-stat-item">
          <div className="skin-stat-value">{vrCount}</div>
          <div className="skin-stat-label">效果图</div>
        </div>
        <div className="skin-stat-item">
          <div className="skin-stat-value">{platformCount}</div>
          <div className="skin-stat-label">平台来源</div>
        </div>
      </div>
      <div className="skin-hint">
        <span>👆 点击场景中的房间</span>
        <span>查看效果图详情</span>
      </div>
    </div>
  )
}

// ─── 🦴 骨栏 ───────────────────────────────────────────
function BoneColumn({ selectedObject, selectedWall, selectedGaussian }: {
  selectedObject: ReturnType<typeof useBuildingStore.getState>['selectedObject']
  selectedWall: ReturnType<typeof useBuildingStore.getState>['selectedWall']
  selectedGaussian: SelectedGaussian | null
}) {
  const wallNames: Record<string, string> = { north: '北墙', south: '南墙', east: '东墙', west: '西墙' }

  // Gaussian 点选中时显示位置信息
  if (selectedGaussian) {
    const [x, y, z] = selectedGaussian.position
    return (
      <div className="physics-col bone-col">
        <div className="physics-col-header">
          <span>🦴</span>
          <span className="physics-col-title">骨</span>
        </div>
        <div className="bone-struct-info">
          <div className="bone-wall-badge non-bearing">
            🎯 高斯点
          </div>
          <div className="bone-row">
            <span className="bone-label">类型</span>
            <span className="bone-value">Gaussian Splat</span>
          </div>
          <div className="bone-row">
            <span className="bone-label">位置 X</span>
            <span className="bone-value">{x.toFixed(2)}</span>
          </div>
          <div className="bone-row">
            <span className="bone-label">位置 Y</span>
            <span className="bone-value">{y.toFixed(2)}</span>
          </div>
          <div className="bone-row">
            <span className="bone-label">位置 Z</span>
            <span className="bone-value">{z.toFixed(2)}</span>
          </div>
        </div>
      </div>
    )
  }

  // CAD 数据
  if (selectedObject?.cadData) {
    const cad = selectedObject.cadData
    return (
      <div className="physics-col bone-col">
        <div className="physics-col-header">
          <span>🦴</span>
          <span className="physics-col-title">骨</span>
        </div>
        <div className="bone-struct-info">
          <div className="bone-row">
            <span className="bone-label">项目</span>
            <span className="bone-value">{cad.project}</span>
          </div>
          {cad.floor && (
            <div className="bone-row">
              <span className="bone-label">楼层</span>
              <span className="bone-value">{cad.floor}</span>
            </div>
          )}
          {cad.discipline && (
            <div className="bone-row">
              <span className="bone-label">专业</span>
              <span className="bone-value">{cad.discipline}</span>
            </div>
          )}
          {cad.layer && (
            <div className="bone-row">
              <span className="bone-label">图层</span>
              <span className="bone-value">{cad.layer}</span>
            </div>
          )}
        </div>
      </div>
    )
  }

  // 墙体数据
  if (selectedWall) {
    const { wall: wDir, isLoadBearing } = selectedWall
    const wName = wallNames[wDir] ?? wDir

    // 模拟墙体属性（真实场景中可从 CAD 数据获取）
    const wallProps = {
      north: { type: '承重墙', material: 'C30混凝土', thickness: 200, pipe: '电气/照明' },
      south: { type: '非承重', material: '轻钢龙骨石膏板', thickness: 100, pipe: '无' },
      east: { type: '承重墙', material: 'C30混凝土', thickness: 200, pipe: '给排水' },
      west: { type: '非承重', material: '加气混凝土砌块', thickness: 150, pipe: '电气' },
    }
    const props = wallProps[wDir as keyof typeof wallProps] ?? { type: '未知', material: '—', thickness: 0, pipe: '—' }

    return (
      <div className="physics-col bone-col">
        <div className="physics-col-header">
          <span>🦴</span>
          <span className="physics-col-title">骨</span>
        </div>
        <div className="bone-struct-info">
          <div className={`bone-wall-badge ${isLoadBearing ? 'bearing' : 'non-bearing'}`}>
            {isLoadBearing ? '🛑 承重结构' : '✅ 非承重'}
          </div>
          <div className="bone-row">
            <span className="bone-label">墙体</span>
            <span className="bone-value">{wName}</span>
          </div>
          <div className="bone-row">
            <span className="bone-label">类型</span>
            <span className="bone-value">{props.type}</span>
          </div>
          <div className="bone-row">
            <span className="bone-label">材质</span>
            <span className="bone-value">{props.material}</span>
          </div>
          <div className="bone-row">
            <span className="bone-label">厚度</span>
            <span className="bone-value">{props.thickness}mm</span>
          </div>
          <div className="bone-row">
            <span className="bone-label">管线</span>
            <span className="bone-value" style={{ color: props.pipe === '无' ? 'var(--accent-green)' : 'var(--accent-yellow)' }}>
              {props.pipe}
            </span>
          </div>
        </div>
      </div>
    )
  }

  // 选中物体（无 CAD）
  if (selectedObject) {
    const dims = selectedObject.dimensions
    return (
      <div className="physics-col bone-col">
        <div className="physics-col-header">
          <span>🦴</span>
          <span className="physics-col-title">骨</span>
        </div>
        <div className="bone-struct-info">
          <div className="bone-row">
            <span className="bone-label">类型</span>
            <span className="bone-value">{selectedObject.type}</span>
          </div>
          <div className="bone-row">
            <span className="bone-label">尺寸</span>
            <span className="bone-value">
              {dims.width.toFixed(1)}×{dims.depth.toFixed(1)}m
            </span>
          </div>
          {dims.height && (
            <div className="bone-row">
              <span className="bone-label">高度</span>
              <span className="bone-value">{dims.height.toFixed(1)}m</span>
            </div>
          )}
          <div className="bone-row">
            <span className="bone-label">位置</span>
            <span className="bone-value">
              [{selectedObject.position.map(v => v.toFixed(1)).join(', ')}]
            </span>
          </div>
        </div>
        <div className="bone-no-cad">
          <span>⚠️ 该区域暂无 CAD 结构数据</span>
        </div>
      </div>
    )
  }

  // 无选中
  return (
    <div className="physics-col bone-col">
      <div className="physics-col-header">
        <span>🦴</span>
        <span className="physics-col-title">骨</span>
      </div>
      <div className="bone-empty">
        <span>🏗️ 点击墙体查看结构数据</span>
      </div>
    </div>
  )
}

// ─── 🥩 肉栏 ───────────────────────────────────────────
function MeatColumn({ selectedObject, selectedWall, selectedGaussian }: {
  selectedObject: ReturnType<typeof useBuildingStore.getState>['selectedObject']
  selectedWall: ReturnType<typeof useBuildingStore.getState>['selectedWall']
  selectedGaussian: SelectedGaussian | null
}) {
  const [physicsResult, setPhysicsResult] = useState<PhysicsQueryResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 当选中 Gaussian 点时，调用 API 查询物理属性
  useEffect(() => {
    if (!selectedGaussian) {
      setPhysicsResult(null)
      setError(null)
      return
    }

    const fetchPhysics = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch('/api/physics/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            position: selectedGaussian.position,
            object_type: selectedGaussian.type,
            scene: '室内_家庭'
          })
        })

        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`)
        }

        const data = await response.json()
        setPhysicsResult(data)
      } catch (err) {
        console.error('Physics query failed:', err)
        setError(err instanceof Error ? err.message : '查询失败')
        
        // Fallback 数据
        const fallbackData: Record<string, PhysicsQueryResult> = {
          'floor_tile': {
            object_type: 'floor_tile',
            material: '瓷砖',
            friction_dry: 0.50,
            friction_wet: 0.35,
            density: 2400,
            surface_density: 24.0,
            drill_safety: '中风险',
            drill_safety_level: 2,
            max_drill_depth_mm: 30,
            max_force_n: 100,
            safe_tools: ['电锤', '冲击钻'],
            warnings: ['避免破坏防水层'],
            position: selectedGaussian.position,
            scene: '室内_家庭'
          },
          'wall_brick': {
            object_type: 'wall_brick',
            material: '普通砖墙',
            friction_dry: 0.50,
            friction_wet: 0.50,
            density: 1800,
            surface_density: 18.0,
            drill_safety: '中风险',
            drill_safety_level: 2,
            max_drill_depth_mm: 50,
            max_force_n: 80,
            safe_tools: ['电锤', '冲击钻'],
            warnings: ['检查是否有管线'],
            position: selectedGaussian.position,
            scene: '室内_家庭'
          },
          'glass_window': {
            object_type: 'glass_window',
            material: '钢化玻璃',
            friction_dry: 0.35,
            friction_wet: 0.30,
            density: 2500,
            surface_density: 25.0,
            drill_safety: '高风险',
            drill_safety_level: 3,
            max_drill_depth_mm: 0,
            max_force_n: 0,
            safe_tools: ['玻璃吸盘', '软尺'],
            warnings: ['边缘脆弱，避免撞击'],
            position: selectedGaussian.position,
            scene: '室内_家庭'
          }
        }
        
        setPhysicsResult(fallbackData[selectedGaussian.type] || fallbackData['wall_brick'])
      } finally {
        setLoading(false)
      }
    }

    fetchPhysics()
  }, [selectedGaussian])

  // Gaussian 点选中时显示 API 查询结果
  if (selectedGaussian) {
    if (loading) {
      return (
        <div className="physics-col meat-col">
          <div className="physics-col-header">
            <span>🥩</span>
            <span className="physics-col-title">肉</span>
          </div>
          <div className="meat-empty">
            <span>⏳ 查询物理属性中...</span>
          </div>
        </div>
      )
    }

    if (error && !physicsResult) {
      return (
        <div className="physics-col meat-col">
          <div className="physics-col-header">
            <span>🥩</span>
            <span className="physics-col-title">肉</span>
          </div>
          <div className="meat-empty">
            <span>❌ {error}</span>
          </div>
        </div>
      )
    }

    if (physicsResult) {
      return (
        <div className="physics-col meat-col">
          <div className="physics-col-header">
            <span>🥩</span>
            <span className="physics-col-title">肉</span>
          </div>

          {/* 物理参数 */}
          <div className="meat-section">
            <div className="meat-section-title">物理参数</div>
            <div className="meat-params">
              <div className="meat-param">
                <span className="meat-param-label">材质</span>
                <span className="meat-param-value">{physicsResult.material}</span>
              </div>
              <div className="meat-param">
                <span className="meat-param-label">摩擦系数(干)</span>
                <span className="meat-param-value">{physicsResult.friction_dry.toFixed(2)}</span>
              </div>
              <div className="meat-param">
                <span className="meat-param-label">摩擦系数(湿)</span>
                <span className="meat-param-value danger">{physicsResult.friction_wet.toFixed(2)}</span>
              </div>
              <div className="meat-param">
                <span className="meat-param-label">密度</span>
                <span className="meat-param-value">{physicsResult.density}</span>
                <span className="meat-param-unit">kg/m³</span>
              </div>
              <div className="meat-param">
                <span className="meat-param-label">面密度</span>
                <span className="meat-param-value">{physicsResult.surface_density.toFixed(1)}</span>
                <span className="meat-param-unit">kg/m²</span>
              </div>
            </div>
          </div>

          {/* 钻孔安全性 */}
          <div className="meat-section">
            <div className="meat-section-title">⚠️ 钻孔安全性</div>
            <div className="meat-drill-safety">
              <span className={`drill-safety-badge ${physicsResult.drill_safety_level === 1 ? 'low' : physicsResult.drill_safety_level === 2 ? 'medium' : 'high'}`}>
                {physicsResult.drill_safety}
              </span>
              {physicsResult.max_drill_depth_mm > 0 && (
                <div className="meat-param" style={{ marginTop: 4 }}>
                  <span className="meat-param-label">最大钻孔深度</span>
                  <span className="meat-param-value">{physicsResult.max_drill_depth_mm}</span>
                  <span className="meat-param-unit">mm</span>
                </div>
              )}
              {physicsResult.max_force_n > 0 && (
                <div className="meat-param">
                  <span className="meat-param-label">最大施力</span>
                  <span className="meat-param-value">{physicsResult.max_force_n}</span>
                  <span className="meat-param-unit">N</span>
                </div>
              )}
            </div>
          </div>

          {/* 推荐工具 */}
          {physicsResult.safe_tools.length > 0 && (
            <div className="meat-section">
              <div className="meat-section-title">🛠️ 推荐工具</div>
              <div className="meat-tools">
                {physicsResult.safe_tools.map(tool => (
                  <span key={tool} className="meat-tool safe">{tool}</span>
                ))}
              </div>
            </div>
          )}

          {/* 警告 */}
          {physicsResult.warnings.length > 0 && (
            <div className="meat-section">
              <div className="meat-section-title">⚠️ 注意事项</div>
              {physicsResult.warnings.map((w, i) => (
                <div key={i} className="meat-warn">{w}</div>
              ))}
            </div>
          )}
        </div>
      )
    }
  }

  // 确定物体类型 key
  const objectTypeKey = (() => {
    if (selectedWall) {
      return selectedWall.isLoadBearing ? 'wall_load_bearing' : 'wall_partition'
    }
    if (selectedObject) {
      return inferMaterialFromObject(selectedObject) ?? 'wall_brick'
    }
    return null
  })()

  const physicsData = objectTypeKey ? OBJECT_PHYSICS_MAP[objectTypeKey] : null

  // 材质数据（来自 MATERIAL_PHYSICS）
  const matKey = (() => {
    if (!physicsData) return null
    if (physicsData.material.includes('混凝土') || physicsData.material.includes('C30')) return '瓷砖'
    if (physicsData.material.includes('瓷砖') || physicsData.material.includes('陶瓷')) return '瓷砖'
    if (physicsData.material.includes('玻璃')) return '钢化玻璃'
    if (physicsData.material.includes('实木') || physicsData.material.includes('木地板')) return '实木地板'
    if (physicsData.material.includes('不锈钢') || physicsData.material.includes('金属')) return '不锈钢'
    return '瓷砖'
  })()

  const mat = matKey ? MATERIAL_PHYSICS[matKey] : null

  if (!physicsData) {
    return (
      <div className="physics-col meat-col">
        <div className="physics-col-header">
          <span>🥩</span>
          <span className="physics-col-title">肉</span>
        </div>
        <div className="meat-empty">
          <span>🔬 选择物体查看物理参数</span>
        </div>
      </div>
    )
  }

  const r = physicsData.robot

  return (
    <div className="physics-col meat-col">
      <div className="physics-col-header">
        <span>🥩</span>
        <span className="physics-col-title">肉</span>
      </div>

      {/* 物理参数 */}
      <div className="meat-section">
        <div className="meat-section-title">物理参数</div>
        <div className="meat-params">
          <div className="meat-param">
            <span className="meat-param-label">摩擦系数(干)</span>
            <span className="meat-param-value">{physicsData.friction}</span>
          </div>
          <div className="meat-param">
            <span className="meat-param-label">密度</span>
            <span className="meat-param-value">{physicsData.density}</span>
            <span className="meat-param-unit">kg/m³</span>
          </div>
          {physicsData.collision_threshold_j && (
            <div className="meat-param">
              <span className="meat-param-label">碰撞阈值</span>
              <span className="meat-param-value">{physicsData.collision_threshold_j}</span>
              <span className="meat-param-unit">J</span>
            </div>
          )}
          {physicsData.mass_kg && (
            <div className="meat-param">
              <span className="meat-param-label">质量</span>
              <span className="meat-param-value">{physicsData.mass_kg}</span>
              <span className="meat-param-unit">kg</span>
            </div>
          )}
        </div>
      </div>

      {/* 安全规则 */}
      {physicsData.rules.length > 0 && (
        <div className="meat-section">
          <div className="meat-section-title">⚠️ 安全规则</div>
          {physicsData.rules.map((rule, i) => (
            <div key={i} className="meat-rule">
              {rule}
            </div>
          ))}
        </div>
      )}

      {/* 机器人约束 */}
      <div className="meat-section">
        <div className="meat-section-title">🤖 机器人约束</div>
        <div className="meat-params">
          {r.max_force_n !== undefined && r.max_force_n > 0 && (
            <div className="meat-param">
              <span className="meat-param-label">最大抓握力</span>
              <span className="meat-param-value">{r.max_force_n}</span>
              <span className="meat-param-unit">N</span>
            </div>
          )}
          {r.grip_force_n && (
            <div className="meat-param">
              <span className="meat-param-label">最大握力</span>
              <span className="meat-param-value">{r.grip_force_n}</span>
              <span className="meat-param-unit">N</span>
            </div>
          )}
          {(r.approach_speed > 0 || r.speed_m_s) && (
            <div className="meat-param">
              <span className="meat-param-label">推荐速度</span>
              <span className="meat-param-value">{(r.approach_speed || r.speed_m_s!).toFixed(1)}</span>
              <span className="meat-param-unit">m/s</span>
            </div>
          )}
        </div>
      </div>

      {/* 工具建议（来自 MATERIAL_PHYSICS） */}
      {mat && (
        <div className="meat-section">
          <div className="meat-section-title">🛠️ 推荐工具</div>
          <div className="meat-tools">
            {mat.safeTools.slice(0, 3).map(tool => (
              <span key={tool} className="meat-tool safe">{tool}</span>
            ))}
          </div>
          {mat.warnings.slice(0, 1).map((w, i) => (
            <div key={i} className="meat-warn">{w}</div>
          ))}
        </div>
      )}
    </div>
  )
}
