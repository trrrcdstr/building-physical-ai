import { useState, useEffect } from 'react'
import { useBuildingStore } from '../store/buildingStore'
import './TopBar.css'

interface ServiceStatus {
  name: string
  status: 'online' | 'degraded' | 'error' | 'unknown'
  latency?: number
}

const SERVICE_CHECKS = [
  { id: 'nn', label: 'NN推理', base: 'https://scene-production.up.railway.app', path: '/neural/api/health' },
  { id: 'scene', label: '场景服务', base: 'https://scene-production.up.railway.app', path: '/scene/' },
  { id: 'vla', label: 'VLA指令', base: 'https://scene-production.up.railway.app', path: '/vla/api/health' },
]

export default function TopBar() {
  const [services, setServices] = useState<ServiceStatus[]>([])
  const activeScene = useBuildingStore(s => s.activeScene)
  const setActiveScene = useBuildingStore(s => s.setActiveScene)
  const [demoLoading, setDemoLoading] = useState(false)

  // 定期检查服务健康状态
  useEffect(() => {
    async function checkServices() {
      const results = await Promise.allSettled(
        SERVICE_CHECKS.map(async (svc) => {
          const t0 = Date.now()
          try {
            const r = await fetch(`${svc.base}${svc.path}`, { signal: AbortSignal.timeout(3000) })
            const ms = Date.now() - t0
            if (!r.ok) throw new Error('not ok')
            return { ...svc, status: 'online' as const, latency: ms }
          } catch {
            // 降级：能连上端口但无响应
            try {
              await fetch(`${svc.base}/`, { signal: AbortSignal.timeout(2000) })
              return { ...svc, status: 'degraded' as const }
            } catch {
              return { ...svc, status: 'error' as const }
            }
          }
        })
      )
      setServices(results.map(r => r.status === 'fulfilled' ? r.value : { id: '?', label: '?', status: 'unknown' as const }))
    }
    checkServices()
    const id = setInterval(checkServices, 8000)
    return () => clearInterval(id)
  }, [])

  function handleDemo() {
    setDemoLoading(true)
    setActiveScene('ns_basement')
    setTimeout(() => setDemoLoading(false), 1500)
  }

  // 场景切换选项
  const sceneOptions: Array<{ id: string; label: string; icon: string }> = [
    { id: 'all', label: '全部场景', icon: '🌐' },
    { id: 'estate_topology', label: '小区拓扑', icon: '🏘️' },
    { id: 'residence', label: '住宅', icon: '🏠' },
    { id: 'villa_garden', label: '别墅园林', icon: '🌳' },
    { id: 'mall', label: '商场', icon: '🛒' },
    { id: 'office', label: '办公', icon: '🏢' },
    { id: 'hotel', label: '酒店', icon: '🏨' },
    { id: 'relation', label: '关系图', icon: '🕸️' },
    { id: 'sample', label: '示例', icon: '📦' },
    { id: 'renderings', label: '效果图', icon: '🎨' },
  ]

  const overallStatus = services.some(s => s.status === 'error')
    ? 'error' : services.some(s => s.status === 'degraded')
    ? 'degraded' : services.every(s => s.status === 'online')
    ? 'online' : 'degraded'

  return (
    <div className="top-bar">
      {/* 品牌标识 */}
      <div className="top-bar-brand">
        <div className="top-bar-brand-icon">🏗️</div>
        Physical AI 空间智能世界模型
        <span className="top-bar-subtitle">v2.0</span>
      </div>

      <div className="top-bar-spacer" />

      {/* ── 场景切换器（新增）─────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginRight: 12 }}>
        {sceneOptions.map(opt => (
          <button
            key={opt.id}
            onClick={() => setActiveScene(opt.id as any)}
            title={`切换到 ${opt.label}`}
            style={{
              padding: '3px 8px',
              fontSize: 11,
              borderRadius: 4,
              border: activeScene === opt.id ? '1px solid var(--accent-blue)' : '1px solid transparent',
              background: activeScene === opt.id ? 'rgba(74,144,217,0.15)' : 'transparent',
              color: activeScene === opt.id ? 'var(--accent-blue)' : '#888',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s',
              opacity: activeScene === opt.id ? 1 : 0.65,
            }}
            onMouseEnter={(e) => { if (activeScene !== opt.id) (e.target as HTMLElement).style.opacity = '1' }}
            onMouseLeave={(e) => { if (activeScene !== opt.id) (e.target as HTMLElement).style.opacity = '0.65' }}
          >
            {opt.icon} {opt.label}
          </button>
        ))}
      </div>

      {/* 服务状态指示灯 */}
      <div className="status-lights">
        {services.map(s => (
          <div key={s.id} className="status-light" title={`${s.label} · ${s.status}${s.latency ? ` · ${s.latency}ms` : ''}`}>
            <span className={`status-dot ${s.status}`} />
            <span>{s.label}</span>
          </div>
        ))}

        {/* 整体状态 */}
        <div className="status-light" style={{ borderLeft: '1px solid var(--border)', paddingLeft: 14 }}>
          <span className={`status-dot ${overallStatus}`} />
          <span style={{ fontSize: 10, color: overallStatus === 'online' ? 'var(--accent-green)' : overallStatus === 'degraded' ? 'var(--accent-yellow)' : 'var(--accent-red)' }}>
            {overallStatus === 'online' ? '系统正常' : overallStatus === 'degraded' ? '部分降级' : '服务异常'}
          </span>
        </div>
      </div>

      {/* 快速演示按钮 */}
      <button
        className="top-action-btn"
        onClick={handleDemo}
        disabled={demoLoading}
        title="加载预设Demo场景"
      >
        {demoLoading ? '⏳ 加载中…' : '🎬 快速演示'}
      </button>
    </div>
  )
}
