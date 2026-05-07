import { useState } from 'react'
import { vrScenePhysicsData } from '../data/vr_scene_physics'
import './VRSceneSelector.css'

interface ScenePhysics {
  floor_material: string
  floor_friction: number
  floor_density: number
  wall_material: string
  wall_friction: number
  wall_density: number
  wall_thickness: number
  wall_load_bearing: boolean
  ceiling_material: string
  furniture: string[]
  tags: string[]
}

interface VrSceneEntry {
  id: string
  name: string
  icon: string
  defaultUrl: string
  alternatives: string[]
  physics: ScenePhysics
}

const SCENES: VrSceneEntry[] = vrScenePhysicsData.scenes

interface VRSceneSelectorProps {
  onSceneChange?: (scene: VrSceneEntry) => void
}

export default function VRSceneSelector({ onSceneChange }: VRSceneSelectorProps) {
  const [selectedScene, setSelectedScene] = useState<VrSceneEntry>(SCENES[0])
  const [altIndex, setAltIndex] = useState(0)
  const [showPhysics, setShowPhysics] = useState(true)
  const [iframeLoaded, setIframeLoaded] = useState(false)
  const [iframeError, setIframeError] = useState(false)

  const handleSceneClick = (scene: VrSceneEntry) => {
    setSelectedScene(scene)
    setAltIndex(0)
    setIframeLoaded(false)
    setIframeError(false)
    onSceneChange?.(scene)
  }

  const currentUrl = selectedScene.alternatives[altIndex] || selectedScene.defaultUrl
  
  const p = selectedScene.physics

  return (
    <div className="vr-scene-selector">
      {/* 场景选择卡片 */}
      <div className="vr-scene-cards">
        {SCENES.map((scene) => (
          <button
            key={scene.id}
            className={`vr-scene-card ${selectedScene.id === scene.id ? 'active' : ''}`}
            onClick={() => handleSceneClick(scene)}
          >
            <span className="vr-scene-icon">{scene.icon}</span>
            <span className="vr-scene-name">{scene.name}</span>
          </button>
        ))}
      </div>

      {/* VR iframe */}
      <div className="vr-iframe-wrap">
        {/* 加载提示 */}
        {!iframeLoaded && !iframeError && (
          <div className="vr-loading-overlay">
            <div className="vr-loading-content">
              <div className="vr-loading-spinner"></div>
              <p>正在加载 VR 全景...</p>
              <p className="vr-loading-hint">如果长时间无响应，请点击下方按钮在新窗口打开</p>
            </div>
          </div>
        )}
        
        <iframe
          src={currentUrl}
          className="vr-iframe"
          allow="fullscreen; accelerometer; gyroscope"
          title={selectedScene.name}
          onLoad={() => setIframeLoaded(true)}
          onError={() => setIframeError(true)}
        />
        
        {/* 外部链接按钮 */}
        <a 
          href={currentUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="vr-external-link"
        >
          🔗 新窗口打开
        </a>
        
        {/* 切换按钮 */}
        {selectedScene.alternatives.length > 1 && (
          <div className="vr-alt-nav">
            <button 
              className="vr-alt-btn"
              onClick={() => {
                setAltIndex((altIndex - 1 + selectedScene.alternatives.length) % selectedScene.alternatives.length)
                setIframeLoaded(false)
              }}
            >
              ◀
            </button>
            <span className="vr-alt-counter">{altIndex + 1}/{selectedScene.alternatives.length}</span>
            <button 
              className="vr-alt-btn"
              onClick={() => {
                setAltIndex((altIndex + 1) % selectedScene.alternatives.length)
                setIframeLoaded(false)
              }}
            >
              ▶
            </button>
          </div>
        )}
      </div>

      {/* 物理数据面板 */}
      {showPhysics && (
        <div className="vr-physics-panel">
          <div className="vr-physics-header">
            <span className="vr-physics-title">📊 物理常识</span>
            <button className="vr-physics-toggle" onClick={() => setShowPhysics(false)}>▼</button>
          </div>
          
          <div className="vr-physics-content">
            {/* 地面 */}
            <div className="vr-phys-section">
              <div className="vr-phys-section-title">🟫 地面</div>
              <div className="vr-phys-row">
                <span className="vr-phys-label">材质</span>
                <span className="vr-phys-value">{p.floor_material}</span>
              </div>
              <div className="vr-phys-row">
                <span className="vr-phys-label">摩擦</span>
                <span className="vr-phys-value">{p.floor_friction}</span>
              </div>
              <div className="vr-phys-row">
                <span className="vr-phys-label">密度</span>
                <span className="vr-phys-value">{p.floor_density} kg/m³</span>
              </div>
            </div>

            {/* 墙体 */}
            <div className="vr-phys-section">
              <div className="vr-phys-section-title">🧱 墙体</div>
              <div className={`vr-load-bearing ${p.wall_load_bearing ? 'bearing' : 'safe'}`}>
                {p.wall_load_bearing ? '⚠️ 承重墙' : '✅ 非承重墙'}
              </div>
              <div className="vr-phys-row">
                <span className="vr-phys-label">材质</span>
                <span className="vr-phys-value">{p.wall_material}</span>
              </div>
              <div className="vr-phys-row">
                <span className="vr-phys-label">摩擦</span>
                <span className="vr-phys-value">{p.wall_friction}</span>
              </div>
              <div className="vr-phys-row">
                <span className="vr-phys-label">墙厚</span>
                <span className="vr-phys-value">{p.wall_thickness}mm</span>
              </div>
            </div>

            {/* 常见物体 */}
            <div className="vr-phys-section">
              <div className="vr-phys-section-title">🛋️ 常见物体</div>
              <div className="vr-furniture-tags">
                {p.furniture.map((item) => (
                  <span key={item} className="vr-furniture-tag">{item}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {!showPhysics && (
        <button className="vr-physics-expand" onClick={() => setShowPhysics(true)}>
          📊 物理常识
        </button>
      )}
    </div>
  )
}
