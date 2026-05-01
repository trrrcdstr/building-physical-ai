/**
 * GaussianScene.tsx
 *
 * 3D Gaussian Splatting 渲染场景
 *
 * 技术方案：Canvas 2D 叠加 Three.js 3D 双层架构
 * - 底层：Canvas 2D 渲染高斯分布（快速、精确）
 * - 顶层：Three.js Points 增强（添加3D深度和相机交互）
 *
 * 高斯模型数据格式（来自 gaussian_api.py / train_gaussian_api.py）：
 * {
 *   scene: "室内_家庭",
 *   config: { num_gaussians: 300, image_width: 160, image_height: 120 },
 *   final_loss: 0.040,
 *   gaussians: {
 *     num_gaussians: number,
 *     positions: [[x, y], ...],  // 2D 图像坐标 (0~160, 0~120)
 *     scales: [r, ...],           // 高斯半径（像素）
 *     colors: [[r,g,b], ...]       // RGB 0-1 float
 *   }
 * }
 *
 * 渲染策略：
 * - ≤300 gaussians: 渲染为彩色椭圆（Canvas 2D，性能好）
 * - >300 gaussians: 切换为 Three.js Points 模式（支持缩放旋转）
 * - 点击场景可切换渲染模式
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { Canvas, useThree, ThreeEvent } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera } from '@react-three/drei'
import * as THREE from 'three'
import { useBuildingStore } from '../store/buildingStore'

// ════════════════════════════════════════════════
//  类型
// ════════════════════════════════════════════════

interface GaussianPoint {
  position: [number, number]
  scale: number
  color: [number, number, number]
}

interface GaussianModel {
  scene: string
  config: {
    num_gaussians: number
    image_width: number
    image_height: number
  }
  final_loss: number
  training_time: number
  gaussians: {
    num_gaussians: number
    positions: number[][]
    scales: number[]
    colors: number[][]
  }
}

interface Props {
  // 可选：指定加载哪个场景的 Gaussian 模型
  sceneName?: string
}

// ════════════════════════════════════════════════
//  可用 Gaussian 模型列表
// ════════════════════════════════════════════════

const GAUSSIAN_MODELS: Record<string, string> = {
  '室内_家庭': '/gaussian/室内_家庭_model.json',
  '室内_工装': '/gaussian/室内_工装_model.json',
  '建筑_别墅': '/gaussian/建筑_别墅建筑花园_model.json',
  '园林景观': '/gaussian/园林效果图_gpu.json',
}

// 备用：内联演示数据（当 API 不可用时）
const DEMO_GAUSSIANS: GaussianPoint[] = Array.from({ length: 300 }, (_, i) => ({
  position: [
    40 + (i % 12) * 8 + Math.random() * 4,
    30 + Math.floor(i / 12) * 7 + Math.random() * 3,
  ],
  scale: 5 + Math.random() * 8,
  color: [
    0.3 + Math.random() * 0.5,
    0.3 + Math.random() * 0.5,
    0.3 + Math.random() * 0.5,
  ],
}))

// ════════════════════════════════════════════════
//  颜色 → 物体类型推断
// ════════════════════════════════════════════════

function inferObjectTypeFromColor(r: number, g: number, b: number): string {
  // 暖色（红/橙/黄）→ 地板
  // 冷色（灰/白/褐）→ 墙体
  // 蓝紫色 → 玻璃
  const warmth = r * 1.5 - b * 0.5
  const coolness = b * 1.2 - r * 0.3

  if (b > 0.5 && r < 0.4 && g < 0.6) {
    return 'glass_window'
  }
  if (warmth > 0.4 && r > 0.5) {
    return 'floor_tile'
  }
  return 'wall_brick'
}

function getObjectTypeName(type: string): string {
  const names: Record<string, string> = {
    'floor_tile': '瓷砖地板',
    'wall_brick': '砖墙',
    'glass_window': '玻璃窗',
  }
  return names[type] || type
}

// ════════════════════════════════════════════════
//  Canvas 2D 渲染层（精确渲染高斯椭圆）
// ════════════════════════════════════════════════

interface GaussianCanvasProps {
  model: GaussianModel | null
  onHover?: (count: number) => void
  renderMode: 'canvas' | 'points'
  onGaussianClick?: (index: number, position: [number, number, number], color: [number, number, number], type: string) => void
}

function GaussianCanvas({ model, onHover, renderMode, onGaussianClick }: GaussianCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const animFrameRef = useRef<number>(0)
  const [dims, setDims] = useState({ w: 320, h: 240 })
  const [highlightedIndex, setHighlightedIndex] = useState<number | null>(null)

  // 加载模型时调整尺寸
  useEffect(() => {
    if (!model) return
    const { config } = model
    const scale = Math.min(320 / config.image_width, 240 / config.image_height)
    setDims({
      w: Math.round(config.image_width * scale),
      h: Math.round(config.image_height * scale),
    })
  }, [model])

  // 处理点击事件
  const handleCanvasClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!model || !onGaussianClick) return

    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const gaussians = model.gaussians
    const scaleX = dims.w / model.config.image_width
    const scaleY = dims.h / model.config.image_height

    // 找到最近的点
    let minDist = Infinity
    let nearestIdx = -1

    for (let i = 0; i < gaussians.num_gaussians; i++) {
      const [px, py] = gaussians.positions[i]
      const cx = px * scaleX
      const cy = py * scaleY

      const dist = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
      if (dist < minDist && dist < 30) {
        minDist = dist
        nearestIdx = i
      }
    }

    if (nearestIdx >= 0) {
      const [px, py] = gaussians.positions[nearestIdx]
      const [cr, cg, cb] = gaussians.colors[nearestIdx]
      const objType = inferObjectTypeFromColor(cr, cg, cb)

      // 映射到 3D 坐标
      const scaleX3D = 100 / model.config.image_width
      const scaleY3D = 60 / model.config.image_height
      const pos3D: [number, number, number] = [
        px * scaleX3D - 50,
        py * scaleY3D - 30,
        0
      ]
      const color3D: [number, number, number] = [cr, cg, cb]

      setHighlightedIndex(nearestIdx)
      onGaussianClick(nearestIdx, pos3D, color3D, objType)
    }
  }, [model, dims, onGaussianClick])

  // 渲染高斯
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const gaussians = model?.gaussians
    if (!gaussians) return

    const scale_x = dims.w / (model!.config.image_width || 160)
    const scale_y = dims.h / (model!.config.image_height || 120)

    const render = () => {
      ctx.clearRect(0, 0, dims.w, dims.h)

      // 半透明背景（保留 Three.js 黑色背景）
      ctx.fillStyle = 'rgba(6, 6, 18, 0.0)'
      ctx.fillRect(0, 0, dims.w, dims.h)

      // 绘制每个高斯椭圆
      for (let i = 0; i < gaussians.num_gaussians; i++) {
        const [px, py] = gaussians.positions[i]
        const r = gaussians.scales[i]
        const [cr, cg, cb] = gaussians.colors[i]

        const cx = px * scale_x
        const cy = py * scale_y
        let rx = r * scale_x
        let ry = r * scale_y

        // 高亮选中的点
        if (i === highlightedIndex) {
          rx *= 1.5
          ry *= 1.5
        }

        // 高斯椭圆：使用径向渐变模拟正态分布
        const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(rx, ry))
        grad.addColorStop(0, `rgba(${(cr*255)|0}, ${(cg*255)|0}, ${(cb*255)|0}, 0.9)`)
        grad.addColorStop(0.5, `rgba(${(cr*255)|0}, ${(cg*255)|0}, ${(cb*255)|0}, 0.4)`)
        grad.addColorStop(1, `rgba(${(cr*255)|0}, ${(cg*255)|0}, ${(cb*255)|0}, 0)`)

        ctx.save()
        ctx.beginPath()
        ctx.ellipse(cx, cy, Math.max(rx, 1), Math.max(ry, 1), 0, 0, Math.PI * 2)
        ctx.fillStyle = grad
        ctx.fill()

        // 高亮边框
        if (i === highlightedIndex) {
          ctx.strokeStyle = '#00ffff'
          ctx.lineWidth = 2
          ctx.stroke()
        }

        ctx.restore()
      }

      // 网格线（参考线）
      ctx.strokeStyle = 'rgba(100, 140, 255, 0.08)'
      ctx.lineWidth = 0.5
      for (let x = 0; x < dims.w; x += 40) {
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, dims.h)
        ctx.stroke()
      }
      for (let y = 0; y < dims.h; y += 40) {
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(dims.w, y)
        ctx.stroke()
      }

      onHover?.(gaussians.num_gaussians)
    }

    render()
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    }
  }, [model, dims, onHover, highlightedIndex])

  if (renderMode !== 'canvas') return null

  return (
    <div
      ref={containerRef}
      style={{
        position: 'absolute',
        bottom: 16,
        right: 16,
        width: dims.w,
        height: dims.h,
        borderRadius: 8,
        overflow: 'hidden',
        border: '1px solid rgba(100,140,255,0.3)',
        zIndex: 20,
        pointerEvents: 'auto',
        cursor: 'crosshair',
      }}
    >
      <canvas
        ref={canvasRef}
        width={dims.w}
        height={dims.h}
        style={{ display: 'block' }}
        onClick={handleCanvasClick}
      />
      {/* 标签 */}
      <div style={{
        position: 'absolute',
        top: 4,
        left: 4,
        background: 'rgba(6,6,18,0.85)',
        color: '#64b5f6',
        fontSize: 9,
        padding: '2px 5px',
        borderRadius: 3,
        fontFamily: 'monospace',
      }}>
        2D Gaussian ({model?.config.num_gaussians ?? 0})
      </div>
      {/* 点击提示 */}
      <div style={{
        position: 'absolute',
        bottom: 4,
        left: 4,
        background: 'rgba(6,6,18,0.85)',
        color: '#aaa',
        fontSize: 8,
        padding: '2px 5px',
        borderRadius: 3,
      }}>
        点击查看物理属性
      </div>
    </div>
  )
}

