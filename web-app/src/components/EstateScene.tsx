import { useRef, useMemo, useState, useEffect, useCallback } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { Html } from '@react-three/drei'
import { useBuildingStore } from '../store/buildingStore'

// ─── 类型定义 ─────────────────────────────
interface EstateNode {
  id: string
  type: string
  position: [number, number, number]
  label: string
  connections: string[]
}

interface EstateEdge {
  from: string
  to: string
  weight: number
  road_id: string
  type: string
}

interface EstateRoad {
  id: string
  name: string
  type: string
  width: number
  path: [number, number, number][]
  is_loop: boolean
}

interface EstateGreenSpace {
  id: string
  name: string
  center: [number, number, number]
  radius_m: number
  type: string
}

interface EstateObstacle {
  id: string
  type: string
  shape: string
  center?: [number, number, number]
  radius?: number
  points?: [number, number, number][]
  reason: string
}

interface PatrolRoute {
  id: string
  name: string
  nodes: string[]
}

interface EstateTopology {
  project: Record<string, any>
  bounds: Record<string, number>
  zones: any[]
  roads: EstateRoad[]
  green_spaces: EstateGreenSpace[]
  entrances: any[]
  nodes: EstateNode[]
  edges: EstateEdge[]
  obstacles: EstateObstacle[]
  patrol_routes: PatrolRoute[]
  robot_config?: Record<string, any>
}

// ─── 颜色常量 ─────────────────────────────
const COLORS = {
  building: '#4A90D9',      // 蓝色 - 楼栋
  road_main: '#666666',     // 深灰 - 主路
  road_branch: '#888888',   // 浅灰 - 支路
  green: '#2E8B57',         // 绿色 - 绿化
  danger: '#E53935',        // 红色 - 危险/禁行区
  entrance: '#FFA500',      // 橙色 - 入口
  node: '#00BCD4',          // 青色 - 节点
  patrol: '#FFEB3B',       // 黄色 - 巡逻路线
  robot: '#E91E63',         // 粉红 - 机器人
  selected: '#FFFFFF',      // 白色 - 选中高亮
  text: '#CCCCCC',          // 浅灰 - 文字
}

// ─── 工具函数：生成圆弧路径点 ──────────────
function generateArcPath(
  points: [number, number, number][],
  segments: number = 32
): [number, number, number][] {
  if (points.length < 2) return points

  const result: [number, number, number][] = []
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i]
    const p1 = points[i + 1]
    for (let t = 0; t <= 1; t += 1 / segments) {
      result.push([
        p0[0] + (p1[0] - p0[0]) * t,
        p0[1] + (p1[1] - p0[1]) * t,
        p0[2] + (p1[2] - p0[2]) * t,
      ])
    }
  }
  // 如果是环路，闭合
  if (points.length > 2) {
    const last = points[points.length - 1]
    const first = points[0]
    for (let t = 0.01; t <= 1; t += 1 / segments) {
      result.push([
        last[0] + (first[0] - last[0]) * t,
        last[1] + (first[1] - last[1]) * t,
        last[2] + (first[2] - last[2]) * t,
      ])
    }
  }
  return result
}

// ─── 道路线框组件 ─────────────────────────
function RoadLine({ road }: { road: EstateRoad }) {
  const lineRef = useRef<THREE.LineSegments>(null)
  const [hovered, setHovered] = useState(false)

  const isMain = road.type === 'main_road'
  const color = isMain ? COLORS.road_main : COLORS.road_branch
  const lineWidth = isMain ? 2.5 : 1.5

  const geometry = useMemo(() => {
    const pts = generateArcPath(road.path, 24)
    const positions: number[] = []
    const hw = road.width / 2

    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = new THREE.Vector3(...pts[i])
      const p1 = new THREE.Vector3(...pts[i + 1])
      const dir = new THREE.Vector3().subVectors(p1, p0).normalize()
      const perp = new THREE.Vector3(-dir.z, 0, dir.x).normalize()

      // 左边缘
      positions.push(
        p0.x + perp.x * hw, 0.15, p0.z + perp.z * hw,
        p1.x + perp.x * hw, 0.15, p1.z + perp.z * hw,
      )
      // 右边缘
      positions.push(
        p0.x - perp.x * hw, 0.15, p0.z - perp.z * hw,
        p1.x - perp.x * hw, 0.15, p1.z - perp.z * hw,
      )
      // 中心虚线（每隔一段）
      if (i % 4 === 0) {
        positions.push(p0.x, 0.16, p0.z, p1.x, 0.16, p1.z)
      }
    }

    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    return geo
  }, [road.path, road.width])

  useFrame((state) => {
    if (!lineRef.current) return
    const mat = lineRef.current.material as THREE.LineBasicMaterial
    mat.opacity = hovered ? 1.0 : 0.7
  })

  return (
    <lineSegments ref={lineRef} geometry={geometry}>
      <lineBasicMaterial
        color={color}
        transparent
        opacity={0.7}
        linewidth={lineWidth}
      />
      <mesh
        visible={false}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[road.width * 1.5, 0.5, road.width * 1.5]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
    </lineSegments>
  )
}

