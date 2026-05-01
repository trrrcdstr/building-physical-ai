/**
 * LitBuildingScene — 带动态阳光的3D建筑场景
 * 接收 time/lat/lng props，根据太阳位置实时调整光照和阴影
 */
import { useRef, useEffect, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import SunCalc from 'suncalc'
import { useBuildingStore } from '../store/buildingStore'
import { ROOM_COLORS } from '../data/sceneConfig'
import { BuildingObject } from '../types/world'

// ── 太阳位置计算 ────────────────────────────────────────────────
function degToRad(d: number) { return d * Math.PI / 180 }

function calcSunLight(time: Date, lat: number, lng: number) {
  const pos = SunCalc.getPosition(time, lat, lng)
  const altDeg = pos.altitude   // 高度角（°）
  const aziDeg = ((pos.azimuth * 180 / Math.PI) + 360) % 360 // 方位角（°），北=0

  // 光强：地平线上为正，否则为0
  const intensity = Math.max(0, Math.sin(degToRad(altDeg)))

  // Three.js directionalLight 位置
  const r = 120
  const altRad = degToRad(altDeg)
  const aziRad = degToRad(aziDeg)
  const proj = r * Math.cos(altRad)          // 投影半径
  const x = proj * Math.sin(aziRad - Math.PI / 2)
  const y = r * Math.sin(altRad)
  const z = proj * Math.cos(aziRad - Math.PI / 2)

  return { x, y, z, intensity, altDeg, aziDeg, isNight: altDeg < 0 }
}

// ── 动态阳光 ────────────────────────────────────────────────────
interface SunLightProps {
  time: Date
  lat: number
  lng: number
}

function SunLight({ time, lat, lng }: SunLightProps) {
  const lightRef = useRef<THREE.DirectionalLight>(null)

  useFrame(() => {
    const { x, y, z, intensity, isNight } = calcSunLight(time, lat, lng)
    if (!lightRef.current) return

    lightRef.current.position.set(x, y, z)

    // 白天：0.5-1.2，夜间：0.05（月光/环境光）
    const baseIntensity = isNight ? 0.05 : 0.5 + intensity * 0.7
    lightRef.current.intensity = baseIntensity

    // 夜间月光偏蓝
    lightRef.current.color.set(
      isNight
        ? new THREE.Color(0.7, 0.75, 1.0)   // 月光：淡蓝色
        : new THREE.Color(1.0, 0.95, 0.85)  // 阳光：暖白色
    )
  })

  return (
    <>
      {/* 主方向光（太阳/月光） */}
      <directionalLight
        ref={lightRef}
        position={[100, 80, -50]}
        intensity={1}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-near={0.5}
        shadow-camera-far={500}
        shadow-camera-left={-200}
        shadow-camera-right={200}
        shadow-camera-top={200}
        shadow-camera-bottom={-200}
        shadow-bias={-0.001}
      />
    </>
  )
}

// ── 单个房间（带阴影）──────────────────────────────────────────
function Room({ obj, index }: { obj: BuildingObject; index: number }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const selectObject = useBuildingStore((s) => s.selectObject)
  const selectedObject = useBuildingStore((s) => s.selectedObject)
  const selectWall = useBuildingStore((s) => s.selectWall)
  const selectedWall = useBuildingStore((s) => s.selectedWall)

  const isSelected = selectedObject?.id === obj.id
  const cat = obj.vrData?.room_category || '其他'
  const baseColor = ROOM_COLORS[cat] || ROOM_COLORS['其他']
  const { width, depth } = obj.dimensions
  const [cx, , cz] = obj.position
  const floorX = cx + width / 2
  const floorZ = cz + depth / 2

  // 悬浮动画
  useFrame(({ clock }) => {
    if (!meshRef.current) return
    const t = clock.elapsedTime
    const targetY = isSelected ? 0.3 : 0
    meshRef.current.position.y = THREE.MathUtils.lerp(
      meshRef.current.position.y, targetY + Math.sin(t * 1.5 + index * 0.3) * 0.04, 0.08
    )
    const mat = meshRef.current.material as THREE.MeshStandardMaterial
    mat.opacity = THREE.MathUtils.lerp(mat.opacity, isSelected ? 1 : 0.75, 0.1)
  })

  const handleClick = (e: any) => {
    e.stopPropagation()
    selectObject(isSelected ? null : obj)
  }

  return (
    <group>
      {/* 地板（接收阴影） */}
      <mesh
        ref={meshRef}
        position={[floorX, 0.05, floorZ]}
        rotation={[-Math.PI / 2, 0, 0]}
        onClick={handleClick}
        onPointerEnter={(e) => { e.stopPropagation(); document.body.style.cursor = 'pointer' }}
        onPointerLeave={() => { document.body.style.cursor = 'default' }}
        receiveShadow
        castShadow
      >
        <planeGeometry args={[width, depth]} />
        <meshStandardMaterial color={isSelected ? '#4CAF50' : baseColor} transparent opacity={0.85} roughness={0.8} metalness={0.1} />
      </mesh>

      {/* 地板边框 */}
      <lineSegments position={[floorX, 0.06, floorZ]}>
        <edgesGeometry args={[new THREE.BoxGeometry(width, 0.01, depth)]} />
        <lineBasicMaterial color={isSelected ? '#4CAF50' : '#888'} />
      </lineSegments>

      {/* 北墙（承重墙） */}
      <WallBox
        position={[floorX, 1.4, cz]}
        args={[width, 2.8, 0.12]}
        color={selectedWall?.roomId === obj.id && selectedWall?.wall === 'north' ? '#E53935' : '#D4A0A0'}
        opacity={selectedWall?.roomId === obj.id && selectedWall?.wall === 'north' ? 0.7 : 0.35}
        onClick={(e: any) => { e.stopPropagation(); selectWall({ roomId: obj.id, wall: 'north', isLoadBearing: true }) }}
      />

      {/* 南墙 */}
      <WallBox
        position={[floorX, 1.0, cz + depth]}
        args={[width, 2.0, 0.12]}
        color={selectedWall?.roomId === obj.id && selectedWall?.wall === 'south' ? '#4CAF50' : '#C8B090'}
        opacity={selectedWall?.roomId === obj.id && selectedWall?.wall === 'south' ? 0.6 : 0.3}
        onClick={(e: any) => { e.stopPropagation(); selectWall({ roomId: obj.id, wall: 'south', isLoadBearing: false }) }}
      />

      {/* 东墙 */}
      <WallBox
        position={[cx + width, 1.4, floorZ]}
        args={[0.12, 2.8, depth]}
        color={selectedWall?.roomId === obj.id && selectedWall?.wall === 'east' ? '#4CAF50' : '#C8B090'}
        opacity={selectedWall?.roomId === obj.id && selectedWall?.wall === 'east' ? 0.6 : 0.3}
        onClick={(e: any) => { e.stopPropagation(); selectWall({ roomId: obj.id, wall: 'east', isLoadBearing: false }) }}
      />

      {/* 西墙 */}
      <WallBox
        position={[cx, 1.4, floorZ]}
        args={[0.12, 2.8, depth]}
        color={selectedWall?.roomId === obj.id && selectedWall?.wall === 'west' ? '#4CAF50' : '#C8B090'}
        opacity={selectedWall?.roomId === obj.id && selectedWall?.wall === 'west' ? 0.6 : 0.3}
        onClick={(e: any) => { e.stopPropagation(); selectWall({ roomId: obj.id, wall: 'west', isLoadBearing: false }) }}
      />

      {/* 选中时显示标签 */}
      {isSelected && (
        <mesh position={[floorX, 3.5, floorZ]}>
          <sphereGeometry args={[0.18, 12, 12]} />
          <meshStandardMaterial color="#F44336" emissive="#F44336" emissiveIntensity={0.8} />
        </mesh>
      )}
    </group>
  )
}

function WallBox({ position, args, color, opacity, onClick }: any) {
  return (
    <mesh position={position} onClick={onClick}
      onPointerEnter={(e: any) => { e.stopPropagation(); document.body.style.cursor = 'pointer' }}
      onPointerLeave={() => { document.body.style.cursor = 'default' }}
      castShadow receiveShadow>
      <boxGeometry args={args} />
      <meshStandardMaterial color={color} transparent opacity={opacity} />
    </mesh>
  )
}

// ── 主场景 ────────────────────────────────────────────────────
export interface LitBuildingSceneProps {
  time: Date
  lat: number
  lng: number
}

export default function LitBuildingScene({ time, lat, lng }: LitBuildingSceneProps) {
  const objects = useBuildingStore((s) => s.objects)
  const selectObject = useBuildingStore((s) => s.selectObject)
  const selectWall = useBuildingStore((s) => s.selectWall)

  const rooms = useMemo(() => objects.filter(o => !o.id.startsWith('parking-') && !o.id.startsWith('basement-')), [objects])
  const parking = useMemo(() => objects.filter(o => o.id.startsWith('parking-')), [objects])

  const handleBackgroundClick = () => { selectObject(null); selectWall(null) }

  const sunInfo = calcSunLight(time, lat, lng)

  return (
    <group>
      {/* 动态阳光 */}
      <SunLight time={time} lat={lat} lng={lng} />

      {/* 环境光（夜间更暗） */}
      <ambientLight intensity={sunInfo.isNight ? 0.02 : 0.4} />

      {/* 背景点击取消选择 */}
      <mesh position={[0, -0.1, 0]} rotation={[-Math.PI / 2, 0, 0]} onClick={handleBackgroundClick}>
        <planeGeometry args={[500, 500]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>

      {/* 房间 */}
      {rooms.map((obj, i) => <Room key={obj.id} obj={obj} index={i} />)}
      {parking.map((obj) => <ParkingSpot key={obj.id} obj={obj} />)}
    </group>
  )
}

// ── 停车位（保留原版）──────────────────────────────────────────
function ParkingSpot({ obj }: { obj: BuildingObject }) {
  const { width, depth } = obj.dimensions
  const [cx, , cz] = obj.position
  const selectObject = useBuildingStore((s) => s.selectObject)

  return (
    <mesh
      position={[cx + width / 2, 0.02, cz + depth / 2]}
      rotation={[-Math.PI / 2, 0, 0]}
      onClick={(e: any) => { e.stopPropagation(); selectObject(obj) }}
      receiveShadow
    >
      <planeGeometry args={[width, depth]} />
      <meshStandardMaterial color="#37474F" roughness={0.9} />
    </mesh>
  )
}
