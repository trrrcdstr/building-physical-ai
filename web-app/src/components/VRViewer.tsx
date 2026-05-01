import { useState, useMemo, useEffect } from 'react'
import './VRViewer.css'

interface VRItem {
  index: number
  url: string
  platform: string
  title: string | null
  designer: string
  rooms: string[]
  views: number
}

// 构建 VR 跳转链接
function buildVRUrl(vr: VRItem): string {
  return vr.url
}

// 平台图标
function platformIcon(platform: string): string {
  if (platform === '3d66') return '🏠'
  if (platform === 'Justeasy') return '🎨'
  if (platform === '酷家乐') return '🛋️'
  if (platform === '720yun') return '🌐'
  if (platform === '小红屋') return '🏡'
  if (platform === '至偶全景') return '📷'
  return '🔗'
}

export default function VRViewer() {
  const [vrItems, setVrItems] = useState<VRItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')
  const [search, setSearch] = useState<string>('')
  const [page, setPage] = useState(0)
  const PAGE_SIZE = 20

  // 加载 VR 数据
  const [refreshKey, setRefreshKey] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setRefreshKey(p => p + 1), 30000)
    return () => clearInterval(id)
  }, [])
  useEffect(() => {
    fetch('/data/vr_data.json')
      .then(r => r.json())
      .then((data: VRItem[]) => {
        setVrItems(data)
        setLoading(false)
      })
      .catch(e => {
        setError('加载 VR 数据失败: ' + e.message)
        setLoading(false)
      })
  }, [refreshKey])

  // 平台统计
  const platformStats = useMemo(() => {
    const stats: Record<string, number> = {}
    vrItems.forEach(v => {
      const p = v.platform || '其他'
      stats[p] = (stats[p] || 0) + 1
    })
    return stats
  }, [vrItems])

  // 过滤 + 搜索
  const filteredVR = useMemo(() => {
    let items = vrItems
    if (filter !== 'all') {
      items = items.filter(v => v.platform === filter)
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase()
      items = items.filter(v =>
        (v.title || '').toLowerCase().includes(q) ||
        (v.designer || '').toLowerCase().includes(q) ||
        (v.rooms || []).some(r => r.toLowerCase().includes(q))
      )
    }
    return items
  }, [vrItems, filter, search])

  // 分页
  const totalPages = Math.ceil(filteredVR.length / PAGE_SIZE)
  const pagedVR = filteredVR.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  // 重置分页
  const handleFilter = (f: string) => { setFilter(f); setPage(0) }
  const handleSearch = (s: string) => { setSearch(s); setPage(0) }

  // 不再检查 activeScene，始终显示（用户可以从场景选择进入）
  // if (activeScene !== 'vr_scene') return null

  if (loading) return (
    <div className="vr-viewer">
      <div className="vr-header"><h3>🎮 VR全景场景</h3></div>
      <div className="vr-empty">⏳ 加载中...</div>
    </div>
  )

  if (error) return (
    <div className="vr-viewer">
      <div className="vr-header"><h3>🎮 VR全景场景</h3></div>
      <div className="vr-empty">❌ {error}</div>
    </div>
  )

  return (
    <div className="vr-viewer">
      <div className="vr-header">
        <h3>🎮 VR全景场景</h3>
        <span className="vr-count">{filteredVR.length} / {vrItems.length} 个</span>
      </div>

      {/* 搜索 */}
      <input
        className="vr-search"
        type="text"
        placeholder="搜索房间/设计师..."
        value={search}
        onChange={e => handleSearch(e.target.value)}
      />

      {/* 平台过滤 */}
      <div className="vr-filter">
        <button
          className={filter === 'all' ? 'active' : ''}
          onClick={() => handleFilter('all')}
        >
          全部 ({vrItems.length})
        </button>
        {Object.entries(platformStats).sort((a, b) => b[1] - a[1]).map(([p, c]) => (
          <button
            key={p}
            className={filter === p ? 'active' : ''}
            onClick={() => handleFilter(p)}
          >
            {platformIcon(p)} {p} ({c})
          </button>
        ))}
      </div>

      {/* VR 列表 */}
      <div className="vr-list">
        {pagedVR.length === 0 ? (
          <div className="vr-empty">暂无匹配的 VR 数据</div>
        ) : (
          pagedVR.map(vr => (
            <div
              key={vr.index}
              className="vr-item"
              onClick={() => window.open(buildVRUrl(vr), '_blank')}
              title={vr.url}
            >
              <div className="vr-icon">{platformIcon(vr.platform)}</div>
              <div className="vr-info">
                <div className="vr-title">
                  {vr.title || (vr.rooms.length > 0 ? vr.rooms.slice(0, 2).join(' · ') : `VR #${vr.index}`)}
                </div>
                <div className="vr-meta">
                  <span className="vr-platform">{vr.platform}</span>
                  {vr.views > 0 && <span className="vr-views">👁 {vr.views}</span>}
                </div>
                {vr.designer && (
                  <div className="vr-designer">🎨 {vr.designer}</div>
                )}
                {vr.rooms.length > 0 && (
                  <div className="vr-rooms">
                    {vr.rooms.slice(0, 4).map(r => (
                      <span key={r} className="vr-room-tag">{r}</span>
                    ))}
                    {vr.rooms.length > 4 && <span className="vr-room-tag">+{vr.rooms.length - 4}</span>}
                  </div>
                )}
              </div>
              <div className="vr-open-btn">↗</div>
            </div>
          ))
        )}
      </div>

      {/* 分页 */}
      {totalPages > 1 && (
        <div className="vr-pagination">
          <button disabled={page === 0} onClick={() => setPage(p => p - 1)}>‹</button>
          <span>{page + 1} / {totalPages}</span>
          <button disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>›</button>
        </div>
      )}
    </div>
  )
}