// ─── 绿化区域组件（椭圆线框）───────────────
function GreenArea({ green }: { green: EstateGreenSpace }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  const segments = 48
  const geometry = useMemo(() => {
    const pts: [number, number, number][] = []
    const rx = green.radius_m
    const rz = green.radius_m * 0.75 // 略扁的椭圆更自然
    for (let i = 0; i <= segments; i++) {
      const angle = (i / segments) * Math.PI * 2
      pts.push([
        green.center[0] + Math.cos(angle) * rx,
        0.08,
        green.center[2] + Math.sin(angle) * rz,
      ])
    }

    const positions: number[] = []
    for (let i = 0; i < pts.length - 1; i++) {
      positions.push(pts[i][0], pts[i][1], pts[i][2])
      positions.push(pts[i + 1][0], pts[i + 1][1], pts[i + 1][2])
    }

    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    return geo
  }, [green.center, green.radius_m])

  // 内部十字交叉线
  const innerLines = useMemo(() => {
    const r = green.radius_m * 0.6
    const cx = green.center[0]
    const cz = green.center[2]
    return [
      [cx - r, 0.09, cz - r * 0.75, cx + r, 0.09, cz + r * 0.75],
      [cx - r, 0.09, cz + r * 0.75, cx + r, 0.09, cz - r * 0.75],
    ]
  }, [green.center, green.radius_m])

  useFrame(() => {
    if (!meshRef.current) return
    const scale = hovered ? 1.02 : 1
    meshRef.current.scale.lerp(new THREE.Vector3(scale, 1, scale), 0.1)
  })

  return (
    <group>
      {/* 外圈 */}
      <lineSegments geometry={geometry}>
        <lineBasicMaterial color={COLORS.green} transparent opacity={0.6} />
      </lineSegments>
      {/* 内部装饰线 */}
      {innerLines.map((pts, idx) => (
        <lineSegments key={idx}>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={2}
              array={new Float32Array(pts)}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color={COLORS.green} transparent opacity={0.25} />
        </lineSegments>
      ))}
      {/* 热区检测 */}
      <mesh
        ref={meshRef}
        position={[green.center[0], 0.05, green.center[2]]}
        visible={false}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <circleGeometry args={[green.radius_m, 32]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
    </group>
  )
}

// ─── 入口标记组件 ─────────────────────────
function EntranceMarker({ entrance }: { entrance: any }) {
  const groupRef = useRef<THREE.Group>(null)
  const [hovered, setHovered] = useState(false)

  const pos = entrance.position as [number, number, number]

  useFrame(({ clock }) => {
    if (!groupRef.current) return
    groupRef.current.rotation.y = clock.elapsedTime * 0.5
    const s = hovered ? 1.3 : 1.0
    groupRef.current.scale.setScalar(THREE.MathUtils.lerp(groupRef.current.scale.x, s, 0.1))
  })

  // 入口拱门形状（线框）
  const archHeight = 6
  const archWidth = 8
  const archPts = [
    [-archWidth/2, 0, 0, -archWidth/2, archHeight, 0],
    [-archWidth/2, archHeight, 0, archWidth/2, archHeight, 0],
    [archWidth/2, archHeight, 0, archWidth/2, 0, 0],
    // 斜撑
    [-archWidth/2, 0, 0, -archWidth/2-2, archHeight*0.6, 0],
    [archWidth/2, 0, 0, archWidth/2+2, archHeight*0.6, 0],
  ]

  return (
    <group ref={groupRef} position={pos}>
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={archPts.length / 3}
            array={new Float32Array(archPts.flat())}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color={COLORS.entrance} transparent opacity={hovered ? 1 : 0.8} />
      </lineSegments>
      {/* 地面标记圆 */}
      <lineSegments>
        <ringGeometry args={[3, 4, 6]} />
        <lineBasicMaterial color={COLORS.entrance} transparent opacity={0.5} side={THREE.DoubleSide} />
      </lineSegments>
      <mesh visible={false} onPointerOver={() => setHovered(true)} onPointerOut={() => setHovered(false)}>
        <boxGeometry args={[12, archHeight+2, 6]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
      {hovered && (
        <Html distanceFactor={15} center position={[0, archHeight + 2, 0]}>
          <div style={{
            background: 'rgba(0,0,0,0.8)',
            color: COLORS.entrance,
            padding: '4px 10px',
            borderRadius: 4,
            fontSize: 11,
            whiteSpace: 'nowrap',
            pointerEvents: 'none',
            border: `1px solid ${COLORS.entrance}`,
          }}>
            {entrance.name}
          </div>
        </Html>
      )}
    </group>
  )
}

// ─── 节点标记组件 ─────────────────────────
function NodeMarker({ node, isSelected, onSelect }: {
  node: EstateNode
  isSelected: boolean
  onSelect: (id: string | null) => void
}) {
  const sphereRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  const isEntrance = node.type === 'entrance'
  const isJunction = node.type === 'road_junction'
  const isFacility = node.type === 'facility'

  let color = COLORS.node
  if (isEntrance) color = COLORS.entrance
  else if (isJunction) color = '#9C27B0' // 紫色路口
  else if (isFacility) color = COLORS.green

  useFrame(({ clock }) => {
    if (!sphereRef.current) return
    const pulse = Math.sin(clock.elapsedTime * 2) * 0.08 + 1
    const targetScale = (isSelected || hovered) ? pulse * 1.5 : pulse * 0.8
    sphereRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.12)
  })

  return (
    <group position={node.position}>
      <mesh
        ref={sphereRef}
        onClick={(e) => { e.stopPropagation(); onSelect(isSelected ? null : node.id) }}
        onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer' }}
        onPointerOut={() => { setHovered(false); document.body.style.cursor = 'default' }}
      >
        <octahedronGeometry args={[isEntrance ? 1.2 : isJunction ? 0.8 : 0.6, 0]} />
        <meshStandardMaterial
          color={isSelected ? COLORS.selected : color}
          emissive={color}
          emissiveIntensity={isSelected || hovered ? 0.6 : 0.2}
          wireframe
          transparent
          opacity={0.85}
        />
      </mesh>
      {(isSelected || hovered) && (
        <Html distanceFactor={20} center position={[0, 3, 0]}>
          <div style={{
            background: 'rgba(0,0,0,0.85)',
            color: '#fff',
            padding: '6px 12px',
            borderRadius: 6,
            fontSize: 11,
            whiteSpace: 'nowrap',
            pointerEvents: 'none',
            border: `1px solid ${color}`,
            maxWidth: 200,
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: 2 }}>{node.label}</div>
            <div style={{ fontSize: 9, color: '#aaa' }}>ID: {node.id} | Type: {node.type}</div>
            <div style={{ fontSize: 9, color: '#aaa' }}>Connections: {node.connections.length}</div>
          </div>
        </Html>
      )}
    </group>
  )
}

// ─── 障碍物/禁行区组件 ─────────────────────
function ObstacleZone({ obs }: { obs: EstateObstacle }) {
  const isDanger = obs.type === 'no_go_zone'
  const color = isDanger ? COLORS.danger : '#FF5722' // 深橙=限制区

  if (obs.shape === 'circle' && obs.center && obs.radius) {
    const pts: number[] = []
    const segs = 32
    for (let i = 0; i <= segs; i++) {
      const a = (i / segs) * Math.PI * 2
      pts.push(
        obs.center[0] + Math.cos(a) * obs.radius, 0.2,
        obs.center[2] + Math.sin(a) * obs.radius,
      )
      if (i < segs) {
        pts.push(
          obs.center[0] + Math.cos(a + (i+1)*(Math.PI*2/segs)) * obs.radius, 0.2,
          obs.center[2] + Math.sin(a + (i+1)*(Math.PI*2/segs)) * obs.radius,
        )
      }
    }
    return (
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={segs + 1}
            array={new Float32Array(pts)}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial
          color={color}
          transparent
          opacity={isDanger ? 0.7 : 0.4}
          dashed={isDanger}
          dashSize={2}
          gapSize={1}
        />
      </lineSegments>
    )
  }

  if (obs.shape === 'polygon' && obs.points && obs.points.length > 0) {
    const pts: number[] = []
    const ptsArr = obs.points
    for (let i = 0; i < ptsArr.length; i++) {
      const next = ptsArr[(i + 1) % ptsArr.length]
      pts.push(ptsArr[i][0], 0.2, ptsArr[i][2], next[0], 0.2, next[2])
    }
    return (
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={ptsArr.length * 2}
            array={new Float32Array(pts)}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial
          color={color}
          transparent
          opacity={isDanger ? 0.65 : 0.35}
          dashed={isDanger}
          dashSize={3}
          gapSize={1.5}
        />
      </lineSegments>
    )
  }

  if (obs.shape === 'polyline' && obs.points) {
    const pts: number[] = []
    for (let i = 0; i < obs.points.length - 1; i++) {
      pts.push(obs.points[i][0], 0.25, obs.points[i][2])
      pts.push(obs.points[i+1][0], 0.25, obs.points[i+1][2])
    }
    return (
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={(obs.points.length - 1) * 2}
            array={new Float32Array(pts)}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#555555" transparent opacity={0.3} />
      </lineSegments>
    )
  }

  return null
}

// ─── 巡逻路线可视化组件 ────────────────────
function PatrolRouteLine({
  route,
  nodesMap,
  isActive,
}: {
  route: PatrolRoute
  nodesMap: Map<string, EstateNode>
  isActive: boolean
}) {
  const lineRef = useRef<THREE.Line>(null)
  const dashOffset = useRef(0)

  const points = useMemo(() => {
    const pts: [number, number, number][] = []
    for (const nid of route.nodes) {
      const n = nodesMap.get(nid)
      if (n) pts.push(n.position)
    }
    return pts
  }, [route.nodes, nodesMap])

  const geometry = useMemo(() => {
    if (points.length < 2) return null
    const pos: number[] = []
    for (let i = 0; i < points.length - 1; i++) {
      pos.push(points[i][0], 0.5, points[i][2])
      pos.push(points[i+1][0], 0.5, points[i+1][2])
    }
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3))
    return geo
  }, [points])

  useFrame((_, delta) => {
    if (!lineRef.current || !isActive) return
    dashOffset.current += delta * 10
    const mat = lineRef.current.material as THREE.LineDashedMaterial
    mat.dashOffset = dashOffset.current
  })

  if (!geometry) return null

  return (
    <line ref={lineRef} geometry={geometry}>
      <lineDashedMaterial
        color={COLORS.patrol}
        transparent
        opacity={isActive ? 0.9 : 0.3}
        dashSize={4}
        gapSize={2}
      />
      {lineRef.current?.computeLineDistances?.()}
    </line>
  )
}

