/**
 * AgentCommandPanel.tsx
 *
 * 具身AI Agent 控制面板 — 物理世界模型的核心交互入口
 *
 * 三个"哇"时刻：
 * 1. 点击房间 → 看到物理属性 + 钻孔安全评估（Block/Function层）
 * 2. 输入"在XX墙钻孔" → Agent自动决策（安全/拒绝/方案）
 * 3. 3D场景中高亮安全钻孔区域（Harness层壁垒展示）
 *
 * 改进（2026-04-25）：
 * - 改进一：清洁任务展示Harness层物理常识（玻璃摩擦系数、安全力度等）
 * - 改进二：空间关系推理有实际内容输出
 * - 改进三：修复服务状态检测
 */

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useBuildingStore } from '../store/buildingStore'
import { roomSceneData } from '../data/room_scene_data'
import { API_ENDPOINTS } from '../config/api'
import './AgentCommandPanel.css'

// ─── 材质物理知识库（Harness层核心数据）─────────────
const MATERIAL_PHYSICS: Record<string, {
  name: string
  friction_dry: number
  friction_wet: number
  density: number  // kg/m³
  hardness: string
  maxForce: number  // N
  warnings: string[]
  safeTools: string[]
  prohibitedTools: string[]
  specialCare: string[]
}> = {
  '钢化玻璃': {
    name: '钢化玻璃 (Tempered Glass)',
    friction_dry: 0.35,
    friction_wet: 0.18,
    density: 2500,
    hardness: '高 (莫氏6-7)',
    maxForce: 5,  // N，仅5牛顿力度
    warnings: [
      '⚠️ 钢化玻璃边缘最脆弱，禁用硬质工具直接接触',
      '⚠️ 湿态摩擦系数骤降至0.18，移动速度需降至0.3m/s',
      '⚠️ 禁用含氨或酒精的清洁剂（腐蚀玻璃镀膜）',
    ],
    safeTools: ['橡胶刮刀', '微纤维布', '硅胶刮板', '软毛刷'],
    prohibitedTools: ['金属刷', '钢丝球', '硬质塑料刮刀', '含研磨剂的清洁剂'],
    specialCare: ['自上而下清洁', '单向擦拭避免来回摩擦', '干燥后用玻璃刮收水'],
  },
  '瓷砖': {
    name: '瓷砖 (Ceramic Tile)',
    friction_dry: 0.40,
    friction_wet: 0.20,
    density: 2300,
    hardness: '高 (莫氏6)',
    maxForce: 20,
    warnings: [
      '⚠️ 湿态摩擦系数0.20，机器人移动速度限制0.3m/s',
      '⚠️ 瓷砖缝隙需用软毛刷清洁，禁止高压水枪',
      '⚠️ 清洁剂pH值需控制在6-8之间',
    ],
    safeTools: ['橡胶刮刀', '软毛刷', '微纤维拖布', '真空吸尘器'],
    prohibitedTools: ['金属铲刀', '高压水枪', '强酸强碱清洁剂'],
    specialCare: ['先扫后拖', '从内向外倒退清洁', '及时擦干缝隙'],
  },
  '不锈钢': {
    name: '不锈钢 (Stainless Steel)',
    friction_dry: 0.20,
    friction_wet: 0.12,
    density: 8000,
    hardness: '中 (莫氏5.5)',
    maxForce: 15,
    warnings: [
      '⚠️ 拉丝面纹理方向清洁，顺纹理单向擦拭',
      '⚠️ 禁用含氯清洁剂（导致点蚀）',
    ],
    safeTools: ['软纤维布', '专用不锈钢清洁剂', '清水'],
    prohibitedTools: ['钢丝球', '含氯清洁剂', '研磨清洁剂'],
    specialCare: ['顺纹理擦拭', '及时擦干水渍', '定期使用专用保养剂'],
  },
  '实木地板': {
    name: '实木地板 (Hardwood)',
    friction_dry: 0.40,
    friction_wet: 0.25,
    density: 700,
    hardness: '低 (莫氏2-3)',
    maxForce: 10,
    warnings: [
      '⚠️ 实木怕水！拖布含水量<30%，严禁积水',
      '⚠️ 移动速度限制0.2m/s，防止刮伤漆面',
      '⚠️ 禁止使用蒸汽拖把',
    ],
    safeTools: ['微纤维拖布(干)', '专用木地板清洁剂', '静电拖布'],
    prohibitedTools: ['湿拖把', '蒸汽拖把', '强碱性清洁剂', '金属刷'],
    specialCare: ['干拖先除灰', '清洁剂需拧干', '定期打蜡保养'],
  },
}

