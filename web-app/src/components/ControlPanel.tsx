import { useBuildingStore } from '../store/buildingStore'
import { SCENE_CONFIGS, CATEGORY_SCENES, worldModelStats } from '../data/sceneConfig'
import { useMemo } from 'react'
import './ControlPanel.css'

const CATEGORY_LABELS: Record<string, { label: string; icon: string; color: string }> = {
  all:       { label: '全部场景', icon: '🌐', color: '#6366f1' },
  interior:  { label: '室内空间', icon: '🏠', color: '#f59e0b' },
  landscape: { label: '园林景观', icon: '🌳', color: '#10b981' },
  architecture: { label: '建筑空间', icon: '🏗️', color: '#3b82f6' },
}

const CATEGORY_SCENE_LIST = {
  all: [],
  interior: CATEGORY_SCENES.interior,
  landscape: CATEGORY_SCENES.landscape,
  architecture: CATEGORY_SCENES.architecture,
}

const CAD_STATS = {
  project: '示范项目',
  location: '某城市',
  totalFiles: 17,
  sizeMB: 73,
  disciplines: ['建筑', '电气', '给排水', '暖通'],
  floor: '地下室',
  note: 'DWG文件待解析（R2004二进制格式）',
  parsed: 0,
}

export default function ControlPanel() {
  const activeCategory = useBuildingStore((s) => s.activeCategory)
  const activeScene = useBuildingStore((s) => s.activeScene)
  const setActiveCategory = useBuildingStore((s) => s.setActiveCategory)
  const setActiveScene = useBuildingStore((s) => s.setActiveScene)
  const viewMode = useBuildingStore((s) => s.viewMode)
  const setViewMode = useBuildingStore((s) => s.setViewMode)
  const showPhysics = useBuildingStore((s) => s.showPhysics)
  const togglePhysics = useBuildingStore((s) => s.togglePhysics)
  const showPaths = useBuildingStore((s) => s.showPaths)
  const togglePaths = useBuildingStore((s) => s.togglePaths)
  const objects = useBuildingStore((s) => s.objects)

  // 过滤后的场景列表
  const sceneList = useMemo(
    () => CATEGORY_SCENE_LIST[activeCategory] || [],
    [activeCategory]
  )

  // 当前场景下的房间数
  const sceneRoomCount = useMemo(() => {
    if (activeScene === 'all' || activeScene === 'ns_basement') return null
    return objects.filter(o => (o as any).sceneType === activeScene).length || null
  }, [objects, activeScene])

  return (
    <div className="control-panel">
      {/* 标题 */}
      <div className="panel-header">
        <div className="panel-title">🏗️ 建筑物理AI世界模型</div>
        <div className="panel-subtitle">Physical AI World Model</div>
      </div>

      {/* 一级分类：室内 / 园林 / 建筑 */}
      <div className="control-section">
        <div className="section-label">📂 场景分类</div>
        <div className="category-tabs">
          {Object.entries(CATEGORY_LABELS).map(([key, val]) => (
            <button
              key={key}
              className={'cat-tab ' + (activeCategory === key ? 'active' : '')}
              style={{ '--cat-color': val.color } as React.CSSProperties}
              onClick={() => { setActiveCategory(key as typeof activeCategory); setActiveScene('all') }}
            >
              <span className="cat-icon">{val.icon}</span>
              <span className="cat-label">{val.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 二级场景选择 */}
      <div className="control-section">
        <div className="section-label">🗺️ 选择场景</div>
        <div className="scene-grid">
          {sceneList.map((sceneId) => {
            const cfg = SCENE_CONFIGS[sceneId]
            if (!cfg) return null
            return (
              <button
                key={sceneId}
                className={'scene-card ' + (activeScene === sceneId ? 'active' : '')}
                style={{ '--scene-color': cfg.color } as React.CSSProperties}
                onClick={() => setActiveScene(sceneId as typeof activeScene)}
              >
                <span className="scene-icon">{cfg.icon}</span>
                <span className="scene-name">{cfg.label}</span>
              </button>
            )
          })}
          {/* 示范地下车库（特殊） */}
          <button
            className={'scene-card cad-card ' + (activeScene === 'ns_basement' ? 'active' : '')}
            onClick={() => setActiveScene('ns_basement')}
          >
            <span className="scene-icon">🚗</span>
            <span className="scene-name">示范地下车库</span>
          </button>
          {/* 空间关系图谱（新） */}
          <button
            className={'scene-card ' + (activeScene === 'relation' ? 'active' : '')}
            style={{ '--scene-color': '#8b5cf6' } as React.CSSProperties}
            onClick={() => setActiveScene('relation' as any)}
          >
            <span className="scene-icon">🔗</span>
            <span className="scene-name">空间关系图谱</span>
          </button>
          {/* VR全景场景（新） */}
          <button
            className={'scene-card ' + (activeScene === 'vr_scene' ? 'active' : '')}
            style={{ '--scene-color': '#10b981' } as React.CSSProperties}
            onClick={() => setActiveScene('vr_scene' as any)}
          >
            <span className="scene-icon">🎮</span>
            <span className="scene-name">VR全景场景</span>
          </button>
        </div>
      </div>

      {/* 当前数据统计 */}
      <div className="control-section">
        <div className="section-label">📊 数据统计</div>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-num">{objects.length || worldModelStats.totalRooms}</div>
            <div className="stat-label">当前场景房间</div>
          </div>
          <div className="stat-card">
            <div className="stat-num">{worldModelStats.totalVR}</div>
            <div className="stat-label">VR全景</div>
          </div>
          <div className="stat-card">
            <div className="stat-num">3</div>
            <div className="stat-label">平台</div>
          </div>
          <div className="stat-card">
            <div className="stat-num">8</div>
            <div className="stat-label">设计师</div>
          </div>
        </div>

        {/* 平台分布 */}
        <div className="mini-bar">
          <span className="bar-label">平台分布</span>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: '80%', background: '#3b82f6' }} title="3d66: 64" />
            <div className="bar-fill" style={{ width: '18%', background: '#10b981' }} title="Justeasy: 15" />
            <div className="bar-fill" style={{ width: '2%', background: '#f59e0b' }} title="720yun: 1" />
          </div>
          <div className="bar-legend">3d66(64) · Justeasy(15) · 720yun(1)</div>
        </div>
      </div>

      {/* CAD数据库（底层支撑） */}
      <div className="control-section cad-section">
        <div className="section-label">🗄️ CAD数据库 <span className="badge">底层支撑</span></div>
        <div className="cad-info">
          <div className="cad-project">📁 {CAD_STATS.project}</div>
          <div className="cad-meta">
            <span>📍 {CAD_STATS.location}</span>
            <span>📐 {CAD_STATS.totalFiles}个DWG · {CAD_STATS.sizeMB}MB</span>
          </div>
          <div className="cad-disciplines">
            {CAD_STATS.disciplines.map(d => (
              <span key={d} className="discipline-tag">{d}</span>
            ))}
          </div>
          <div className="cad-status">
            <span className="status-dot pending" /> 待解析（需导出DXF）
          </div>
          <div className="cad-note">{CAD_STATS.note}</div>
        </div>
      </div>

      {/* 视图控制 */}
      <div className="control-section">
        <div className="section-label">👁️ 视图模式</div>
        <div className="button-group">
          <button className={viewMode === '3d' ? 'active' : ''} onClick={() => setViewMode('3d')}>3D</button>
          <button className={viewMode === 'floorplan' ? 'active' : ''} onClick={() => setViewMode('floorplan')}>平面图</button>
          <button className={viewMode === 'physics' ? 'active' : ''} onClick={() => setViewMode('physics')}>物理视图</button>
        </div>
        <div className="button-group mt-8">
          <label className="checkbox-item">
            <input type="checkbox" checked={showPhysics} onChange={togglePhysics} />
            <span>⚛️ 物理属性</span>
          </label>
          <label className="checkbox-item">
            <input type="checkbox" checked={showPaths} onChange={togglePaths} />
            <span>🛤️ 路径规划</span>
          </label>
        </div>
      </div>

      {/* 物理标签说明 */}
      <div className="control-section">
        <div className="section-label">🏷️ 物理标签</div>
        <div className="tag-cloud">
          {worldModelStats.physicsTags.map(tag => (
            <span key={tag} className="physics-tag">{tag}</span>
          ))}
        </div>
      </div>

      {/* 底部愿景 */}
      <div className="vision-note">
        <div className="vision-title">🌟 数字镜像世界</div>
        <div className="vision-text">
          VR效果图 + CAD建筑数据 + 物理属性 = 机器人物理世界模型<br/>
          让AI理解空间规则，走进人类世界
        </div>
      </div>
    </div>
  )
}