// ─── 机器人胶囊体组件 ──────────────────────
function RobotAgent({
  position,
  targetPosition,
  isMoving,
}: {
  position: [number, number, number]
  targetPosition: [number, number, number]
  isMoving: boolean
}) {
  const groupRef = useRef<THREE.Group>(null)
  const bodyRef = useRef<THREE.Mesh>(null)

  useFrame((state, delta) => {
    if (!groupRef.current || !bodyRef.current) return

    // 平滑移动到目标位置
    groupRef.current.position.x = THREE.MathUtils.lerp(groupRef.current.position.x, targetPosition[0], 0.03)
    groupRef.current.position.y = THREE.MathUtils.lerp(groupRef.current.position.y, targetPosition[1] + 0.9, 0.03)
    groupRef.current.position.z = THREE.MathUtils.lerp(groupRef.current.position.z, targetPosition[2], 0.03)

    // 面向目标方向
    if (isMoving) {
      const dx = targetPosition[0] - groupRef.current.position.x
      const dz = targetPosition[2] - groupRef.current.position.z
      if (Math.abs(dx) > 0.1 || Math.abs(dz) > 0.1) {
        const angle = Math.atan2(dx, dz)
        groupRef.current.rotation.y = THREE.MathUtils.lerpAngle(groupRef.current.rotation.y, angle, 0.05)
      }
    }

    // 悬浮动画
    const floatY = Math.sin(state.clock.elapsedTime * 2) * 0.05
    bodyRef.current.position.y = floatY

    // 移动时发光增强
    const mat = bodyRef.current.material as THREE.MeshStandardMaterial
    mat.emissiveIntensity = isMoving ? 0.8 : 0.3
  })

  return (
    <group ref={groupRef} position={position}>
      {/* 身体（胶囊体用圆柱+球模拟） */}
      <mesh ref={bodyRef} position={[0, 0.45, 0]} castShadow>
        <capsuleGeometry args={[0.25, 0.5, 4, 8]} />
        <meshStandardMaterial
          color={COLORS.robot}
          emissive={COLORS.robot}
          emissiveIntensity={0.3}
          wireframe
          transparent
          opacity={0.9}
        />
      </mesh>
      {/* 方向指示器 */}
      <mesh position={[0, 0.45, 0.35]}>
        <coneGeometry args={[0.1, 0.25, 4]} />
        <meshStandardMaterial color={COLORS.robot} emissive={COLORS.robot} emissiveIntensity={0.5} wireframe />
      </mesh>
      {/* 底部光环 */}
      <mesh position={[0, 0.02, 0]} rotation={[-Math.PI/2, 0, 0]}>
        <ringGeometry args={[0.4, 0.55, 16]} />
        <meshBasicMaterial color={COLORS.robot} transparent opacity={0.3} side={THREE.DoubleSide} />
      </mesh>
    </group>
  )
}