// ════════════════════════════════════════════════
//  Three.js Points 渲染层（3D 交互）
// ════════════════════════════════════════════════

interface GaussianPointsProps {
  model: GaussianModel | null
  width: number
  height: number
  highlightedIndex: number | null
  onPointClick: (index: number, position: [number, number, number], color: [number, number, number], type: string) => void
}

function GaussianPoints({ model, width, height, highlightedIndex, onPointClick }: GaussianPointsProps) {
  const gaussians = model?.gaussians
  if (!gaussians) return null

  const N = gaussians.num_gaussians

  // 将 2D 图像坐标映射到 3D 空间
  // X: 0~width → -50~50
  // Y: 0~height → -30~30
  // Z: 随机散布在 ±5 范围（模拟深度）
  const { positions, colors, sizes } = useMemo(() => {
    const positions = new Float32Array(N * 3)
    const colors = new Float32Array(N * 3)
    const sizes = new Float32Array(N)

    const scaleX = 100 / (model!.config.image_width || 160)
    const scaleY = 60 / (model!.config.image_height || 120)

    for (let i = 0; i < N; i++) {
      const [px, py] = gaussians.positions[i]
      positions[i * 3] = (px * scaleX) - 50
      positions[i * 3 + 1] = (py * scaleY) - 30
      positions[i * 3 + 2] = (Math.random() - 0.5) * 5

      const [cr, cg, cb] = gaussians.colors[i]
      colors[i * 3] = cr
      colors[i * 3 + 1] = cg
      colors[i * 3 + 2] = cb

      // 高亮点加大
      sizes[i] = i === highlightedIndex
        ? gaussians.scales[i] * 0.8
        : gaussians.scales[i] * 0.3
    }

    return { positions, colors, sizes }
  }, [gaussians, model, highlightedIndex])

  // 处理点击事件
  const handleClick = useCallback((e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation()
    if (!model) return

    // 获取点击的点索引
    const intersect = e.intersections[0]
    if (!intersect) return

    const index = intersect.index
    if (index === undefined) return

    const [px, py] = model.gaussians.positions[index]
    const [cr, cg, cb] = model.gaussians.colors[index]
    const objType = inferObjectTypeFromColor(cr, cg, cb)

    const scaleX3D = 100 / model.config.image_width
    const scaleY3D = 60 / model.config.image_height
    const pos3D: [number, number, number] = [
      positions[index * 3],
      positions[index * 3 + 1],
      positions[index * 3 + 2]
    ]
    const color3D: [number, number, number] = [cr, cg, cb]

    onPointClick(index, pos3D, color3D, objType)
  }, [model, positions, onPointClick])

  // 自定义着色器材质（圆点）
  const material = useMemo(() => new THREE.ShaderMaterial({
    vertexShader: `
      attribute float size;
      varying vec3 vColor;
      void main() {
        vColor = color;
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = size * (300.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      varying vec3 vColor;
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        float alpha = 1.0 - smoothstep(0.2, 0.5, d);
        gl_FragColor = vec4(vColor, alpha * 0.85);
      }
    `,
    transparent: true,
    vertexColors: true,
    depthWrite: false,
  }), [])

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))
    geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1))
    return geo
  }, [positions, colors, sizes])

  return (
    <points
      geometry={geometry}
      material={material}
      onClick={handleClick}
      onPointerOver={(e) => {
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={(e) => {
        document.body.style.cursor = 'default'
      }}
    />
  )
}

// ════════════════════════════════════════════════
//  高亮点标记（3D）
// ════════════════════════════════════════════════

interface HighlightMarkerProps {
  position: [number, number, number] | null
  color: [number, number, number] | null
}

function HighlightMarker({ position, color }: HighlightMarkerProps) {
  if (!position || !color) return null

  return (
    <group position={position}>
      {/* 外圈 */}
      <mesh>
        <ringGeometry args={[2, 2.5, 32]} />
        <meshBasicMaterial color="#00ffff" transparent opacity={0.8} side={THREE.DoubleSide} />
      </mesh>
      {/* 中心点 */}
      <mesh>
        <circleGeometry args={[1, 32]} />
        <meshBasicMaterial color={`rgb(${color[0]*255}, ${color[1]*255}, ${color[2]*255})`} />
      </mesh>
    </group>
  )
}

// ════════════════════════════════════════════════
//  主组件
// ════════════════════════════════════════════════

const DATA_CENTER: [number, number, number] = [-3.7, 0, 0.8]

export default function GaussianScene({ sceneName = '室内_家庭' }: Props) {
  const [model, setModel] = useState<GaussianModel | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [renderMode, setRenderMode] = useState<'canvas' | 'points'>('canvas')
  const [hoveredCount, setHoveredCount] = useState(0)
  const [highlightedIndex, setHighlightedIndex] = useState<number | null>(null)
  const [highlightedPosition, setHighlightedPosition] = useState<[number, number, number] | null>(null)
  const [highlightedColor, setHighlightedColor] = useState<[number, number, number] | null>(null)

  const selectObject = useBuildingStore(s => s.selectObject)
  const selectGaussian = useBuildingStore(s => s.selectGaussian)

  // 加载 Gaussian 模型
  useEffect(() => {
    setLoading(true)
    setError(null)

    const modelKey = Object.keys(GAUSSIAN_MODELS).find(k =>
      sceneName.includes(k) || k.includes(sceneName)
    ) || '室内_家庭'

    // 尝试加载模型 JSON
    fetch(`/gaussian/${modelKey}_model.json`)
      .then(r => {
        if (!r.ok) throw new Error('Model not found')
        return r.json()
      })
      .then(data => {
        setModel(data as GaussianModel)
        setLoading(false)
      })
      .catch(() => {
        // Fallback: 使用演示数据
        const demoModel: GaussianModel = {
          scene: '演示模式',
          config: { num_gaussians: 300, image_width: 160, image_height: 120 },
          final_loss: 0.0,
          training_time: 0,
          gaussians: {
            num_gaussians: 300,
            positions: DEMO_GAUSSIANS.map(g => g.position),
            scales: DEMO_GAUSSIANS.map(g => g.scale),
            colors: DEMO_GAUSSIANS.map(g => g.color),
          }
        }
        setModel(demoModel)
        setLoading(false)
      })
  }, [sceneName])

  // 切换渲染模式
  const toggleMode = useCallback(() => {
    setRenderMode(m => m === 'canvas' ? 'points' : 'canvas')
  }, [])

  // 处理高斯点点击
  const handleGaussianClick = useCallback((index: number, position: [number, number, number], color: [number, number, number], type: string) => {
    setHighlightedIndex(index)
    setHighlightedPosition(position)
    setHighlightedColor(color)

    // 调用 store 更新选中状态
    const gaussianId = `gaussian_${index}`
    selectGaussian({
      id: gaussianId,
      position,
      type,
      color
    })

    // 同时更新 selectedObject 以便 PhysicsPanel 显示
    selectObject({
      id: gaussianId,
      name: getObjectTypeName(type),
      type: 'gaussian_point',
      category: 'structure',
      subcategory: type,
      position: [0, 0, 0],
      dimensions: { width: 1, depth: 1, height: 1 },
      material: type,
    } as any)
  }, [selectGaussian, selectObject])

  const imgW = model?.config.image_width || 160
  const imgH = model?.config.image_height || 120

  return (
    <group>
      {/* 相机已由父组件 App.tsx 的 CameraController 控制 */}

      {/* 3D Points 渲染层（当切换到 points 模式时） */}
      {renderMode === 'points' && model && (
        <>
          <GaussianPoints
            model={model}
            width={imgW}
            height={imgH}
            highlightedIndex={highlightedIndex}
            onPointClick={handleGaussianClick}
          />
          <HighlightMarker position={highlightedPosition} color={highlightedColor} />
        </>
      )}

      {/* 信息面板 */}
      <group position={[DATA_CENTER[0] + 40, DATA_CENTER[1] + 15, DATA_CENTER[2]]}>
        {/* 模型信息卡片 */}
        <mesh>
          <planeGeometry args={[30, 12]} />
          <meshBasicMaterial color="#0a0a1a" transparent opacity={0.85} />
        </mesh>
        <text
          position={[-12, 4, 0.01]}
          fontSize={1.5}
          color="#64b5f6"
          anchorX="left"
          font="https://fonts.gstatic.com/s/notosanssc/v36/k3kXo84MPvpLmixcA63oeALhLOCT-xWNm8Hqd37g1OkDRZe7lR4sg1IzSy-MNbE9VQ8.woff2"
        >
          {loading ? '加载中...' : (model?.scene || '未知')}
        </text>
        <text
          position={[-12, 2, 0.01]}
          fontSize={1.0}
          color="#aaa"
          anchorX="left"
        >
          {loading ? '' : `高斯数: ${model?.config.num_gaussians} | 损失: ${model?.final_loss.toFixed(4)}`}
        </text>
        <text
          position={[-12, 0.5, 0.01]}
          fontSize={0.9}
          color="#888"
          anchorX="left"
        >
          {loading ? '' : `图像: ${model?.config.image_width}×${model?.config.image_height}px | 渲染模式: ${renderMode}`}
        </text>

        {/* 渲染模式切换按钮说明 */}
        <text
          position={[-12, -1.5, 0.01]}
          fontSize={0.8}
          color="#64b5f6"
          anchorX="left"
        >
          点击 [G] 切换: canvas/points 模式
        </text>

        {/* 悬停计数 */}
        {hoveredCount > 0 && (
          <text position={[-12, -3, 0.01]} fontSize={0.9} color="#aaa" anchorX="left">
            悬停高斯: {hoveredCount} 个
          </text>
        )}

        {/* 进度指示 */}
        {loading && (
          <text position={[-12, 2, 0.01]} fontSize={1.0} color="#fbbf24" anchorX="left">
            加载 Gaussian 模型中...
          </text>
        )}
      </group>

      {/* Canvas 2D 渲染层（默认） */}
      {renderMode === 'canvas' && (
        <GaussianCanvas
          model={model}
          onHover={setHoveredCount}
          renderMode={renderMode}
          onGaussianClick={handleGaussianClick}
        />
      )}

      {/* 键盘快捷键监听 */}
      <KeyboardHandler onToggle={toggleMode} />
    </group>
  )
}

// 键盘快捷键
function KeyboardHandler({ onToggle }: { onToggle: () => void }) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'g' || e.key === 'G') onToggle()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onToggle])
  return null
}

// 导出子组件供独立使用
export { GaussianCanvas, GaussianPoints }
