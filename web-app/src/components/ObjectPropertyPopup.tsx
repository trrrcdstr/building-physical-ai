import { useEffect, useRef, useState } from 'react'
import { useBuildingStore } from '../store/buildingStore'
import { OBJECT_PHYSICS_MAP, inferMaterialFromObject } from '../shared/physicsConstants'

interface PopupState {
  visible: boolean
  x: number
  y: number
  name: string
  typeLabel: string
  physicsKey: string | null
  physicsData: ReturnType<typeof OBJECT_PHYSICS_MAP.get> extends infer T ? T : never
}

export default function ObjectPropertyPopup() {
  const hoveredObject = useBuildingStore(s => (s as any).hoveredObject as {
    id: string; name: string; category?: string; type?: string
  } | null)
  const [popup, setPopup] = useState<PopupState>({
    visible: false, x: 0, y: 0, name: '', typeLabel: '', physicsKey: null, physicsData: null,
  })
  const [fading, setFading] = useState(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const mouseRef = useRef({ x: 0, y: 0 })

  // 鼠标移动监听
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY }
      if (popup.visible) {
        // 实时跟随鼠标，但避免左上角溢出
        const x = Math.min(e.clientX + 14, window.innerWidth - 230)
        const y = Math.min(e.clientY + 10, window.innerHeight - 100)
        setPopup(p => ({ ...p, x, y }))
      }
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [popup.visible])

  // hoveredObject 变化处理
  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current)

    if (!hoveredObject) {
      // 消失动画
      if (popup.visible) {
        setFading(true)
        timerRef.current = setTimeout(() => {
          setPopup(p => ({ ...p, visible: false }))
          setFading(false)
        }, 300)
      }
      return
    }

    // 显示弹窗
    const obj = hoveredObject
    const physicsKey = inferMaterialFromObject(obj) ?? 'wall_brick'
    const physicsData = OBJECT_PHYSICS_MAP[physicsKey] ?? null

    const typeLabelMap: Record<string, string> = {
      wall: '墙体', floor: '地面', ceiling: '顶棚', door: '门', window: '窗',
      furniture: '家具', appliance: '家电', stairs: '楼梯', corridor: '走廊',
      landscape: '景观',
    }
    const typeLabel = typeLabelMap[obj.type ?? ''] ?? obj.category ?? obj.type ?? '物体'

    const x = Math.min(mouseRef.current.x + 14, window.innerWidth - 230)
    const y = Math.min(mouseRef.current.y + 10, window.innerHeight - 100)

    setPopup({
      visible: true, x, y,
      name: obj.name || typeLabel,
      typeLabel,
      physicsKey,
      physicsData,
    })
    setFading(false)
  }, [hoveredObject?.id])

  // 清理
  useEffect(() => () => { if (timerRef.current) clearTimeout(timerRef.current) }, [])

  if (!popup.visible) return null

  const pd = popup.physicsData

  return (
    <div
      className={`object-popup ${fading ? 'fade-out' : ''}`}
      style={{ left: popup.x, top: popup.y }}
    >
      {/* 头部：名称 */}
      <div className="object-popup-header">
        <span className="object-popup-icon">
          {pd?.objectType.includes('墙') ? '🧱'
            : pd?.objectType.includes('地面') || pd?.objectType.includes('地板') ? '🪵'
            : pd?.objectType.includes('玻璃') ? '🪟'
            : pd?.objectType.includes('门') ? '🚪'
            : '📦'}
        </span>
        <span className="object-popup-name">{popup.name}</span>
        <span className="object-popup-type">{popup.typeLabel}</span>
      </div>

      {/* 关键物理属性 */}
      <div className="object-popup-attrs">
        {pd ? (
          <>
            <div className="object-popup-attr">
              <span className={`object-popup-attr-dot ${pd.drillable ? 'dot-warning' : 'dot-danger'}`} />
              <span>材质</span>
              <span className="object-popup-attr-value">{pd.material}</span>
            </div>
            <div className="object-popup-attr">
              <span className="object-popup-attr-dot dot-info" />
              <span>摩擦 μ</span>
              <span className="object-popup-attr-value">{pd.friction_dry} (干)</span>
              {pd.friction_wet !== undefined && (
                <span style={{ color: '#f87171', fontSize: 9 }}>/ {pd.friction_wet} (湿)</span>
              )}
            </div>
            <div className="object-popup-attr">
              <span className="object-popup-attr-dot dot-safe" />
              <span>密度</span>
              <span className="object-popup-attr-value">{pd.density} kg/m³</span>
            </div>
            {pd.robot.max_force_n > 0 && (
              <div className="object-popup-attr">
                <span className="object-popup-attr-dot dot-warning" />
                <span>机器人</span>
                <span className="object-popup-attr-value">≤{pd.robot.max_force_n}N</span>
              </div>
            )}
            {pd.rules[0] && (
              <div className="object-popup-attr">
                <span className={`object-popup-attr-dot ${pd.drillable ? 'dot-warning' : 'dot-danger'}`} />
                <span style={{ color: '#fbbf24', fontSize: 9 }}>{pd.rules[0]}</span>
              </div>
            )}
          </>
        ) : (
          <div className="object-popup-attr">
            <span className="object-popup-attr-dot dot-info" />
            <span>点击查看物理详情</span>
          </div>
        )}
      </div>
    </div>
  )
}