// ─── 组团建筑群（参数化生成）────────────────
function ZoneBuildings({ zone }: { zone: any }) {
  const groupRef = useRef<THREE.Group>(null)

  // 根据组团信息参数化生成别墅位置
  const buildings = useMemo(() => {
    const result: Array<{
      id: string
      pos: [number, number, number]
      rotation: number
      houseType: string
    }> = []

    const cx = zone.center[0]
    const cy = zone.center[2]
    const count = zone.building_count

    if (zone.id === 'zone_a') {
      // 北部组团：沿弧形排列
      for (let i = 0; i < count; i++) {
        const t = i / (count - 1)
        const angle = -Math.PI * 0.15 + t * Math.PI * 0.3
        const r = 80 + Math.sin(t * Math.PI) * 40
        result.push({
          id: `b_a_${i}`,
          pos: [cx + Math.sin(angle) * r, 0, cy + 100 - Math.cos(angle) * r * 0.6],
          rotation: angle + Math.PI / 2,
          houseType: i % 2 === 0 ? 'B-1' : 'B-2',
        })
      }
    } else if (zone.id === 'zone_b') {
      // 中部核心组团：弧形+放射状
      const rows = 5
      const perRow = Math.ceil(count / rows)
      let idx = 0
      for (let row = 0; row < rows && idx < count; row++) {
        const rowRadius = 40 + row * 22
        const countInRow = perRow - row
        const startAngle = -Math.PI * 0.45
        const endAngle = Math.PI * 0.45
        for (let col = 0; col < countInRow && idx < count; col++) {
          const t = countInRow > 1 ? col / (countInRow - 1) : 0.5
          const angle = startAngle + t * (endAngle - startAngle)
          result.push({
            id: `b_b_${idx}`,
            pos: [cx + Math.sin(angle) * rowRadius, 0, cy + Math.cos(angle) * rowRadius * 0.85],
            rotation: -angle,
            houseType: idx % 2 === 0 ? 'B-1' : 'B-2',
          })
          idx++
        }
      }
    } else if (zone.id === 'zone_c') {
      // 南部组团：网格偏移排列
      const cols = 5
      const rows = Math.ceil(count / cols)
      let idx = 0
      for (let r = 0; r < rows && idx < count; r++) {
        for (let c = 0; c < cols && idx < count; c++) {
          const offset_x = (r % 2) * 12
          result.push({
            id: `b_c_${idx}`,
            pos: [cx - 60 + c * 18 + offset_x, 0, cy - 30 + r * 20],
            rotation: 0,
            houseType: idx < 14 ? (idx % 2 === 0 ? 'B-1' : 'B-2') : (idx % 2 === 0 ? 'C-1' : 'C-2'),
          })
          idx++
        }
      }
    } else if (zone.id === 'zone_d') {
      // 东部边缘：单列弧形
      for (let i = 0; i < count; i++) {
        const t = i / (count - 1)
        const angle = Math.PI * 0.2 + t * Math.PI * 0.5
        const r = 140
        result.push({
          id: `b_d_${i}`,
          pos: [cx + Math.cos(angle) * r, 0, cy + Math.sin(angle) * r * 0.7],
          rotation: -angle + Math.PI / 2,
          houseType: i % 2 === 0 ? 'B-1' : 'B-2',
        })
      }
    }

    return result
  }, [zone])

  return (
    <group ref={groupRef}>
      {buildings.map((b) => (
        <VillaWireframe key={b.id} {...b} />
      ))}
    </group>
  )
}

