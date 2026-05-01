import { useRef, useEffect, useMemo, useState } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { useBuildingStore } from '../store/buildingStore'
import { ROOM_COLORS } from '../data/sceneConfig'
import { BuildingObject } from '../types/world'

// ─── 单个房间（带点击高亮 + Hover效果）───
function Room({ obj, index }: { obj: BuildingObject; index: number }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const wallRefs = useRef<THREE.Mesh[]>([])
  const [hovered, setHovered] = useState(false)
  const [hoveredWall, setHoveredWall] = useState<string | null>(null)
  const selectObject = useBuildingStore((s) => s.selectObject)
  const selectWall = useBuildingStore((s) => s.selectWall)
  const selectedObject = useBuildingStore((s) => s.selectedObject)
  const selectedWall = useBuildingStore((s) => s.selectedWall)
  const showPhysics = useBuildingStore((s) => s.showPhysics)
  const isSelected = selectedObject?.id === obj.id

  const cat = obj.vrData?.room_category || '其他'
  const baseColor = ROOM_COLORS[cat] || ROOM_COLORS['其他']
  const { width, depth } = obj.dimensions

  // 计算位置（地板中心）
  const [cx, cy, cz] = obj.position
  const floorX = cx + width / 2
  const floorZ = cz + depth / 2

  // 选中/悬浮动画
  useFrame(({ clock }) => {
    if (!meshRef.current) return
    const t = clock.elapsedTime
    const targetY = isSelected ? 0.3 : hovered ? 0.15 : 0
    meshRef.current.position.y = THREE.MathUtils.lerp(
      meshRef.current.position.y,
      targetY + Math.sin(t * 1.5 + index * 0.3) * (isSelected ? 0.05 : 0),
      0.08
    )
    // 悬浮时轻微发光
    const targetOpacity = hovered || isSelected ? 1 : 0.75
    ;(meshRef.current.material as THREE.MeshStandardMaterial).opacity = THREE.MathUtils.lerp(
      (meshRef.current.material as THREE.MeshStandardMaterial).opacity,
      targetOpacity,
      0.1
    )
  })

  const handleClick = (e: any) => {
    e.stopPropagation()
    selectObject(isSelected ? null : obj)
  }

  const wallColor = '#C8B090'
  const wallOpacity = 0.35

  // P1：墙体点击联动 —— 承重墙红色，安全区绿色
  const handleWallClick = (wallDir: string, e: any) => {
    e.stopPropagation()
    const isLoadBearing = wallDir === 'north'
    selectObject(obj)
    selectWall({ roomId: obj.id, wall: wallDir, isLoadBearing })
  }

  const getWallColor = (wallDir: string) => {
    // 选中墙体高亮
    if (selectedWall?.roomId === obj.id && selectedWall?.wall === wallDir) {
      return wallDir === 'north' ? '#E53935' : '#4CAF50' // 红色=承重危险, 绿色=安全
    }
    if (hoveredWall === wallDir) return wallDir === 'north' ? '#EF5350' : '#66BB6A'
    return wallDir === 'north' ? '#D4A0A0' : wallColor
  }

  const getWallOpacity = (wallDir: string) => {
    if (selectedWall?.roomId === obj.id && selectedWall?.wall === wallDir) return 0.7
    if (hoveredWall === wallDir) return 0.55
    return wallOpacity
  }

  return (
    <group>
      {/* 地板（主点击区域） */}
      <mesh
        ref={meshRef}
        position={[floorX, 0.05, floorZ]}
        rotation={[-Math.PI / 2, 0, 0]}
        onClick={handleClick}
        onPointerEnter={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer' }}
        onPointerLeave={() => { setHovered(false); document.body.style.cursor = 'default' }}
        receiveShadow
      >
        <planeGeometry args={[width, depth]} />
        <meshStandardMaterial
          color={isSelected ? '#4CAF50' : hovered ? '#8BC34A' : baseColor}
          transparent
          opacity={0.85}
          roughness={0.8}
          metalness={0.1}
        />
      </mesh>

      {/* 地板边框 */}
      <lineSegments position={[floorX, 0.06, floorZ]}>
        <edgesGeometry args={[new THREE.BoxGeometry(width, 0.01, depth)]} />
        <lineBasicMaterial color={isSelected ? '#4CAF50' : hovered ? '#8BC34A' : '#888'} />
      </lineSegments>

      {/* 北墙（承重墙 - 红色高亮） */}
      <mesh
        position={[floorX, 1.4, cz]}
        onClick={(e) => handleWallClick('north', e)}
        onPointerEnter={(e) => { e.stopPropagation(); setHoveredWall('north'); document.body.style.cursor = 'pointer' }}
        onPointerLeave={() => { setHoveredWall(null); document.body.style.cursor = 'default' }}
        castShadow
      >
        <boxGeometry args={[width, 2.8, 0.12]} />
        <meshStandardMaterial color={getWallColor('north')} transparent opacity={getWallOpacity('north')} />
      </mesh>

      {/* 南墙 */}
      <mesh
        position={[floorX, 1.0, cz + depth]}
        onClick={(e) => handleWallClick('south', e)}
        onPointerEnter={(e) => { e.stopPropagation(); setHoveredWall('south'); document.body.style.cursor = 'pointer' }}
        onPointerLeave={() => { setHoveredWall(null); document.body.style.cursor = 'default' }}
        castShadow
      >
        <boxGeometry args={[width, 2.0, 0.12]} />
        <meshStandardMaterial color={getWallColor('south')} transparent opacity={getWallOpacity('south')} />
      </mesh>

      {/* 东墙 */}
      <mesh
        position={[cx + width, 1.4, floorZ]}
        onClick={(e) => handleWallClick('east', e)}
        onPointerEnter={(e) => { e.stopPropagation(); setHoveredWall('east'); document.body.style.cursor = 'pointer' }}
        onPointerLeave={() => { setHoveredWall(null); document.body.style.cursor = 'default' }}
        castShadow
      >
        <boxGeometry args={[0.12, 2.8, depth]} />
        <meshStandardMaterial color={getWallColor('east')} transparent opacity={getWallOpacity('east')} />
      </mesh>

      {/* 西墙 */}
      <mesh
        position={[cx, 1.4, floorZ]}
        onClick={(e) => handleWallClick('west', e)}
        onPointerEnter={(e) => { e.stopPropagation(); setHoveredWall('west'); document.body.style.cursor = 'pointer' }}
        onPointerLeave={() => { setHoveredWall(null); document.body.style.cursor = 'default' }}
        castShadow
      >
        <boxGeometry args={[0.12, 2.8, depth]} />
        <meshStandardMaterial color={getWallColor('west')} transparent opacity={getWallOpacity('west')} />
      </mesh>

      {/* 房间名称标签（选中时显示） */}
      {isSelected && (
        <mesh position={[floorX, 3.5, floorZ]}>
          <sphereGeometry args={[0.18, 12, 12]} />
          <meshStandardMaterial color="#F44336" emissive="#F44336" emissiveIntensity={0.8} />
        </mesh>
      )}

      {/* 物理标签 */}
      {showPhysics && isSelected && obj.vrData?.physics_tags?.map((tag, i) => (
        <mesh key={tag} position={[floorX + (i - 2) * 0.4, 3.8, floorZ]}>
          <sphereGeometry args={[0.08, 8, 8]} />
          <meshStandardMaterial color="#FF9800" emissive="#FF9800" emissiveIntensity={0.6} />
        </mesh>
      ))}
    </group>
  )
}

// ─── 停车位 ───
function ParkingSpot({ obj }: { obj: BuildingObject }) {
  const selectObject = useBuildingStore((s) => s.selectObject)
  const selectedObject = useBuildingStore((s) => s.selectedObject)
  const isSelected = selectedObject?.id === obj.id
  const [hovered, setHovered] = useState(false)

  return (
    <mesh
      position={[obj.position[0], 0.03, obj.position[2]]}
      rotation={[-Math.PI / 2, 0, obj.rotation[1]]}
      onClick={(e) => { e.stopPropagation(); selectObject(isSelected ? null : obj) }}
      onPointerEnter={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer' }}
      onPointerLeave={() => { setHovered(false); document.body.style.cursor = 'default' }}
    >
      <planeGeometry args={[obj.dimensions.width, obj.dimensions.depth]} />
      <meshStandardMaterial
        color={isSelected ? '#4CAF50' : hovered ? '#78909C' : '#546E7A'}
        transparent
        opacity={isSelected ? 0.9 : hovered ? 0.75 : 0.55}
        roughness={0.9}
      />
    </mesh>
  )
}

// ─── JEPA 世界模型可视化层 ───
function JEPALayer() {
  const { camera } = useThree()
  const objects = useBuildingStore((s) => s.objects)
  const selectedObject = useBuildingStore((s) => s.selectedObject)
  const showPaths = useBuildingStore((s) => s.showPaths)

  // 编码器：计算选中房间的特征向量（可视化）
  const encoded = useMemo(() => {
    if (!selectedObject) return null
    const cat = selectedObject.vrData?.room_category || '其他'
    const hash = cat.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
    return {
      x: (hash % 100) / 100 * 2 - 1,
      y: ((hash >> 4) % 100) / 100 * 2 - 1,
      z: ((hash >> 8) % 100) / 100 * 2 - 1,
    }
  }, [selectedObject])

  // 预测器：显示下一个可能状态的预测点
  const predicted = useMemo(() => {
    if (!encoded) return null
    return {
      x: encoded.x * 1.5,
      y: encoded.y * 1.5 + 3,
      z: encoded.z * 1.5,
    }
  }, [encoded])

  // 路径规划：显示从选中房间到预测点的轨迹
  const pathPoints = useMemo(() => {
    if (!selectedObject || !encoded) return []
    const start = selectedObject.position
    const end = [encoded.x * 15, 3, encoded.z * 15]
    return [
      new THREE.Vector3(start[0], 1.5, start[2]),
      new THREE.Vector3(...end),
    ]
  }, [selectedObject, encoded])

  if (!selectedObject || !showPaths) return null

  return (
    <group>
      {/* 编码器表示空间（抽象潜在空间可视化） */}
      <mesh position={[15, 5, 15]}>
        <boxGeometry args={[4, 4, 4]} />
        <meshStandardMaterial color="#1a1a3e" transparent opacity={0.3} wireframe />
      </mesh>

      {/* 当前状态（编码器输出） */}
      {encoded && (
        <mesh position={[15 + encoded.x * 1.5, 5 + encoded.y * 1.5, 15 + encoded.z * 1.5]}>
          <sphereGeometry args={[0.2, 16, 16]} />
          <meshStandardMaterial color="#4CAF50" emissive="#4CAF50" emissiveIntensity={0.8} />
        </mesh>
      )}

      {/* 预测状态（预测器输出） */}
      {predicted && (
        <>
          <mesh position={[15 + predicted.x, 5 + predicted.y, 15 + predicted.z]}>
            <sphereGeometry args={[0.15, 16, 16]} />
            <meshStandardMaterial color="#FF9800" emissive="#FF9800" emissiveIntensity={0.8} />
          </mesh>
          <lineSegments>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                array={new Float32Array([
                  15 + (encoded?.x ?? 0) * 1.5, 5 + (encoded?.y ?? 0) * 1.5, 15 + (encoded?.z ?? 0) * 1.5,
                  15 + (predicted?.x ?? 0), 5 + (predicted?.y ?? 0), 15 + (predicted?.z ?? 0),
                ])}
                count={2}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial color="#FF9800" opacity={0.6} transparent />
          </lineSegments>
        </>
      )}

      {/* 3D空间中的实际路径 */}
      {pathPoints.length === 2 && (
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              array={new Float32Array([
                ...pathPoints[0].toArray(),
                ...pathPoints[1].toArray(),
              ])}
              count={2}
              itemSize={3}
            />
          </bufferGeometry>
          <lineDashedMaterial color="#2196F3" dashSize={0.5} gapSize={0.3} />
        </line>
      )}
    </group>
  )
}

// ─── 场景统计HUD ───
function SceneHUD() {
  const objects = useBuildingStore((s) => s.objects)
  const activeScene = useBuildingStore((s) => s.activeScene)

  const rooms = objects.filter(o => !o.id.startsWith('parking-') && !o.id.startsWith('basement-'))
  const vrCount = new Set(rooms.map(r => r.vrData?.vr_id)).size
  const catCount = new Set(rooms.map(r => r.vrData?.room_category)).size

  return (
    <group position={[0, 0.1, 0]}>
      {/* 地面 */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[200, 200]} />
        <meshStandardMaterial color="#1a1a2e" />
      </mesh>

      {/* 网格 */}
      <gridHelper args={[200, 40, '#2a2a4e', '#1e1e3e']} position={[0, 0.05, 0]} />

      {/* 场景标签 */}
      <mesh position={[20, 0.1, -20]}>
        <planeGeometry args={[8, 2]} />
        <meshBasicMaterial color="#0a0a1a" transparent opacity={0.8} />
      </mesh>
    </group>
  )
}

// ─── 主场景 ───
export default function BuildingScene() {
  const objects = useBuildingStore((s) => s.objects)
  const selectObject = useBuildingStore((s) => s.selectObject)
  const showPaths = useBuildingStore((s) => s.showPaths)

  const rooms = useMemo(
    () => objects.filter((o) => !o.id.startsWith('parking-') && !o.id.startsWith('basement-')),
    [objects]
  )
  const parking = useMemo(
    () => objects.filter((o) => o.id.startsWith('parking-')),
    [objects]
  )

  // 背景点击取消选择
  const selectWall = useBuildingStore((s) => s.selectWall)

  const handleBackgroundClick = () => {
    selectObject(null)
    selectWall(null)
  }

  return (
    <group>
      <SceneHUD />

      {/* 点击背景取消选择 */}
      <mesh
        position={[0, -0.1, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        onClick={handleBackgroundClick}
      >
        <planeGeometry args={[500, 500]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>

      {/* 房间 */}
      {rooms.map((obj, i) => (
        <Room key={obj.id} obj={obj} index={i} />
      ))}

      {/* 停车位 */}
      {parking.map((obj) => (
        <ParkingSpot key={obj.id} obj={obj} />
      ))}

      {/* JEPA 世界模型可视化 */}
      <JEPALayer />
    </group>
  )
}
