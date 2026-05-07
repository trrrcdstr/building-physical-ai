import { useState, useMemo, useEffect } from 'react'
import { useBuildingStore } from '../store/buildingStore'
import './RenderingGallery.css'

// 效果图根目录（本地 Desktop）
const RENDER_ROOT = 'C:/Users/Administrator/Desktop/设计数据库/效果图'
// 图片 HTTP 代理地址（本地图片服务器）
const IMG_PROXY = 'http://localhost:8888'

interface RenderingObject {
  id: string
  name: string
  type: string
  scene_type: string
  category: string
  scene: string
  path: string
  subdir: string
  size_kb: number
  position: { x: number; y: number; z: number }
  tags: string[]
}

/** 把 file:///C:/Users/... 转成 http://localhost:8888/相对路径 */
function toHttpUrl(filePath: string): string {
  try {
    // 处理 file:///C:/Users/... 格式
    let rel = filePath
    if (filePath.startsWith('file://')) {
      rel = filePath.slice(7) // 去掉 file://
      // Windows: file:///C:/Users/... → C:/Users/...
      if (rel.startsWith('/')) rel = rel.slice(1)
    }
    // 去掉 RENDER_ROOT 前缀
    if (rel.startsWith(RENDER_ROOT)) {
      rel = rel.slice(RENDER_ROOT.length)
    }
    // 去掉开头的 / 或 \
    rel = rel.replace(/^[\\/]+/, '')
    // 编码中文路径
    const encoded = encodeURI(rel)
    return `${IMG_PROXY}/${encoded}`
  } catch {
    return filePath
  }
}

let _cache: RenderingObject[] | null = null

async function loadRenderings(): Promise<RenderingObject[]> {
  if (_cache) return _cache
  try {
    const resp = await fetch('/data/rendering_objects.json')
    const data = await resp.json()
    _cache = data as RenderingObject[]
    return _cache
  } catch {
    return []
  }
}