// ─── 房间空间关系知识库 ──────────────────────────────
const ROOM_SPATIAL_KNOWLEDGE: Record<string, {
  area: number
  adjacent: { room: string; distance: number; features: string[] }[]
  powerOutlets: { count: number; nearest: number }  // 最近插座距离(m)
  wetAreas: string[]  // 湿区标识
  safetyNotes: string[]
}> = {
  'master_bathroom': {
    area: 8.5,
    adjacent: [
      { room: '主卧', distance: 0, features: ['相邻', '共享墙体有门洞'] },
    ],
    powerOutlets: { count: 2, nearest: 1.2 },
    wetAreas: ['淋浴区', '马桶区', '洗手台'],
    safetyNotes: [
      '电源插座距淋浴区需保持≥1.8m（GB 4706.1）',
      '湿区地面摩擦系数0.20，移动速度限制0.3m/s',
    ],
  },
  'shower_room': {
    area: 2.1,
    adjacent: [
      { room: '主卧卫生间', distance: 0, features: ['位于内部'] },
      { room: '马桶区', distance: 0.4, features: ['间距40cm', '连续湿滑表面'] },
      { room: '洗手台', distance: 0.55, features: ['间距55cm'] },
    ],
    powerOutlets: { count: 1, nearest: 1.8 },
    wetAreas: ['淋浴隔断', '地面', '墙壁溅水区'],
    safetyNotes: [
      '玻璃隔断邻接马桶区和洗手台，形成连续湿滑表面',
      '最近电源插座1.8m，符合安全规范',
      '禁止在湿区使用非防水电气设备',
    ],
  },
  'bedroom': {
    area: 20.0,
    adjacent: [
      { room: '书房', distance: 3.5, features: ['相邻'] },
      { room: '主卧卫生间', distance: 2.0, features: ['相邻'] },
    ],
    powerOutlets: { count: 4, nearest: 0.5 },
    wetAreas: [],
    safetyNotes: [
      '电源插座分布均匀（4个），最近距床0.5m',
      '实木地板区域，拖布含水量<30%',
    ],
  },
}

// ─── 类型定义 ───────────────────────────────────────
interface PhysicsAnalysis {
  materials: {
    name: string
    friction_dry: number
    friction_wet: number
    maxForce: number
    warnings: string[]
    safeTools: string[]
    prohibitedTools: string[]
    specialCare: string[]
  }[]
  safetyInstructions: string[]
  robotConfig: {
    maxSpeed: number
    forceLimit: number
    mode: string
  }
}

interface SpatialRelation {
  description: string
  distance?: number
  features: string[]
}

interface DrillResult {
  wall: string
  safe: boolean
  reason: string
  depth_cm?: number
  tool?: string
  warnings?: string[]
  steps?: string[]
}

interface AgentResponse {
  task_type: string
  success: boolean
  message: string
  room?: string
  drill_result?: DrillResult
  physics_analysis?: PhysicsAnalysis
  spatial_relations?: SpatialRelation[]
  steps?: string[]
  warnings?: string[]
  confidence?: number
}

// ─── 物理分析展示组件（P1升级：决策摘要醒目化）──────
function PhysicsAnalysisDisplay({ analysis, title, decisionSummary }: {
  analysis: PhysicsAnalysis; title: string; decisionSummary?: string
}) {
  return (
    <div className="physics-analysis-card">
      <div className="physics-header">
        <span className="physics-icon">⚛️</span>
        <span className="physics-title">{title}</span>
      </div>

      {/* 决策摘要 — P1核心：3秒内让观众看懂"为什么能干对" */}
      {decisionSummary && (
        <div className="decision-summary-card">
          <div className="decision-summary-label">🎯 决策摘要</div>
          <div className="decision-summary-text">{decisionSummary}</div>
        </div>
      )}

      {/* 机器人配置 */}
      <div className="physics-robot-config">
        <span className="config-tag">🤖 机器人配置</span>
        <div className="config-items">
          <span>移动速度: <strong>{analysis.robotConfig.maxSpeed}m/s</strong></span>
          <span>力度限制: <strong>{analysis.robotConfig.forceLimit}N</strong></span>
          <span>工作模式: <strong>{analysis.robotConfig.mode}</strong></span>
        </div>
      </div>

      {/* 材质分析 */}
      {analysis.materials.map((mat, i) => (
        <div key={i} className="material-analysis">
          <div className="material-name">📦 {mat.name}</div>

          {/* 摩擦系数 */}
          <div className="friction-row">
            <span className="friction-label">摩擦系数:</span>
            <span className="friction-dry">干态 <strong>{mat.friction_dry}</strong></span>
            <span className="friction-arrow">→</span>
            <span className="friction-wet">湿态 <strong className="warn">{mat.friction_wet}</strong> ⚠️</span>
          </div>

          {/* 安全力度 */}
          <div className="force-row">
            <span>安全接触力度: <strong>{mat.maxForce}N</strong></span>
          </div>

          {/* 警告 */}
          {mat.warnings.map((w, wi) => (
            <div key={wi} className="physics-warning">⚠️ {w}</div>
          ))}

          {/* 可用工具 */}
          <div className="tool-row">
            <span className="tool-label">✅ 可用工具:</span>
            <div className="tool-tags">
              {mat.safeTools.map((t, ti) => (
                <span key={ti} className="tool-tag safe">{t}</span>
              ))}
            </div>
          </div>

          {/* 禁用工具 */}
          <div className="tool-row">
            <span className="tool-label">❌ 禁用工具:</span>
            <div className="tool-tags">
              {mat.prohibitedTools.map((t, ti) => (
                <span key={ti} className="tool-tag prohibited">{t}</span>
              ))}
            </div>
          </div>

          {/* 特殊护理 */}
          {mat.specialCare.length > 0 && (
            <div className="special-care">
              <span className="care-label">💡 操作要点:</span>
              {mat.specialCare.map((c, ci) => (
                <div key={ci} className="care-item">• {c}</div>
              ))}
            </div>
          )}
        </div>
      ))}

      {/* 总体安全须知 */}
      {analysis.safetyInstructions.length > 0 && (
        <div className="safety-instructions">
          <div className="safety-title">🛡️ 安全须知</div>
          {analysis.safetyInstructions.map((s, si) => (
            <div key={si} className="safety-item">• {s}</div>
          ))}
        </div>
      )}
    </div>
  )
}

