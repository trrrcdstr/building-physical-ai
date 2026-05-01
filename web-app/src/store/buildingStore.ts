import { create } from 'zustand'
import { BuildingObject, SceneCategory } from '../types/world'

// ── 场景类型枚举（皮·骨·肉架构 — 新增 currentSceneType）────────────
export type SceneType =
  | 'residential_villa' // 住宅别墅
  | 'garden'             // 园林
  | 'commercial'        // 商场
  | 'office'            // 办公
  | 'hotel'             // 酒店
  | 'industrial'        // 工业
  | 'estate'            // 小区拓扑
  | 'relation_graph'   // 关系图
  | 'spatio_temporal'   // 时空光影

// 兼容旧版 activeScene 字符串类型
export type LegacySceneType =
  | 'residence' | 'mall' | 'office' | 'hotel'
  | 'villa_garden' | 'park'
  | 'office_building' | 'residential' | 'commercial_complex'
  | 'ns_basement' | 'sample' | 'renderings' | 'vr_scene'
  | 'estate_topology'
  | 'all'
  | 'relation'

// ── Gaussian 选中状态类型 ───────────────────────────────────────────
export interface SelectedGaussian {
  id: string
  position: [number, number, number]
  type: string
  color: [number, number, number]
}

// ── SceneType → LegacySceneType 映射 ───────────────────────────────
const SCENE_TYPE_MAPPING: Record<SceneType, LegacySceneType> = {
  residential_villa: 'residence',
  garden:            'villa_garden',
  commercial:        'mall',
  office:            'office',
  hotel:             'hotel',
  industrial:        'sample',
  estate:            'estate_topology',
  relation_graph:   'relation',
  spatio_temporal:  'residence',
}

// LegacySceneType → SceneType 反向映射（保守，非精确匹配则返回 residential_villa）
const REVERSE_MAPPING: Record<string, SceneType> = {
  residence:         'residential_villa',
  villa_garden:      'garden',
  mall:              'commercial',
  office_building:   'office',
  office:            'office',
  hotel:             'hotel',
  sample:            'industrial',
  estate_topology:   'estate',
  relation:          'relation_graph',
}

interface BuildingState {
  // ── 旧版状态（保留，向下兼容 TopBar 等）─────────────────────────
  activeCategory: SceneCategory | 'all'
  activeScene: LegacySceneType | 'all' | 'relation'
  objects: BuildingObject[]
  selectedObject: BuildingObject | null
  selectedWall: { roomId: string; wall: string; isLoadBearing: boolean } | null
  showPhysics: boolean
  showPaths: boolean
  viewMode: '3d' | 'floorplan' | 'physics'
  currentTask: string | null

  // ── 新版状态（皮·骨·肉 — SceneNavigator 专用）───────────────────
  currentSceneType: SceneType

  // ── Gaussian 选中状态 ─────────────────────────────────────────────
  selectedGaussian: SelectedGaussian | null

  // ── Actions ─────────────────────────────────────────────────────
  setActiveCategory: (cat: SceneCategory | 'all') => void
  setActiveScene: (scene: LegacySceneType | 'all' | 'relation') => void
  selectObject: (obj: BuildingObject | null) => void
  selectWall: (wall: { roomId: string; wall: string; isLoadBearing: boolean } | null) => void
  loadObjects: (data: BuildingObject[]) => void
  setViewMode: (mode: '3d' | 'floorplan' | 'physics') => void
  togglePhysics: () => void
  togglePaths: () => void
  setTask: (task: string | null) => void
  /** 皮·骨·肉入口 — 设置场景类型，同时同步旧版 activeScene */
  setCurrentSceneType: (type: SceneType) => void
  /** 选中 Gaussian 点 */
  selectGaussian: (gaussian: SelectedGaussian | null) => void
  // ── 时空光影状态 ────────────────────────────────────────────────
  sunTime: Date
  sunLat: number
  sunLng: number
  setSunState: (time: Date, lat: number, lng: number) => void
}

export const useBuildingStore = create<BuildingState>((set) => ({
  activeCategory: 'all',
  activeScene: 'residence',
  objects: [],
  selectedObject: null,
  selectedWall: null,
  showPhysics: false,
  showPaths: false,
  viewMode: '3d',
  currentTask: null,

  // 默认使用住宅场景（residential_villa）
  currentSceneType: 'residential_villa',

  // Gaussian 选中状态
  selectedGaussian: null,

  // 时空光影默认值（北京）
  sunTime: new Date(),
  sunLat: 39.9042,
  sunLng: 116.4074,

  setActiveCategory: (cat) => set({ activeCategory: cat }),

  setActiveScene: (scene) =>
    set({ activeScene: scene }),

  selectObject: (obj) => set({ selectedObject: obj, selectedGaussian: null }),

  selectWall: (wall) => set({ selectedWall: wall }),

  loadObjects: (data) => set({ objects: data }),

  setViewMode: (mode) => set({ viewMode: mode }),

  togglePhysics: () => set((s) => ({ showPhysics: !s.showPhysics })),

  togglePaths: () => set((s) => ({ showPaths: !s.showPaths })),

  setTask: (task) => set({ currentTask: task }),

  /** 统一入口：设置 currentSceneType 并同步旧版 activeScene */
  setCurrentSceneType: (type) =>
    set({
      currentSceneType: type,
      activeScene: SCENE_TYPE_MAPPING[type],
    }),

  /** 选中 Gaussian 点，同时清除 selectedObject */
  selectGaussian: (gaussian) =>
    set({
      selectedGaussian: gaussian,
      selectedObject: null,
    }),

  setSunState: (time, lat, lng) => set({ sunTime: time, sunLat: lat, sunLng: lng }),
}))
