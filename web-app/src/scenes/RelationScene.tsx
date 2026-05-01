/**
 * RelationScene.tsx
 *
 * 空间关系3D场景
 *
 * 151个门/窗对象沿墙面排列：
 *   - Z = -3m（墙面位置）
 *   - Y = 0.8~1.05m（门把手高度）
 *   - X = 0~300m（沿墙分布）
 *
 * 功能：
 * 1. 3D 渲染门/窗对象（可点击选择）
 * 2. 空间关系可视化（选中对象 → 显示与其他对象的关系线）
 * 3. 颜色编码：同房间=绿线，不同房间=红线
 */

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { useThree } from '@react-three/fiber'
import { Html, Line, Text } from '@react-three/drei'
import * as THREE from 'three'
import './RelationScene.css'

// ════════════════════════════════════════════════
//  类型
// ════════════════════════════════════════════════

export interface DoorObject {
  id: number
  name: string
  type: 'door' | 'window'
  position: [number, number, number]  // [X, Y, Z]
  dimensions: { width: number; height: number; depth: number }
  color: string
}

export interface RelationEdge {
  source: number
  target: number
  relation: 'same_room' | 'diff_room'
  distance: number
  probability: number
}

interface Props {
  selectedId?: number
  onSelect?: (id: number) => void
  relations?: RelationEdge[]
  showRelations?: boolean
}

// ════════════════════════════════════════════════
//  门/窗尺寸模板
// ════════════════════════════════════════════════

const DOOR_TEMPLATES = {
  standard: { width: 0.9, height: 2.1, depth: 0.08, color: '#8B6914' },
  double: { width: 1.5, height: 2.1, depth: 0.08, color: '#9B7B1A' },
  security: { width: 0.86, height: 2.05, depth: 0.07, color: '#5C4033' },
  sliding: { width: 1.8, height: 2.1, depth: 0.05, color: '#A0826D' },
}

const WINDOW_TEMPLATES = {
  single: { width: 1.2, height: 1.5, depth: 0.05, color: '#87CEEB' },
  double: { width: 1.8, height: 1.5, depth: 0.05, color: '#ADD8E6' },
  french: { width: 2.4, height: 2.1, depth: 0.05, color: '#B0E0E6' },
}

// ════════════════════════════════════════════════
//  生成151个门/窗对象
// ════════════════════════════════════════════════

function generateDoors(): DoorObject[] {
  const objects: DoorObject[] = []
  // 135门 + 16窗，X从0到300米均匀分布
  for (let i = 0; i < 151; i++) {
    const x = (i / 150) * 300  // 0~300m
    const isDoor = i < 135
    const isDouble = i % 4 === 0  // 每4个有1个双开门

    if (isDoor) {
      const tpl = isDouble ? DOOR_TEMPLATES.double : DOOR_TEMPLATES.standard
      objects.push({
        id: i,
        name: `门-${i.toString().padStart(3, '0')}`,
        type: 'door',
        position: [x, tpl.height / 2, -3],
        dimensions: { ...tpl },
        color: tpl.color,
      })
    } else {
      const winTypes = Object.values(WINDOW_TEMPLATES)
      const tpl = winTypes[i % winTypes.length]
      objects.push({
        id: i,
        name: `窗-${i.toString().padStart(3, '0')}`,
        type: 'window',
        position: [x, 1.2, -3],
        dimensions: { ...tpl },
        color: tpl.color,
      })
    }
  }
  return objects
}

// ════════════════════════════════════════════════
//  关系推理（前端本地计算）
// ════════════════════════════════════════════════

function computeRelations(objects: DoorObject[], thresholdClose = 5.0, thresholdFar = 10.0): RelationEdge[] {
  const edges: RelationEdge[] = []
  for (let i = 0; i < objects.length; i++) {
    for (let j = i + 1; j < objects.length; j++) {
      const pi = objects[i].position
      const pj = objects[j].position
      const dist = Math.sqrt(
        (pi[0] - pj[0]) ** 2 +
        (pi[1] - pj[1]) ** 2 +
        (pi[2] - pj[2]) ** 2
      )
      if (dist < thresholdFar) {
        const isSame = dist < thresholdClose
        edges.push({
          source: i,
          target: j,
          relation: isSame ? 'same_room' : 'diff_room',
          distance: dist,
          probability: isSame ? 0.99 : 0.01,
        })
      }
    }
  }
  return edges
}

// ════════════════════════════════════════════════
//  单个门对象
// ════════════════════════════════════════════════