// ─── 空间关系展示组件 ────────────────────────────────
function SpatialRelationDisplay({ relations, roomName }: { relations: SpatialRelation[]; roomName: string }) {
  return (
    <div className="spatial-relation-card">
      <div className="spatial-header">
        <span className="spatial-icon">🗺️</span>
        <span className="spatial-title">空间关系推理</span>
      </div>

      <div className="spatial-room-info">
        <span>📍 {roomName}</span>
      </div>

      {relations.map((rel, i) => (
        <div key={i} className="spatial-relation-item">
          <div className="rel-description">{rel.description}</div>
          {rel.distance !== undefined && (
            <div className="rel-distance">📏 距离: {rel.distance}米</div>
          )}
          {rel.features.map((f, fi) => (
            <div key={fi} className="rel-feature">• {f}</div>
          ))}
        </div>
      ))}

      <div className="spatial-footer">
        <span className="spatial-badge">Harness层 · L3</span>
      </div>
    </div>
  )
}

// ─── 钻孔分析结果渲染（P1增强：决策叙事+替代方案）──
function DrillWallAnalysis({ result, roomName }: { result: DrillResult; roomName: string }) {
  const wallColors: Record<string, string> = {
    north: '#E53935', south: '#43A047', east: '#FB8C00', west: '#1E88E5'
  }
  const wallLabels: Record<string, string> = {
    north: '北墙（承重墙）', south: '南墙', east: '东墙', west: '西墙'
  }
  // 墙体材质信息
  const wallMaterial: Record<string, { type: string; concrete: string; hasHiddenPipes: boolean }> = {
    north: { type: '承重墙', concrete: 'C30钢筋混凝土', hasHiddenPipes: true },
    south: { type: '填充墙', concrete: '加气混凝土砌块', hasHiddenPipes: false },
    east:  { type: '填充墙', concrete: '加气混凝土砌块', hasHiddenPipes: true },
    west:  { type: '填充墙', concrete: '加气混凝土砌块', hasHiddenPipes: false },
  }
  const icon = result.safe ? '✅' : '🚫'
  const color = result.safe ? '#2E7D32' : '#C62828'
  const bg    = result.safe ? '#E8F5E9' : '#FFEBEE'
  const wInfo = wallMaterial[result.wall] || { type: '未知', concrete: '—', hasHiddenPipes: false }

  return (
    <div className="drill-result-card" style={{ borderLeftColor: color, background: bg }}>
      <div className="drill-wall-header">
        <span className="drill-wall-icon" style={{ color }}>{icon}</span>
        <span className="drill-wall-name" style={{ color }}>{wallLabels[result.wall] || result.wall}</span>
        {result.safe
          ? <span className="drill-badge safe">可钻孔</span>
          : <span className="drill-badge danger">禁止钻孔</span>}
      </div>

      {/* 墙体材质信息 */}
      <div className="drill-wall-material">
        <span>🏗️ 墙体类型: <strong>{wInfo.type}</strong></span>
        <span>🧱 材质: <strong>{wInfo.concrete}</strong></span>
        <span>⚡ 暗埋管线: <strong>{wInfo.hasHiddenPipes ? '⚠️ 有' : '✅ 无'}</strong></span>
      </div>

      <div className="drill-reason">{result.reason}</div>
      {result.depth_cm && (
        <div className="drill-meta">
          <span>🔧 推荐深度: <strong>{result.depth_cm}cm</strong></span>
          <span>🛠️ 工具: {result.tool || '冲击钻'}</span>
        </div>
      )}
      {result.warnings && result.warnings.length > 0 && (
        <div className="drill-warnings">
          {result.warnings.map((w, i) => (
            <div key={i} className="drill-warning-item">⚠️ {w}</div>
          ))}
        </div>
      )}
      {/* 替代方案（钻孔拒绝时） */}
      {!result.safe && (
        <div className="drill-alternatives">
          <div className="drill-alt-title">💡 替代方案</div>
          <div className="drill-alt-item">• 免钉胶承重挂钩（承重5kg）</div>
          <div className="drill-alt-item">• 落地式置物架（无需打孔）</div>
          <div className="drill-alt-item">• 转移至南墙/西墙安全区域</div>
        </div>
      )}
      {result.steps && result.steps.length > 0 && (
        <div className="drill-steps">
          <div className="drill-steps-title">📋 操作步骤</div>
          {result.steps.map((s, i) => (
            <div key={i} className="drill-step-item">
              <span className="step-num">{i + 1}</span>
              <span>{s}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ─── 房间物理面板 ────────────────────────────────────
function RoomPhysicsCard({ roomId }: { roomId: string }) {
  const room = roomSceneData.rooms.find(r => r.id === roomId)
  if (!room) return null

  const wallRiskColors: Record<string, string> = {
    north: room.drill_analysis?.north_wall_load_bearing ? '#C62828' : '#2E7D32',
    south: '#2E7D32',
    east:  room.drill_analysis?.east_wall_caution ? '#E65100' : '#2E7D32',
    west: '#2E7D32',
  }
  const wallRisk: Record<string, string> = {
    north: room.drill_analysis?.north_wall_load_bearing ? '🔴 承重墙' : '🟢 非承重',
    south: '🟢 安全',
    east:  room.drill_analysis?.east_wall_caution ? '🟡 有窗/管道' : '🟢 安全',
    west: '🟢 安全',
  }

  return (
    <div className="room-physics-card">
      <div className="rpc-header">
        <span className="rpc-icon">🏠</span>
        <span className="rpc-name">{room.name}</span>
        <span className="rpc-type">{room.type_cn}</span>
      </div>
      <div className="rpc-stats">
        <div className="rpc-stat"><span className="rpc-stat-num">{room.area_m2}</span><span>㎡</span></div>
        <div className="rpc-stat"><span className="rpc-stat-num">{room.door_count}</span><span>门</span></div>
        <div className="rpc-stat"><span className="rpc-stat-num">{room.window_count}</span><span>窗</span></div>
      </div>
      <div className="rpc-section">
        <div className="rpc-section-title">🧱 钻孔安全评估</div>
        {['north', 'south', 'east', 'west'].map(wall => (
          <div key={wall} className="wall-risk-row">
            <span className="wall-label">{wall.toUpperCase().padEnd(5)}</span>
            <span className="wall-risk" style={{ color: wallRiskColors[wall] }}>
              {wallRisk[wall]}
            </span>
          </div>
        ))}
      </div>
      {room.furniture_clearances && room.furniture_clearances.length > 0 && (
        <div className="rpc-section">
          <div className="rpc-section-title">📐 家具间距要求</div>
          {room.furniture_clearances.map((fc: any) => (
            <div key={fc.item} className="clearance-row">
              <span>🛏️ {fc.item}: </span>
              <span>{fc.margin_cm}cm {fc.direction === 'front' ? '前方' : fc.direction === 'pull' ? '拉出' : '后方'}</span>
            </div>
          ))}
        </div>
      )}
      {room.physics_tags && room.physics_tags.length > 0 && (
        <div className="rpc-section">
          <div className="rpc-section-title">⚛️ 物理属性标签</div>
          <div className="rpc-tags">
            {room.physics_tags.slice(0, 8).map((t: string) => (
              <span key={t} className="rpc-tag">{t}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ─── 步骤时间线视图 ────────────────────────────────
function TimelineStepsView({ steps, currentStep, isExecuting }: {
  steps: string[]; currentStep: number; isExecuting: boolean;
}) {
  return (
    <div className="timeline-steps-card">
      <div className="timeline-steps-header">
        <span className="timeline-steps-title">⚡ 执行步骤</span>
        {isExecuting && <span className="exec-running-badge">运行中</span>}
      </div>
      {steps.map((step, i) => {
        const state = currentStep < 0 ? 'pending' : currentStep > i ? 'done' : currentStep === i ? 'active' : 'pending'
        return (
          <div key={i} className={`timeline-step ${state}`}>
            <div className="timeline-step-header">
              <span className="timeline-step-icon">
                {state === 'done' ? '✅' : state === 'active' ? '⚙️' : `${i + 1}`}
              </span>
              <span className="timeline-step-text">{step}</span>
            </div>
            {state === 'active' && (
              <div className="step-progress-fill" style={{ width: '100%' }} />
            )}
            {state === 'pending' && (
              <div className="step-pending-dots">
                <span /><span /><span />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── 实时数据面板 ────────────────────────────────────
function ExecDataPanel({ data, phase }: { data: { speed: number; force: number; friction: number; temp: number }; phase: string }) {
  return (
    <div className="exec-data-panel">
      <div className="edp-header">
        <span>📊 实时数据</span>
        {phase && <span className="edp-phase">{phase}</span>}
      </div>
      <div className="edp-rows">
        {[
          { label: '速度', unit: 'm/s', key: 'speed' as const, max: 1.0 },
          { label: '力度', unit: 'N',  key: 'force' as const, max: 10 },
          { label: '摩擦', unit: '',   key: 'friction' as const, max: 1 },
          { label: '温度', unit: '°C', key: 'temp' as const, max: 50 },
        ].map(({ label, unit, key, max }) => {
          const val = data[key]
          const pct = Math.min((val / max) * 100, 100)
          return (
            <div key={key} className="edp-row">
              <span className="edp-label">{label}</span>
              <div className="edp-bar-bg">
                <div className="edp-bar-fill" style={{ width: `${pct}%` }} />
              </div>
              <span className="edp-val">{val.toFixed(2)}{unit}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── 推理结果展示组件（P1：决策摘要+Harness决策过程）──
function InferenceResultDisplay({ result, roomName }: { result: AgentResponse; roomName: string }) {
  // 根据任务类型生成决策摘要
  const getDecisionSummary = (): string | undefined => {
    if (result.task_type === 'clean' && result.physics_analysis) {
      const mats = result.physics_analysis.materials.map(m => m.name).join('、')
      const mode = result.physics_analysis.robotConfig.mode
      const maxF = result.physics_analysis.robotConfig.forceLimit
      return `识别材质：${mats} → 切换${mode}，力度限制${maxF}N，禁用硬质工具`
    }
    if (result.task_type === 'drill' && result.drill_result) {
      const dr = result.drill_result
      return dr.safe
        ? `✅ 安全区：${dr.wall}墙，建议深度<${dr.depth_cm}cm，工具：${dr.tool}`
        : `🛑 操作拒绝：${dr.wall}墙为承重墙，破坏结构安全！`
    }
    return undefined
  }

  return (
    <div className="inference-result">
      {/* 钻孔任务：先展示Harness决策过程 */}
      {result.task_type === 'drill' && result.drill_result && (
        <div className="harness-decision-flow">
          <div className="harness-flow-title">🛡️ Harness层决策过程</div>
          <div className="harness-flow-steps">
            <div className="harness-flow-step">
              <span className="hfs-num">1</span>
              <span className="hfs-text">墙体类型识别</span>
              <span className={`hfs-result ${result.drill_result.safe ? 'pass' : 'fail'}`}>
                {result.drill_result.wall === 'north' ? '承重墙' : '非承重墙'}
              </span>
            </div>
            <div className="harness-flow-step">
              <span className="hfs-num">2</span>
              <span className="hfs-text">管线排查</span>
              <span className="hfs-result pass">{result.drill_result.safe ? '无暗埋管线' : '—'}</span>
            </div>
            <div className="harness-flow-step">
              <span className="hfs-num">3</span>
              <span className="hfs-text">安全决策</span>
              <span className={`hfs-result ${result.drill_result.safe ? 'pass' : 'fail'}`}>
                {result.drill_result.safe ? '✅ 允许执行' : '🛑 拒绝执行'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 物理分析（含决策摘要） */}
      {result.physics_analysis && (
        <PhysicsAnalysisDisplay
          analysis={result.physics_analysis}
          title="任务分析（Harness层）"
          decisionSummary={getDecisionSummary()}
        />
      )}

      {/* 空间关系推理 */}
      {result.spatial_relations && result.spatial_relations.length > 0 && (
        <SpatialRelationDisplay
          relations={result.spatial_relations}
          roomName={roomName}
        />
      )}

      {/* 操作步骤 */}
      {result.steps && result.steps.length > 0 && (
        <div className="result-steps-card">
          <div className="result-steps-header">
            <span>📋 操作步骤</span>
            {result.confidence !== undefined && (
              <span className="confidence-badge">
                置信度 {Math.round(result.confidence * 100)}%
              </span>
            )}
          </div>
          <div className="result-steps">
            {result.steps.map((s, i) => (
              <div key={i} className="result-step">
                <span className="step-num">{i + 1}</span>
                <span className="step-text">{s}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 警告信息 */}
      {result.warnings && result.warnings.length > 0 && (
        <div className="result-warnings">
          <div className="warnings-header">⚠️ 安全警告</div>
          {result.warnings.map((w, i) => (
            <div key={i} className="warning-item">• {w}</div>
          ))}
        </div>
      )}

      {/* 钻孔结果 */}
      {result.drill_result && (
        <DrillWallAnalysis result={result.drill_result} roomName={roomName} />
      )}
    </div>
  )
}

// ─── 命令示例 ─────────────────────────────────────────
const COMMAND_EXAMPLES = [
  { icon: '🚿', text: '清洁淋浴房的玻璃隔断', hint: '展示Harness层物理常识（玻璃摩擦系数、力度限制）' },
  { icon: '🧱', text: '在东墙钻一个孔挂画', hint: '自动判断非承重墙，输出安全方案' },
  { icon: '🔧', text: '在北墙钻孔安装书架', hint: '检测承重墙，输出警告+替代方案' },
  { icon: '🧹', text: '清洁卧室实木地板', hint: '注意地板防水，移动速度0.2m/s' },
  { icon: '🪟', text: '清洁厨房不锈钢台面', hint: '顺纹理擦拭，禁用含氯清洁剂' },
  { icon: '📦', text: '把床头柜移到窗边', hint: '搬运任务+路径规划' },
]

// ─── 指令历史 ─────────────────────────────────────────
interface ChatMessage {
  id: number
  role: 'user' | 'agent'
  text: string
  result?: AgentResponse
}

// ─── 主组件 ──────────────────────────────────────────
export default function AgentCommandPanel() {
  const selectedObject = useBuildingStore(s => s.selectedObject)
  const selectedWall   = useBuildingStore(s => s.selectedWall)
  const activeScene    = useBuildingStore(s => s.activeScene)

  const [command, setCommand]     = useState('')
  const [loading, setLoading]      = useState(false)
  const [messages, setMessages]   = useState<ChatMessage[]>([])
  const [serverStatus, setStatus]  = useState<'ok' | 'warn' | 'error'>('error')
  const [nnAvailable, setNnAvailable] = useState(false)
  const [activeWall, setActiveWall] = useState<string | null>(null)
  const [msgId, setMsgId]          = useState(1)
  const [isExecuting, setIsExecuting] = useState(false)
  const [currentStep, setCurrentStep]  = useState(-1)
  const [execPhase, setExecPhase]      = useState('')
  const [execData, setExecData]        = useState({ speed: 0, force: 0, friction: 0, temp: 22 })
  const [execResult, setExecResult]     = useState<{ success: boolean; message: string } | null>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // ── 服务健康检查（P0修复：5001无/health端点，改用根路径）───
  useEffect(() => {
    Promise.all([
      // 检查NN推理服务 (5000) — 有/api/health
      fetch(Gp.neural.health)
        .then(r => r.ok ? r.json() : null)
        .catch(() => null),
      // 检查场景API (5001) — 改用 Railway 云端
      fetch('https://scene-production.up.railway.app/scene/')
        .then(r => r.ok ? r.json() : null)
        .catch(() => null),
    ]).then(([nn, v1]) => {
      const nnOk = !!nn
      const v1Ok = !!v1
      if (nnOk && v1Ok) {
        setStatus('ok')
        setNnAvailable(true)
      } else if (nnOk) {
        setStatus('warn')
        setNnAvailable(true)
      } else {
        setStatus('error')
        setNnAvailable(false)
      }
    }).catch(() => {
      setStatus('error')
      setNnAvailable(false)
    })
  }, [])

  // ── 材质识别函数 ───────────────────────────────────
  const identifyMaterials = (cmd: string, roomId: string): string[] => {
    const materials: string[] = []
    const room = roomSceneData.rooms.find(r => r.id === roomId)
    const roomType = room?.type || ''

    // 基于命令关键词识别材质
    if (cmd.includes('淋浴') || cmd.includes('浴室') || cmd.includes('卫生间')) {
      materials.push('瓷砖')  // 地面
      if (cmd.includes('隔断') || cmd.includes('玻璃')) {
        materials.push('钢化玻璃')  // 淋浴房隔断
      }
      materials.push('不锈钢')  // 花洒/水龙头
    }

    if (cmd.includes('厨房') || cmd.includes('台面')) {
      materials.push('不锈钢')
      materials.push('瓷砖')
    }

    if (cmd.includes('卧室') || cmd.includes('地板') || cmd.includes('实木')) {
      materials.push('实木地板')
    }

    if (cmd.includes('客厅') || cmd.includes('地砖')) {
      materials.push('瓷砖')
    }

    // 默认：如果识别不出，添加基础材质
    if (materials.length === 0) {
      materials.push('瓷砖')  // 默认地面材质
    }

    return materials
  }

  // ── 生成物理分析（Harness层核心）──────────────────
  const generatePhysicsAnalysis = (materials: string[], cmd: string): PhysicsAnalysis => {
    const materialData = materials.map(m => MATERIAL_PHYSICS[m] || MATERIAL_PHYSICS['瓷砖'])

    // 计算机器人配置
    const hasGlass = materials.includes('钢化玻璃')
    const hasWet = cmd.includes('淋浴') || cmd.includes('浴室') || cmd.includes('卫生间')

    const physicsAnalysis: PhysicsAnalysis = {
      materials: materialData,
      safetyInstructions: [
        ...(hasWet ? ['⚠️ 湿区操作！地面湿滑，移动速度限制0.3m/s'] : []),
        ...(hasGlass ? ['⚠️ 玻璃表面易碎，力度限制<5N，禁止硬质工具接触'] : []),
      ],
      robotConfig: {
        maxSpeed: hasWet ? 0.3 : (hasGlass ? 0.2 : 0.5),
        forceLimit: Math.min(...materialData.map(m => m.maxForce)),
        mode: hasWet ? '防滑模式' : (hasGlass ? '轻柔模式' : '标准模式'),
      },
    }

    return physicsAnalysis
  }

  // ── 生成空间关系推理 ───────────────────────────────
  const generateSpatialRelations = (roomId: string, cmd: string): SpatialRelation[] => {
    const room = roomSceneData.rooms.find(r => r.id === roomId)
    const roomType = room?.type || ''
    const relations: SpatialRelation[] = []

    // 淋浴房特殊空间关系
    if (cmd.includes('淋浴')) {
      relations.push({
        description: '淋浴房位于主卧卫生间内',
        distance: undefined,
        features: [`面积约2.1㎡`, `地面瓷砖材质，湿态摩擦系数0.20`],
      })

      if (cmd.includes('隔断') || cmd.includes('玻璃')) {
        relations.push({
          description: '玻璃隔断位置关系',
          distance: 0.4,
          features: [
            '邻接马桶区（间距40cm）',
            '邻接洗手台（间距55cm）',
            '⚠️ 马桶区域为湿区，与玻璃隔断形成连续湿滑表面',
          ],
        })
      }

      relations.push({
        description: '电源安全距离',
        distance: 1.8,
        features: ['最近电源插座距淋浴房1.8米', '符合GB 4706.1安全规范（≥1.8m）'],
      })
    }

    // 卧室空间关系
    if (cmd.includes('卧室') || roomType.includes('bedroom')) {
      relations.push({
        description: '卧室空间布局',
        features: [`面积约${room?.area_m2 || 20}㎡`, '相邻房间：书房、主卧卫生间'],
      })

      if (room?.adjacent_rooms) {
        relations.push({
          description: '相邻房间',
          features: room.adjacent_rooms.map((r: string) => `• ${r}`),
        })
      }
    }

    // 厨房空间关系
    if (cmd.includes('厨房')) {
      relations.push({
        description: '厨房台面位置',
        features: ['不锈钢台面邻接灶台', '需注意热源距离', '电源插座分布：4个'],
      })
    }

    return relations
  }

  // ── 发送指令 ─────────────────────────────────────
  const sendCommand = useCallback(async (cmd: string) => {
    if (!cmd.trim()) return
    const userMsg: ChatMessage = { id: msgId, role: 'user', text: cmd }
    const agentMsg: ChatMessage = { id: msgId + 1, role: 'agent', text: '正在分析任务...', result: undefined }
    setMessages(prev => [...prev, userMsg, agentMsg])
    setMsgId(prev => prev + 2)
    setLoading(true)
    setCommand('')

    const roomId = selectedObject?.id?.split('-')[0] || 'room_00'

    try {
      // ── 调用后端 Agent API ──────────────────────────────
      const res = await fetch(API_ENDPOINTS.agent.process, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd, room_id: roomId }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data: AgentResponse = await res.json()

      // 补充 drill_result 缺失字段（前端展示需要）
      if (data.task_type === 'drill' && data.drill_result) {
        const dr = data.drill_result
        if (dr.safe && !dr.warnings) {
          dr.depth_cm = dr.depth_cm ?? 6
          dr.tool = dr.tool ?? '冲击钻 + 6mm麻花钻头'
          dr.warnings = ['避开窗框50cm范围', '避开墙角30cm范围', '确认墙内无水管电线']
          if (!dr.steps) {
            dr.steps = [
              '① 用水平仪确认位置（建议离地150cm）',
              '② 用铅笔标记打孔位置',
              '③ 贴美纹纸保护周围墙面',
              '④ 低速预钻（6mm钻头）',
              '⑤ 插入膨胀螺栓',
              '⑥ 安装挂钩并确认牢固',
            ]
          }
        } else if (!dr.safe && !dr.warnings) {
          dr.warnings = ['禁止钻孔！', '建议改用免钉胶或落地支架']
          dr.steps = null
        }
        // 构造人类可读 reason
        if (!dr.reason || dr.reason.length < 5) {
          dr.reason = dr.safe
            ? '砖墙（非承重墙），可以安全钻孔'
            : '混凝土承重墙，禁止钻孔！'
        }
      }

      // 清洁任务：补全物理分析（前端展示需要）
      if (data.task_type === 'clean' && data.physics_analysis) {
        const mats = data.physics_analysis.materials || []
        const physicsSteps: string[] = []
        const safe = data.physics_analysis.safety_notes || []
        const speed = data.physics_analysis.robotConfig?.maxSpeed || 0.3
        const force = data.physics_analysis.robotConfig?.forceLimit || 5
        physicsSteps.push(`【安全准备】${data.physics_analysis.robotConfig?.mode || '清洁模式'}，移动速度限制${speed}m/s，力度<${force}N`)
        mats.forEach((m: any) => {
          if (m.name?.includes('玻璃') || m.name?.includes('Glass')) {
            physicsSteps.push('【玻璃清洁】橡胶刮刀自上而下刮除水渍，力度<5N')
            physicsSteps.push('【框架擦拭】微纤维布擦拭金属框架，禁用腐蚀性清洁剂')
          } else if (m.name?.includes('瓷砖') || m.name?.includes('Tile')) {
            physicsSteps.push('【地面清洁】从内向外倒退清洁，禁止金属铲刀')
          } else if (m.name?.includes('实木') || m.name?.includes('地板') || m.name?.includes('Wood')) {
            physicsSteps.push('【地板保护】拖布含水量<30%，移动速度0.2m/s')
          }
        })
        physicsSteps.push('【干燥检测】启动气流干燥，5分钟后检测表面湿度<30%')
        physicsSteps.push('【完成确认】拍照记录清洁效果')
        if (!data.steps) data.steps = physicsSteps
      }

      // 更新 agent 消息
      setMessages(prev => prev.map(m =>
        m.id === agentMsg.id
          ? { ...m, text: data.message, result: data }
          : m
      ))
      setActiveWall(data.drill_result?.wall || null)
    } catch (err: any) {
      setMessages(prev => prev.map(m =>
        m.id === agentMsg.id
          ? { ...m, text: `❌ Agent服务离线 (5002不可达)：${err.message}` }
          : m
      ))
    } finally {
      setLoading(false)
    }
  }, [msgId, selectedObject])

  // ── 快捷命令 ─────────────────────────────────────
  const handleExample = (text: string) => {
    setCommand(text)
    inputRef.current?.focus()
  }

  // ── 执行步骤动画（核心缺失逻辑）───────────────────
  const handleExecute = useCallback(() => {
    const lastResult = messages[messages.length - 1]?.result
    const steps = lastResult?.steps
    if (!steps || steps.length === 0 || isExecuting) return

    // 清理旧定时器
    if (timerRef.current) { clearTimeout(timerRef.current); timerRef.current = null }
    setExecResult(null)
    setCurrentStep(-1)
    setIsExecuting(true)
    setExecPhase('初始化机器人...')
    setExecData({ speed: 0, force: 0, friction: 0, temp: 22 })

    // 逐步执行动画
    let step = 0
    const runStep = () => {
      setCurrentStep(step)
      const progress = ((step + 1) / steps.length) * 100
      if (step === 0) setExecPhase('移动到目标位置...')
      else if (step === 1) setExecPhase('传感器校准中...')
      else setExecPhase(`执行步骤 ${step + 1}/${steps.length}...`)
      setExecData({
        speed:    step < 2 ? 0 : 0.3 + step * 0.05,
        force:    step < 2 ? 0 : 3  + step * 0.8,
        friction: step < 2 ? 0 : 0.35 - step * 0.01,
        temp:     22 + step,
      })

      if (step >= steps.length - 1) {
        timerRef.current = setTimeout(() => {
          setIsExecuting(false)
          setExecPhase('执行完成')
          setExecResult({ success: true, message: '✅ 任务执行成功' })
          timerRef.current = setTimeout(() => setExecResult(null), 3500)
        }, 2500)
      } else {
        step++
        timerRef.current = setTimeout(runStep, 2500)
      }
    }

    timerRef.current = setTimeout(runStep, 800)
  }, [messages, isExecuting])

  // ── 清理定时器 ────────────────────────────────────
  useEffect(() => {
    return () => { if (timerRef.current) clearTimeout(timerRef.current) }
  }, [])

  // ── 渲染 ─────────────────────────────────────────
  return (
    <div className="agent-panel">
      {/* ── Header ── */}
      <div className="agent-header">
        <div className="agent-title">🤖 具身AI Agent</div>
        <div className="agent-subtitle">建筑物理世界模型 · Harness层</div>
        <div className="agent-server">
          <span className={'srv-dot ' + serverStatus} />
          <span className="srv-label">
            {serverStatus === 'ok'
              ? `✅ 全部服务在线`
              : serverStatus === 'warn'
                ? `⚡ 核心服务在线 (场景API缓存模式)`
                : `🔄 正在连接服务...`}
          </span>
        </div>
      </div>

      {/* ── 选中房间物理信息 ── */}
      {selectedObject && (
        <div className="agent-section">
          <RoomPhysicsCard roomId={selectedObject.id.split('-')[0] || 'room_00'} />
        </div>
      )}

      {/* ── P1：3D墙体点击联动 ── */}
      {selectedWall && (
        <div className="agent-section wall-info-card" style={{
          borderLeft: `4px solid ${selectedWall.isLoadBearing ? '#E53935' : '#4CAF50'}`,
          background: selectedWall.isLoadBearing ? '#FFF3F3' : '#F1F8E9',
          borderRadius: 8,
          padding: '10px 12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span style={{ fontSize: 18 }}>{selectedWall.isLoadBearing ? '🚫' : '✅'}</span>
            <strong style={{ color: selectedWall.isLoadBearing ? '#C62828' : '#2E7D32' }}>
              {selectedWall.wall === 'north' ? '北墙' : selectedWall.wall === 'south' ? '南墙' : selectedWall.wall === 'east' ? '东墙' : '西墙'}
              {selectedWall.isLoadBearing ? ' · 承重墙' : ' · 非承重墙'}
            </strong>
          </div>
          {selectedWall.isLoadBearing ? (
            <>
              <div style={{ color: '#C62828', fontSize: 13, marginBottom: 4 }}>🛑 严禁钻孔！破坏结构安全！</div>
              <div style={{ fontSize: 12, color: '#666' }}>替代方案：免钉胶挂钩 / 落地式置物架 / 转移至安全墙体</div>
            </>
          ) : (
            <>
              <div style={{ color: '#2E7D32', fontSize: 13, marginBottom: 4 }}>✅ 可安全钻孔（建议深度≤6cm）</div>
              <div style={{ fontSize: 12, color: '#666' }}>工具：冲击钻+6mm钻头 | 注意：避开窗框50cm、墙角30cm</div>
            </>
          )}
          <button
            style={{ marginTop: 8, padding: '4px 12px', border: 'none', borderRadius: 4, background: '#eee', cursor: 'pointer', fontSize: 12 }}
            onClick={() => {
              const wallDir = selectedWall.wall === 'north' ? '北' : selectedWall.wall === 'south' ? '南' : selectedWall.wall === 'east' ? '东' : '西'
              setCommand(`在${wallDir}墙钻孔挂画`)
              inputRef.current?.focus()
            }}
          >
            🧱 测试钻孔指令
          </button>
        </div>
      )}

      {/* ── 命令输入 ── */}
      <div className="agent-section">
        <div className="agent-input-row">
          <input
            ref={inputRef}
            className="agent-input"
            placeholder="输入指令，如：清洁淋浴房的玻璃隔断..."
            value={command}
            onChange={e => setCommand(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                sendCommand(command)
              }
            }}
            disabled={loading}
          />
          <button
            className="agent-send-btn"
            onClick={() => sendCommand(command)}
            disabled={loading || !command.trim()}
          >
            {loading ? '...' : '▶'}
          </button>
        </div>

        {/* 快捷命令示例 */}
        <div className="cmd-examples">
          {COMMAND_EXAMPLES.map((ex, i) => (
            <button key={i} className="cmd-example-btn" onClick={() => handleExample(ex.text)}>
              <span>{ex.icon}</span>
              <span className="ex-text">{ex.text}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ── 对话历史 ── */}
      <div className="agent-chat">
        {messages.length === 0 && (
          <div className="agent-empty">
            <div className="empty-icon">🏗️</div>
            <div className="empty-title">建筑物理世界模型</div>
            <div className="empty-desc">
              <p>点击房间 → 查看物理属性</p>
              <p>输入指令 → Agent智能规划</p>
            </div>
          </div>
        )}

        {messages.map(m => (
          <div key={m.id} className={`chat-msg ${m.role}`}>
            <div className="msg-bubble">
              <div className="msg-text">{m.text}</div>
              {m.result && (
                <InferenceResultDisplay
                  result={m.result}
                  roomName={m.result.room || '未知房间'}
                />
              )}
              {m.role === 'agent' && m.result && (
                <>
                  {/* 步骤时间线 */}
                  {m.result.steps && m.result.steps.length > 0 && (
                    <TimelineStepsView
                      steps={m.result.steps}
                      currentStep={currentStep}
                      isExecuting={isExecuting}
                    />
                  )}
                  {/* 执行按钮 */}
                  {!isExecuting && !execResult && (
                    <button className="exec-btn" onClick={handleExecute}>
                      <span>▶</span> 开始执行
                    </button>
                  )}
                  {/* 实时数据面板 */}
                  {(isExecuting || execData.speed > 0) && (
                    <ExecDataPanel data={execData} phase={execPhase} />
                  )}
                  {/* 执行结果 */}
                  {execResult && (
                    <div className={`exec-result ${execResult.success ? 'success' : 'fail'}`}>
                      {execResult.message}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
    </div>
  )
}