// ─── 单栋别墅线框 ──────────────────────────
function VillaWireframe({
  id,
  pos,
  rotation,
  houseType,
}: {
  id: string
  pos: [number, number, number]
  rotation: number
  houseType: string
}) {
  const groupRef = useRef<THREE.Group>(null)
  const [hovered, setHovered] = useState(false)
  const selectObject = useBuildingStore(s => s.selectObject)
  const selectedObject = useBuildingStore(s => s.selectedObject)
  const isSelected = selectedObject?.id === id

  // B型3层，C型2层
  const floors = houseType.startsWith('C') ? 2 : 3
  const floorHeight = 3.3
  const width = 9
  const depth = 13

  useFrame(({ clock }) => {
    if (!groupRef.current) return
    const t = clock.elapsedTime
    const targetY = isSelected ? 0.5 : hovered ? 0.2 : 0
    groupRef.current.position.y = THREE.MathUtils.lerp(
      groupRef.current.position.y, targetY + Math.sin(t * 1.2 + parseFloat(id.slice(-2))) * 0.03, 0.08
    )
  })

  // 生成每层的线框边
  const floorLines = useMemo(() => {
    const allLines: Array<{ key: string; pts: number[] }> = []
    const hw = width / 2
    const hd = depth / 2

    for (let f = 0; f < floors; f++) {
      const y = f * floorHeight
      const baseKey = `${id}_f${f}`

      // 地板矩形
      allLines.push({
        key: `${baseKey}_floor`,
        pts: [
          -hw, y, -hd, hw, y, -hd,
          hw, y, -hd, hw, y, hd,
          hw, y, hd, -hw, y, hd,
          -hw, y, hd, -hw, y, -hd,
        ],
      })

      // 天花板矩形
      const cy = y + floorHeight
      allLines.push({
        key: `${baseKey}_ceil`,
        pts: [
          -hw, cy, -hd, hw, cy, -hd,
          hw, cy, -hd, hw, cy, hd,
          hw, cy, hd, -hw, cy, hd,
          -hw, cy, hd, -hw, cy, -hd,
        ],
      })

      // 立柱（四角）
      const corners = [[-hw, -hd], [hw, -hd], [hw, hd], [-hw, hd]]
      for (const [x, z] of corners) {
        allLines.push({
          key: `${baseKey}_col_${x}_${z}`,
          pts: [x, y, z, x, cy, z],
        })
      }

      // 屋顶坡度线（顶层）
      if (f === floors - 1) {
        const ridgeY = cy + 2.5
        allLines.push({
          key: `${baseKey}_roof1`,
          pts: [-hw, cy, -hd, 0, ridgeY, 0, hw, cy, -hd],
        })
        allLines.push({
          key: `${baseKey}_roof2`,
          pts: [-hw, cy, hd, 0, ridgeY, 0, hw, cy, hd],
        })
      }
    }

    return allLines
  }, [floors, id])

  return (
    <group
      ref={groupRef}
      position={pos}
      rotation={[0, rotation, 0]}
      onClick={(e) => { e.stopPropagation(); selectObject(isSelected ? null : { id, name: `${houseType} (${id})`, type: 'building' } as any) }}
      onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer' }}
      onPointerOut={() => { setHovered(false); document.body.style.cursor = 'default' }}
    >
      {floorLines.map(fl => (
        <lineSegments key={fl.key}>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={fl.pts.length / 3}
              array={new Float32Array(fl.pts)}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial
            color={isSelected ? COLORS.selected : COLORS.building}
            transparent
            opacity={isSelected ? 1 : (hovered ? 0.9 : 0.55)}
            linewidth={isSelected ? 2 : 1}
          />
        </lineSegments>
      ))}
      {(isSelected || hovered) && (
        <Html distanceFactor={25} center position={[0, floors * floorHeight + 3, 0]}>
          <div style={{
            background: 'rgba(30,60,120,0.9)',
            color: '#fff',
            padding: '6px 10px',
            borderRadius: 6,
            fontSize: 10,
            whiteSpace: 'nowrap',
            pointerEvents: 'none',
            border: '1px solid #4A90D9',
          }}>
            <div style={{ fontWeight: 'bold' }}>{id}</div>
            <div>{houseType} · {floors}层</div>
            <div>{width}m × {depth}m</div>
          </div>
        </Html>
      )}
    </group>
  )
}