function DoorMesh({ obj, isSelected, onClick }: {
  obj: DoorObject
  isSelected: boolean
  onClick: () => void
}) {
  const meshRef = useRef<THREE.Mesh>(null)

  const color = isSelected
    ? obj.type === 'door' ? '#FFD700' : '#00FFFF'
    : obj.color

  const emissive = isSelected ? '#FFD700' : '#000000'
  const emissiveIntensity = isSelected ? 0.4 : 0

  return (
    <group position={obj.position}>
      {/* 门框 */}
      <mesh
        ref={meshRef}
        onClick={onClick}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[
          obj.dimensions.width,
          obj.dimensions.height,
          obj.dimensions.depth,
        ]} />
        <meshStandardMaterial
          color={color}
          metalness={obj.type === 'door' ? 0.1 : 0.6}
          roughness={obj.type === 'door' ? 0.8 : 0.2}
          emissive={emissive}
          emissiveIntensity={emissiveIntensity}
        />
      </mesh>

      {/* 门把手 */}
      {obj.type === 'door' && (
        <mesh position={[obj.dimensions.width / 2 - 0.1, 0, obj.dimensions.depth / 2 + 0.02]}>
          <sphereGeometry args={[0.03, 8, 8]} />
          <meshStandardMaterial
            color="#C0C0C0"
            metalness={0.9}
            roughness={0.1}
          />
        </mesh>
      )}

      {/* 选中高亮 */}
      {isSelected && (
        <mesh position={[0, 0, obj.dimensions.depth / 2 + 0.05]}>
          <boxGeometry args={[
            obj.dimensions.width + 0.05,
            obj.dimensions.height + 0.05,
            0.02,
          ]} />
          <meshBasicMaterial color="#FFD700" transparent opacity={0.3} />
        </mesh>
      )}

      {/* 标签 */}
      {isSelected && (
        <Html position={[0, obj.dimensions.height / 2 + 0.3, 0]} center>
          <div className="door-label">
            <strong>{obj.name}</strong>
            <span>{obj.type === 'door' ? '🚪 门' : '🪟 窗'}</span>
          </div>
        </Html>
      )}
    </group>
  )
}

// ════════════════════════════════════════════════
//  关系线
// ════════════════════════════════════════════════

function RelationLine({ edge, objects, isSelected }: {
  edge: RelationEdge
  objects: DoorObject[]
  isSelected: boolean
}) {
  const source = objects[edge.source]
  const target = objects[edge.target]

  if (!source || !target) return null

  const isHighlighted = isSelected
  const color = edge.relation === 'same_room'
    ? (isHighlighted ? '#00FF88' : '#22CC66')
    : (isHighlighted ? '#FF4444' : '#883333')

  const opacity = isHighlighted ? 0.8 : 0.15
  const lineWidth = isHighlighted ? 2 : 1

  return (
    <Line
      points={[
        [source.position[0], source.position[1], source.position[2]],
        [target.position[0], target.position[1], target.position[2]],
      ]}
      color={color}
      lineWidth={lineWidth}
      transparent
      opacity={opacity}
      dashed={edge.relation === 'diff_room'}
      dashScale={50}
      dashSize={1}
      gapSize={1}
    />
  )
}

// ════════════════════════════════════════════════
//  3D 墙面
// ════════════════════════════════════════════════

function Wall() {
  return (
    <mesh position={[150, 1.5, -3.1]} receiveShadow>
      <boxGeometry args={[300, 3, 0.2]} />
      <meshStandardMaterial color="#3D3D3D" roughness={0.9} />
    </mesh>
  )
}

// ════════════════════════════════════════════════
//  地板
// ════════════════════════════════════════════════

function Floor() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[150, 0, 0]} receiveShadow>
      <planeGeometry args={[310, 20]} />
      <meshStandardMaterial color="#2A2A2A" roughness={0.95} />
    </mesh>
  )
}

// ════════════════════════════════════════════════
//  主场景
// ════════════════════════════════════════════════

export default function RelationScene({ selectedId, onSelect, relations = [], showRelations = false }: Props) {
  const objects = useMemo(() => generateDoors(), [])

  // 如果没有传入relations，用本地计算
  const edges = useMemo(() => {
    if (relations.length > 0) return relations
    return computeRelations(objects)
  }, [relations, objects])

  return (
    <group>
      {/* 墙面和地板 */}
      <Wall />
      <Floor />

      {/* 关系线 */}
      {showRelations && edges.map((edge, i) => (
        <RelationLine
          key={i}
          edge={edge}
          objects={objects}
          isSelected={
            selectedId !== undefined &&
            (edge.source === selectedId || edge.target === selectedId)
          }
        />
      ))}

      {/* 门/窗对象 */}
      {objects.map((obj) => (
        <DoorMesh
          key={obj.id}
          obj={obj}
          isSelected={obj.id === selectedId}
          onClick={() => onSelect?.(obj.id)}
        />
      ))}

      {/* 轴标签 */}
      <Text
        position={[150, -0.5, 0]}
        fontSize={3}
        color="#334466"
        anchorX="center"
      >
        沿墙距离 (0 — 300 米)
      </Text>

      {/* 图例 */}
      <group position={[-5, 3, 0]}>
        <Html>
          <div className="scene-legend">
            <div className="legend-title">空间关系图例</div>
            <div className="legend-item">
              <span className="legend-line same" />同房间（&lt; 5m）
            </div>
            <div className="legend-item">
              <span className="legend-line diff" />不同房间（&gt; 10m）
            </div>
            <div className="legend-item">
              <span className="legend-dot door" />门（135个）
            </div>
            <div className="legend-item">
              <span className="legend-dot window" />窗（16个）
            </div>
          </div>
        </Html>
      </group>
    </group>
  )
}
