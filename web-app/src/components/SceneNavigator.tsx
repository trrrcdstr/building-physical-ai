import { useBuildingStore } from '../store/buildingStore'
import './SceneNavigator.css'

// ── 场景类型枚举（与 buildingStore 对齐）────────────────────
export type NavigatorSceneType =
  | 'residential_villa' // 住宅别墅 → store: 'residence'
  | 'garden'            // 园林    → store: 'villa_garden'
  | 'commercial'        // 商场    → store: 'mall'
  | 'office'            // 办公    → store: 'office'
  | 'hotel'             // 酒店    → store: 'hotel'
  | 'industrial'        // 工业    → store: 'sample'
  | 'estate'            // 小区拓扑 → store: 'estate_topology'
  | 'relation_graph'   // 关系图  → store: 'relation'
  | 'spatio_temporal'   // 时空光影

// ── 场景卡片数据（效果图统计）────────────────────────────────
interface SceneCardData {
  id: NavigatorSceneType
  icon: string
  name: string
  count: number | string
  countLabel: string
  storeValue: string
}

const SCENE_CARDS: SceneCardData[] = [
  {
    id: 'residential_villa',
    icon: '🏠',
    name: '住宅',
    count: 613,
    countLabel: '效果图',
    storeValue: 'residence',
  },
  {
    id: 'garden',
    icon: '🌳',
    name: '园林',
    count: 76,
    countLabel: '效果图',
    storeValue: 'villa_garden',
  },
  {
    id: 'commercial',
    icon: '🏬',
    name: '商场',
    count: 28,
    countLabel: '效果图',
    storeValue: 'mall',
  },
  {
    id: 'office',
    icon: '🏢',
    name: '办公',
    count: 6,
    countLabel: '效果图',
    storeValue: 'office',
  },
  {
    id: 'hotel',
    icon: '🏨',
    name: '酒店',
    count: 20,
    countLabel: '效果图',
    storeValue: 'hotel',
  },
  {
    id: 'industrial',
    icon: '🏭',
    name: '工业',
    count: 6,
    countLabel: '效果图',
    storeValue: 'sample',
  },
]

// ── 特殊视图按钮数据 ─────────────────────────────────────────
interface SpecialViewData {
  id: 'estate' | 'relation_graph' | 'spatio_temporal'
  icon: string
  name: string
  storeValue: string
}

const SPECIAL_VIEWS: SpecialViewData[] = [
  { id: 'estate', icon: '🏘️', name: '小区拓扑', storeValue: 'estate_topology' },
  { id: 'relation_graph', icon: '🕸️', name: '关系图', storeValue: 'relation' },
  { id: 'spatio_temporal', icon: '☀️', name: '时空光影', storeValue: 'residence' },
  { id: 'gaussian', icon: '🎯', name: '高斯重建', storeValue: 'gaussian' },
]

// ── 判断当前激活的场景卡片 ─────────────────────────────────
function isCardActive(card: SceneCardData, specialActive: SpecialViewData | null, activeScene: string): boolean {
  if (specialActive) return false
  return activeScene === card.storeValue
}

function isSpecialActive(view: SpecialViewData, activeScene: string, currentSceneType: string): boolean {
  if (view.id === 'spatio_temporal') return currentSceneType === 'spatio_temporal'
  return activeScene === view.storeValue
}

// ── 主组件 ───────────────────────────────────────────────────
export default function SceneNavigator() {
  const activeScene = useBuildingStore((s) => s.activeScene)
  const currentSceneType = useBuildingStore((s) => s.currentSceneType)
  const setActiveScene = useBuildingStore((s) => s.setActiveScene)
  const setCurrentSceneType = useBuildingStore((s) => s.setCurrentSceneType)

  // 判断当前激活的是哪种特殊视图
  const activeSpecial =
    SPECIAL_VIEWS.find((v) => {
      if (v.id === 'spatio_temporal') return currentSceneType === 'spatio_temporal'
      if (v.id === 'gaussian') return currentSceneType === 'gaussian'
      return activeScene === v.storeValue
    }) ?? null

  function handleCardClick(card: SceneCardData) {
    setActiveScene(card.storeValue as any)
  }

  function handleSpecialClick(view: SpecialViewData) {
    if (view.id === 'spatio_temporal') {
      setCurrentSceneType('spatio_temporal')
    } else if (view.id === 'gaussian') {
      setCurrentSceneType('gaussian')
    } else {
      setActiveScene(view.storeValue as any)
    }
  }

  return (
    <div className="scene-navigator">
      {/* 横向滚动卡片区 */}
      <div className="sn-scroll-track">
        {SCENE_CARDS.map((card) => (
          <button
            key={card.id}
            className={`sn-card ${isCardActive(card, activeSpecial, activeScene) ? 'sn-card--active' : ''}`}
            onClick={() => handleCardClick(card)}
            title={`切换到${card.name}场景（${card.count}${card.countLabel}）`}
          >
            <span className="sn-card-icon">{card.icon}</span>
            <span className="sn-card-name">{card.name}</span>
            <span className="sn-card-count">
              <span className="sn-card-num">{card.count}</span>
              <span className="sn-card-unit">{card.countLabel}</span>
            </span>
          </button>
        ))}
      </div>

      {/* 分隔线 */}
      <div className="sn-divider" />

      {/* 右侧特殊视图按钮 */}
      <div className="sn-special-views">
        {SPECIAL_VIEWS.map((view) => (
          <button
            key={view.id}
            className={`sn-special-btn ${isSpecialActive(view, activeScene, currentSceneType) ? 'sn-special-btn--active' : ''}`}
            onClick={() => handleSpecialClick(view)}
            title={`切换到${view.name}视图`}
          >
            <span className="sn-special-icon">{view.icon}</span>
            <span className="sn-special-label">{view.name}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