export default function RenderingGallery() {
  const activeScene = useBuildingStore((s) => s.activeScene)
  const [renderings, setRenderings] = useState<RenderingObject[]>([])
  const [loaded, setLoaded] = useState(false)
  const [filterCat, setFilterCat] = useState<string>('all')
  const [filterScene, setFilterScene] = useState<string>('all')
  const [selected, setSelected] = useState<RenderingObject | null>(null)
  const [previewOpen, setPreviewOpen] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  // 记录加载失败的图片 ID（避免重复请求）
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set())

  useEffect(() => {
    const id = setInterval(() => { _cache = null; setRefreshKey(p => p + 1) }, 30000)
    return () => clearInterval(id)
  }, [])
  useEffect(() => {
    _cache = null
    setLoaded(false)
    loadRenderings().then(data => {
      setRenderings(data)
      setLoaded(true)
    })
  }, [refreshKey])

  function handleImgError(id: string) {
    setFailedImages(prev => new Set([...prev, id]))
  }

  const stats = useMemo(() => {
    const s: Record<string, number> = {}
    renderings.forEach(r => { s[r.category] = (s[r.category] || 0) + 1 })
    return s
  }, [renderings])

  const sceneStats = useMemo(() => {
    const s: Record<string, number> = {}
    renderings.forEach(r => { s[r.scene] = (s[r.scene] || 0) + 1 })
    return s
  }, [renderings])

  const sceneOptions = useMemo(() => {
    const cats: Record<string, Set<string>> = {}
    renderings.forEach(r => {
      if (!cats[r.category]) cats[r.category] = new Set()
      cats[r.category].add(r.scene)
    })
    return cats
  }, [renderings])

  const filtered = useMemo(() => {
    let list = renderings
    if (filterCat !== 'all') list = list.filter(r => r.category === filterCat)
    if (filterScene !== 'all') list = list.filter(r => r.scene === filterScene)
    return list
  }, [renderings, filterCat, filterScene])

  if (activeScene !== 'renderings') return null

  return (
    <>
      <div className="rgallery">
        <div className="rgallery-header">
          <h3>🖼️ 效果图世界</h3>
          <span className="rgallery-count">{renderings.length} 张</span>
        </div>

        <div className="rgallery-tabs">
          <button className={filterCat === 'all' ? 'active' : ''} onClick={() => { setFilterCat('all'); setFilterScene('all') }}>
            全部({renderings.length})
          </button>
          {Object.entries(stats).map(([cat, count]) => (
            <button key={cat} className={filterCat === cat ? 'active' : ''} onClick={() => { setFilterCat(cat); setFilterScene('all') }}>
              {cat}({count})
            </button>
          ))}
        </div>

        {filterCat !== 'all' && sceneOptions[filterCat] && (
          <div className="rgallery-scenes">
            <button className={filterScene === 'all' ? 'active' : ''} onClick={() => setFilterScene('all')}>全部场景</button>
            {Array.from(sceneOptions[filterCat]).map(scene => (
              <button key={scene} className={filterScene === scene ? 'active' : ''} onClick={() => setFilterScene(scene)}>
                {scene}({sceneStats[scene]})
              </button>
            ))}
          </div>
        )}

        <div className="rgallery-stats">
          {Object.entries(sceneStats).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([scene, count]) => (
            <div key={scene} className="rgallery-stat">
              <span className="rgallery-stat-label">{scene}</span>
              <div className="rgallery-stat-bar">
                <div className="rgallery-stat-fill" style={{ width: `${Math.min(100, (count / renderings.length) * 600)}%` }} />
              </div>
              <span className="rgallery-stat-count">{count}张</span>
            </div>
          ))}
        </div>

        <div className="rgallery-grid">
          {filtered.length === 0 ? (
            <div className="rgallery-empty">加载中...</div>
          ) : (
            filtered.slice(0, 48).map(r => {
              const imgUrl = failedImages.has(r.id) ? null : toHttpUrl(r.path)
              const bgStyle = imgUrl
                ? { backgroundImage: `url(${imgUrl})` }
                : { background: 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)' }
              return (
              <div key={r.id} className={`rgallery-item ${selected?.id === r.id ? 'selected' : ''}`} onClick={() => setSelected(r)} title={r.name}>
                <div className="rgallery-thumb" style={bgStyle}
                  onClick={e => { e.stopPropagation(); setSelected(r); setPreviewOpen(true) }}
                  onError={() => handleImgError(r.id)}>
                  {imgUrl && <img src={imgUrl} alt="" style={{ display: 'none' }} onError={() => handleImgError(r.id)} />}
                  {(!imgUrl || failedImages.has(r.id)) && (
                    <div className="rgallery-thumb-placeholder">
                      <span>{r.category[0]}</span>
                    </div>
                  )}
                  <span className="rgallery-badge">{r.category}</span>
                </div>
                <div className="rgallery-item-info">
                  <span className="rgallery-item-scene">{r.scene}</span>
                  <span className="rgallery-item-name">{r.name.slice(0, 14)}</span>
                </div>
              </div>
            )})
          )}
        </div>

        {filtered.length > 48 && (
          <div className="rgallery-more">还有 {filtered.length - 48} 张，继续浏览</div>
        )}

        {selected && (
          <div className="rgallery-detail">
            <div className="rgallery-detail-tags">
              {selected.tags.map(t => <span key={t} className="rgallery-tag">{t}</span>)}
            </div>
            <div className="rgallery-detail-meta">
              <span>{selected.category} / {selected.scene}</span>
              <span>{selected.size_kb}KB</span>
              <span>{selected.subdir || '根目录'}</span>
            </div>
          </div>
        )}
      </div>

      {previewOpen && selected && (
        <div className="rgallery-preview" onClick={() => setPreviewOpen(false)}>
          <div className="rgallery-preview-inner" onClick={e => e.stopPropagation()}>
            <button className="rgallery-preview-close" onClick={() => setPreviewOpen(false)}>X</button>
            <img src={toHttpUrl(selected.path)} alt={selected.name} className="rgallery-preview-img"
              onError={e => { (e.target as HTMLImageElement).style.display = 'none' }} />
            <div className="rgallery-preview-info">
              <h4>{selected.name}</h4>
              <p>{selected.category} / {selected.scene} | {selected.tags.join(' | ')}</p>
              <p>{selected.path}</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
