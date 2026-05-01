import React, { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Stars } from '@react-three/drei'
import { ErrorBoundary } from './components/ErrorBoundary'
import BuildingScene from './scenes/BuildingScene'
import LitBuildingScene from './scenes/LitBuildingScene'
import RelationScene from './scenes/RelationScene'
import GaussianScene from './scenes/GaussianScene'
import SunCalcTimeController from './components/SunCalcTimeController'
import EstateScene from './components/EstateScene'
import TopBar from './components/TopBar'
import SceneNavigator from './components/SceneNavigator'
import SceneColumn from './components/SceneColumn'
import PhysicsPanel from './components/PhysicsPanel'
import AgentCommandPanel from './components/AgentCommandPanel'
import StatusBar from './components/StatusBar'
import NeuralInferencePanel from './components/NeuralInferencePanel'
import VRViewer from './components/VRViewer'
import RenderingGallery from './components/RenderingGallery'
import { useBuildingStore } from './store/buildingStore'
import { useState, useEffect } from 'react'
import { worldObjects, sceneData } from './data/sceneData'
import './App.css'
import { API_BASE_URL } from './config/api'

const API_BASE = API_BASE_URL + '/api'

// ── 场景懒加载（与旧版逻辑完全兼容）────────────────────────────
function SceneLoader() {
  const activeScene = useBuildingStore(s => s.activeScene)
  const loadObjects = useBuildingStore(s => s.loadObjects)

  useEffect(() => {
    if (activeScene === 'sample' || activeScene === 'all') {
      loadObjects(worldObjects as any)
    } else if (activeScene === 'ns_basement') {
      // nsBasement.ts has encoding corruption - temporarily use sample data
      loadObjects(worldObjects as any)
    } else if (activeScene !== 'relation' && activeScene !== 'estate_topology') {
      const sceneObjs = (sceneData as any)[activeScene]
      loadObjects((sceneObjs || []) as any)
    }
  }, [activeScene])

  return null
}

// ── 相机控制器（皮·骨·肉场景自适应）───────────────────────────
// ── 相机控制器（皮·骨·肉场景自适应）──────────────────────────
// 数据中心位置（worldObjects 的几何中心）
const DATA_CENTER: [number, number, number] = [-3.7, 0, 0.8]
const DATA_RADIUS = 30  // 数据范围半径

function CameraController() {
  const activeScene = useBuildingStore(s => s.activeScene)
  const sceneView = useActiveSceneView()

  // 小区拓扑场景使用不同的相机参数
  if (activeScene === 'estate_topology') {
    return (
      <OrbitControls
        makeDefault
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={600}
        maxPolarAngle={Math.PI / 2.05}
        target={[0, 0, 0]}
        dampingFactor={0.08}
        enableDamping={true}
      />
    )
  }

  // 时空光影/建筑场景 → 对准数据中心
  const target = sceneView === 'spatio_temporal' || sceneView === 'building'
    ? DATA_CENTER
    : [150, 2, -3]  // relation scene: 门/窗区域

  return (
    <OrbitControls
      makeDefault
      enablePan={true}
      enableZoom={true}
      enableRotate={true}
      minDistance={2}
      maxDistance={sceneView === 'spatio_temporal' ? DATA_RADIUS * 3 : 400}
      maxPolarAngle={Math.PI / 2.15}
      target={target}
      dampingFactor={0.05}
      enableDamping={true}
    />
  )
}

function useRefreshKey() {
  const [refreshKey, setRefreshKey] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setRefreshKey(p => p + 1), 30000)
    return () => clearInterval(id)
  }, [])
  return refreshKey
}

