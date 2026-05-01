import { useBuildingStore } from '../store/buildingStore'
import './SceneColumn.css'

const SCENES = [
  { id: 'sample',     name: '示例地下室',  icon: '🏗️', meta: '151节点·场景图' },
  { id: 'ns_basement',name: '空间关系图谱', icon: '🔗', meta: '1029条边关系' },
  { id: 'relation',   name: '神经网络推理', icon: '🧠',  meta: '空间+物理双推理' },
  { id: 'vr',         name: 'VR全景',       icon: '🌐',  meta: '444条全景' },
  { id: 'rendering',  name: '效果图库',     icon: '🖼️',  meta: '1053张渲染图' },
]

const QUICK_ACTIONS = [
  { icon: '🔄', label: '重置视角',   action: 'reset' },
  { icon: '🏠', label: '俯视图',     action: 'top' },
  { icon: '📐', label: '正视南墙',   action: 'front' },
  { icon: '🔍', label: '聚焦选中',   action: 'focus' },
]

export default function SceneColumn() {
  const activeScene = useBuildingStore(s => s.activeScene)
  const setActiveScene = useBuildingStore(s => s.setActiveScene)

  return (
    <div className="scene-column">
      {/* 场景切换（场景列表面板） */}
      <div className="panel scene-list-panel">
        <div className="panel-header">
          <span className="panel-title">🗺️ 场景选择</span>
          <span className="panel-tag cyan">感知层</span>
        </div>
        <div className="scene-grid">
          {SCENES.map(s => (
            <div
              key={s.id}
              className={`scene-card ${activeScene === s.id ? 'active' : ''}`}
              onClick={() => setActiveScene(s.id as any)}
            >
              <div className="scene-card-icon">{s.icon}</div>
              <div className="scene-card-name">{s.name}</div>
              <div className="scene-card-meta">{s.meta}</div>
            </div>
          ))}
        </div>

        {/* 视角快捷操作 */}
        <div className="view-actions">
          {QUICK_ACTIONS.map(a => (
            <button key={a.action} className="view-action-btn" title={a.label}>
              <span>{a.icon}</span>
              <span>{a.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 选中对象信息 */}
      <ObjectInfoPanel />
    </div>
  )
}

function ObjectInfoPanel() {
  const selectedObject = useBuildingStore(s => s.selectedObject)
  const selectedWall  = useBuildingStore(s => (s as any).selectedWall)

  if (!selectedObject && !selectedWall) {
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title">📦 选中对象</span>
        </div>
        <div className="panel-body">
          <div className="physics-empty-hint" style={{ padding: '16px 8px' }}>
            <div style={{ fontSize: 24, opacity: 0.25 }}>🎯</div>
            <div style={{ fontSize: 11 }}>点击3D场景中的物体</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
              查看物理属性与安全信息
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (selectedWall) {
    const wallName: Record<string, string> = { north: '北墙', south: '南墙', east: '东墙', west: '西墙' }
    const isBearing = selectedWall.isLoadBearing
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title">🧱 墙体信息</span>
          <span className={isBearing ? 'panel-tag red' : 'panel-tag green'}>
            {isBearing ? '承重墙' : '非承重墙'}
          </span>
        </div>
        <div className="panel-body">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div className="info-row">
              <span className="info-label">位置</span>
              <span className="info-value">{wallName[selectedWall.wall] ?? selectedWall.wall}</span>
            </div>
            <div className="info-row">
              <span className="info-label">结构</span>
              <span className="info-value" style={{ color: isBearing ? '#f87171' : '#34d399' }}>
                {isBearing ? '钢筋混凝土' : '轻质隔墙'}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">钻孔</span>
              <span className="info-value" style={{ color: isBearing ? '#f87171' : '#34d399' }}>
                {isBearing ? '🛑 禁止' : '✅ 允许'}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">管线风险</span>
              <span className="info-value" style={{ color: '#fbbf24' }}>⚠️ 需探测</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // 普通物体
  const obj = selectedObject as any
  const dims = obj?.dimensions ?? {}
  const cat = obj?.category ?? 'object'

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">📦 选中对象</span>
        <span className="panel-tag blue">{cat}</span>
      </div>
      <div className="panel-body">
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 10 }}>
          {obj?.name ?? '未知物体'}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {dims.width && (
            <div className="info-row">
              <span className="info-label">尺寸</span>
              <span className="info-value">
                {dims.width.toFixed(1)} × {dims.depth?.toFixed(1) ?? '?'} × {dims.height?.toFixed(1) ?? '?'} m
              </span>
            </div>
          )}
          {obj?.position && (
            <div className="info-row">
              <span className="info-label">坐标</span>
              <span className="info-value">
                ({ (obj.position as [number,number,number])[0].toFixed(0) },
                 { (obj.position as [number,number,number])[1].toFixed(2) },
                 { (obj.position as [number,number,number])[2].toFixed(0) })
              </span>
            </div>
          )}
          {obj?.material && (
            <div className="info-row">
              <span className="info-label">材质</span>
              <span className="info-value">{obj.material}</span>
            </div>
          )}
          {obj?.room && (
            <div className="info-row">
              <span className="info-label">所属房间</span>
              <span className="info-value">{obj.room}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