// ─── 边界线组件 ───────────────────────────
function BoundaryLine() {
  const bounds = {
    minX: -220, maxX: 240,
    minY: -180, maxY: 160,
  }

  const pts = [
    bounds.minX, 0.3, bounds.maxY, bounds.maxX, 0.3, bounds.maxY,
    bounds.maxX, 0.3, bounds.maxY, bounds.maxX, 0.3, bounds.minY,
    bounds.maxX, 0.3, bounds.minY, bounds.minX, 0.3, bounds.minY,
    bounds.minX, 0.3, bounds.minY, bounds.minX, 0.3, bounds.maxY,
  ]

  return (
    <lineSegments>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={8}
          array={new Float32Array(pts)}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial color="#444444" transparent opacity={0.3} />
    </lineSegments>
  )
}

// ═══════════════════════════════════════════
// ║           主场景组件                     ║
// ═══════════════════════════════════════════
export default function EstateScene() {
  const [topology, setTopology] = useState<EstateTopology | null>(null)
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [activePatrolId, setActivePatrolId] = useState<string | null>('patrol_outer_ring')
  const [robotPos, setRobotPos] = useState<[number, number, number]>([0, 0, 0])
  const [robotTarget, setRobotTarget] = useState<[number, number, number]>([0, 0, 0])
  const [robotMoving, setRobotMoving] = useState(false)

  // 加载拓扑数据
  useEffect(() => {
    fetch('/data/estate_topology.json')
      .then(r => r.json())
      .then(setTopology)
      .catch(() => {
        // fallback: 如果fetch失败，使用内联数据（开发模式）
        console.log('EstateScene: using inline topology data')
      })
  }, [])

  // 节点映射
  const nodesMap = useMemo(() => {
    if (!topology) return new Map<string, EstateNode>()
    const map = new Map<string, EstateNode>()
    topology.nodes.forEach(n => map.set(n.id, n))
    return map
  }, [topology])

  // 点击节点时机器人导航过去
  const handleNodeSelect = useCallback((nid: string | null) => {
    setSelectedNodeId(nid)
    if (nid && topology) {
      const node = topology.nodes.find(n => n.id === nid)
      if (node) {
        setRobotTarget(node.position)
        setRobotMoving(true)
        setTimeout(() => setRobotMoving(false), 3000)
      }
    }
  }, [topology])

  if (!topology) {
    return (
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="#333" wireframe />
      </mesh>
    )
  }

  return (
    <group>
      {/* ── 地面网格 ── */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[500, 350]} />
        <meshStandardMaterial color="#0a0a12" transparent opacity={0.6} />
      </mesh>

      {/* ── 边界线 ── */}
      <BoundaryLine />

      {/* ── 道路网络 ── */}
      {topology.roads.map(road => (
        <RoadLine key={road.id} road={road} />
      ))}

      {/* ── 绿化区域 ── */}
      {topology.green_spaces.map(green => (
        <GreenArea key={green.id} green={green} />
      ))}

      {/* ── 入口标记 ── */}
      {topology.entrances.map(ent => (
        <EntranceMarker key={ent.id} entrance={ent} />
      ))}

      {/* ── 建筑群（按组团） ── */}
      {topology.zones.map(zone => (
        <ZoneBuildings key={zone.id} zone={zone} />
      ))}

      {/* ── 路径节点 ── */}
      {topology.nodes.map(node => (
        <NodeMarker
          key={node.id}
          node={node}
          isSelected={selectedNodeId === node.id}
          onSelect={handleNodeSelect}
        />
      ))}

      {/* ── 障碍物/禁行区 ── */}
      {topology.obstacles.filter(o => o.shape !== 'polyline').map(obs => (
        <ObstacleZone key={obs.id} obs={obs} />
      ))}

      {/* ── 边界线障碍物 ── */}
      {topology.obstacles.filter(o => o.shape === 'polyline').map(obs => (
        <ObstacleZone key={obs.id} obs={obs} />
      ))}

      {/* ── 巡逻路线 ── */}
      {topology.patrol_routes.map(route => (
        <PatrolRouteLine
          key={route.id}
          route={route}
          nodesMap={nodesMap}
          isActive={activePatrolId === route.id}
        />
      ))}

      {/* ── 机器人 Agent ── */}
      <RobotAgent
        position={robotPos}
        targetPosition={robotTarget}
        isMoving={robotMoving}
      />

      {/* ── 图例面板（HTML overlay） ── */}
      <Html position={[210, 80, 0]} distanceFactor={30}>
        <div style={{
          background: 'rgba(6,6,18,0.92)',
          border: '1px solid #333',
          borderRadius: 8,
          padding: '10px 14px',
          color: '#ccc',
          fontSize: 10,
          lineHeight: 1.8,
          pointerEvents: 'auto',
          minWidth: 130,
        }}>
          <div style={{ fontWeight: 'bold', color: '#fff', marginBottom: 6, fontSize: 11 }}>
            小区拓扑 · 图例
          </div>
          {[
            ['■', COLORS.building, '别墅楼栋'],
            ['━', COLORS.road_main, '主干道(6-7m)'],
            ['━', COLORS.road_branch, '支路(4.5m)'],
            ['○', COLORS.green, '绿化景观'],
            ['◆', COLORS.entrance, '出入口'],
            ['●', COLORS.node, '道路节点'],
            ['╌', COLORS.patrol, '巡逻路线'],
            ['✕', COLORS.danger, '禁行区域'],
            ['◈', COLORS.robot, '机器人'],
          ].map(([sym, color, label]) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ color, fontWeight: 'bold', width: 14 }}>{sym}</span>
              <span>{label}</span>
            </div>
          ))}
          <hr style={{ borderColor: '#333', margin: '6px 0' }} />
          <div style={{ fontSize: 9, color: '#888' }}>
            点击节点 → 机器人导航<br/>
            点击楼栋 → 查看户型信息
          </div>
        </div>
      </Html>

      {/* ── 标题标签 ── */}
      <Html position={[0, 95, 0]} center distanceFactor={40}>
        <div style={{
          background: 'rgba(74,144,217,0.15)',
          border: '1px solid rgba(74,144,217,0.4)',
          borderRadius: 6,
          padding: '4px 16px',
          color: '#4A90D9',
          fontSize: 13,
          fontWeight: 'bold',
          letterSpacing: 2,
          whiteSpace: 'nowrap',
          pointerEvents: 'none',
        }}>
          小区拓扑 · 具身AI导航
        </div>
      </Html>
    </group>
  )
}