// ── 关系数据加载（带自动刷新）──────────────────────────────
function useRelationEdges(activeScene: string) {
  const [edges, setEdges] = useState<any[]>([])
  const refreshKey = useRefreshKey()

  useEffect(() => {
    if (activeScene !== 'relation') { setEdges([]); return }
    fetch(`${API_BASE}/scene`)
      .then(r => r.json())
      .then((data: any) => {
        const positions = data.positions as [number, number, number][]
        if (!positions) { setEdges([]); return }
        const n = positions.length
        const result: any[] = []
        for (let i = 0; i < n; i++) {
          for (let j = i + 1; j < n; j++) {
            const pi = positions[i], pj = positions[j]
            const dist = Math.sqrt(
              (pi[0] - pj[0]) ** 2 + (pi[1] - pj[1]) ** 2 + (pi[2] - pj[2]) ** 2
            )
            if (dist < 20) {
              result.push({
                source: i, target: j, distance: dist,
                relation: dist < 5 ? 'same_room' : 'diff_room',
                probability: dist < 5 ? 0.99 : 0.01,
              })
            }
          }
        }
        setEdges(result)
      })
      .catch(() => setEdges([]))
  }, [activeScene, refreshKey])

  return edges
}

// ── 获取相机初始位置（根据场景）─────────────────────────────
function getCameraPosition(activeScene: string): [number, number, number] {
  switch (activeScene) {
    case 'estate_topology':
      return [0, 300, 280]
    case 'relation':
      // 门/窗在 [150, ~1, -3]，俯视角度看
      return [150, 8, 12]
    // 时空光影场景：对准数据中心 [-3.7, 0, 0.8]，斜上方45°视角
    case 'spatio_temporal':
      return [DATA_CENTER[0], 25, DATA_CENTER[2] + 25]
    case 'gaussian':
      return [DATA_CENTER[0], 25, DATA_CENTER[2] + 25]
    // 默认建筑场景：也对准数据中心
    default:
      return [DATA_CENTER[0], 25, DATA_CENTER[2] + 25]
  }
}

// ── 判断当前应渲染哪个3D场景（皮·骨·肉入口逻辑）────────────────
function useActiveSceneView() {
  const currentSceneType = useBuildingStore(s => s.currentSceneType)
  const activeScene = useBuildingStore(s => s.activeScene)

  // 优先用新版 currentSceneType 判断（SceneNavigator 入口）
  // 降级用旧版 activeScene（TopBar 直接操作）
  if (currentSceneType === 'estate') {
    return 'estate'
  }
  if (currentSceneType === 'relation_graph') {
    return 'relation'
  }
  if (currentSceneType === 'spatio_temporal') {
    return 'spatio_temporal'
  }
  if (currentSceneType === 'gaussian') {
    return 'gaussian'
  }
  // 住宅、园林、商场、办公、酒店、工业 → BuildingScene
  return 'building'
}

// ────────────────────────────────────────────────────────────
export default function App() {
  const activeScene = useBuildingStore(s => s.activeScene)
  const currentSceneType = useBuildingStore(s => s.currentSceneType)
  const [selectedDoorId, setSelectedDoorId] = useState<number | undefined>(undefined)
  const [showRelations, setShowRelations] = useState(true)
  const relationEdges = useRelationEdges(activeScene)
  const cameraPos = getCameraPosition(activeScene)
  const sceneView = useActiveSceneView()
  const sunTime = useBuildingStore(s => s.sunTime)
  const sunLat = useBuildingStore(s => s.sunLat)
  const sunLng = useBuildingStore(s => s.sunLng)
  const setSunState = useBuildingStore(s => s.setSunState)
  const loadObjects = useBuildingStore(s => s.loadObjects)

  // spatio_temporal 场景加载 worldObjects
  useEffect(() => {
    if (sceneView === 'spatio_temporal') {
      loadObjects(worldObjects as any)
    }
  }, [sceneView])

  // 判断是否为小区拓扑场景（控制主面板显隐）
  const isEstateScene = sceneView === 'estate'

  // 渲染哪个 3D 场景
  const renderScene = () => {
    switch (sceneView) {
      case 'estate':
        return <EstateScene />
      case 'relation':
        return (
          <RelationScene
            selectedId={selectedDoorId}
            onSelect={setSelectedDoorId}
            relations={relationEdges}
            showRelations={showRelations}
          />
        )
      case 'spatio_temporal':
        return <LitBuildingScene time={sunTime} lat={sunLat} lng={sunLng} />
      case 'gaussian':
        return <GaussianScene />
      default:
        return <BuildingScene />
    }
  }

  return (
    <div className="app-container">

      {/* ── 顶部导航栏 ───────────────────── */}
      <TopBar />

      {/* ── 皮·骨·肉场景卡片导航（新增）──── */}
      <SceneNavigator />

      {/* ── 主区域（三栏叙事流）──────────── */}
      <div className="main-body" style={{ display: isEstateScene ? 'none' : undefined }}>

        {/* 左栏：3D场景视图（感知层） */}
        <SceneColumn />

        {/* 中栏：物理常识面板（分析层） */}
        <PhysicsPanel />

        {/* 右栏：Agent任务面板（执行层） */}
        <AgentCommandPanel />

      </div>

      {/* ── 3D Canvas（全屏底层）───────────── */}
      <Canvas
        shadows
        gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
        camera={{ position: cameraPos, fov: isEstateScene ? 50 : 55, near: 0.1, far: isEstateScene ? 3000 : 2000 }}
        style={{ position: 'absolute', inset: 0, zIndex: 0, pointerEvents: 'auto' }}
      >
        <PerspectiveCamera makeDefault fov={isEstateScene ? 50 : 55} near={0.1} far={isEstateScene ? 3000 : 2000} />
        <CameraController />
        <color attach="background" args={['#060612']} />
        {/* Stars: spatio_temporal 时减弱星空亮度，突出场景 */}
        <Stars
          radius={sceneView === 'spatio_temporal' ? 80 : (isEstateScene ? 350 : 200)}
          depth={50}
          count={sceneView === 'spatio_temporal' ? 500 : (isEstateScene ? 3000 : 2000)}
          factor={sceneView === 'spatio_temporal' ? 2 : 4}
          saturation={0.3}
          fade
          speed={0.3}
        />
        <ambientLight intensity={0.25} />
        <directionalLight
          position={[40, 60, 30]}
          intensity={0.7}
          castShadow
          shadow-mapSize={[2048, 2048]}
          shadow-camera-far={isEstateScene ? 800 : 400}
          shadow-camera-left={isEstateScene ? -300 : -150}
          shadow-camera-right={isEstateScene ? 300 : 150}
          shadow-camera-top={isEstateScene ? 250 : 150}
          shadow-camera-bottom={isEstateScene ? -250 : -150}
        />
        <pointLight position={[-30, 20, -30]} intensity={0.25} color="#4488ff" />
        <pointLight position={[200, 15, 20]} intensity={0.3} color="#FFA500" />
        <hemisphereLight args={['#87CEEB', '#8B7355', 0.3]} />

        <ErrorBoundary>
          {renderScene()}
        </ErrorBoundary>
      </Canvas>

      {/* ── 底层组件（始终存在但可隐藏）──── */}
      <StatusBar />
      {sceneView === 'relation' && (
        <div className="neural-panel-container" style={{ bottom: 16, left: 16, right: 16, height: 280, zIndex: 10 }}>
          <NeuralInferencePanel
            selectedDoorId={selectedDoorId}
            onSelectDoor={setSelectedDoorId}
            onToggleRelations={() => setShowRelations(v => !v)}
            showRelations={showRelations}
          />
        </div>
      )}
      <VRViewer />
      <RenderingGallery />
      <SceneLoader />

      {/* ── 时空光影控制器（仅在时空场景显示）── */}
      {sceneView === 'spatio_temporal' && (
        <SunCalcTimeController
          onChange={({ time, lat, lng }) => setSunState(time, lat, lng)}
        />
      )}
    </div>
  )
}
