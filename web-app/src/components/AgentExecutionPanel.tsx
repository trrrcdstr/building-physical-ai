/**
 * AgentExecutionPanel.tsx
 *
 * 具身执行面板 — 皮·骨·肉"肉"层核心界面
 *
 * 功能：
 * 1. 任务选择（钻孔/搬运/清洁/巡检）
 * 2. 执行状态实时显示（步骤进度条）
 * 3. 机器人状态监控（模拟数据）
 * 4. Harness 安全约束反馈
 * 5. 执行结果日志
 *
 * 数据来源：Agent API (port 5002)
 */

import React, { useState, useEffect, useCallback, useRef } from 'react'
import { useBuildingStore } from '../store/buildingStore'
import { inferMaterialFromTask, MATERIAL_PHYSICS_DB } from '../shared/materialPhysicsDb'
import { API_ENDPOINTS } from '../config/api'
import './AgentExecutionPanel.css'

// ════════════════════════════════════════════════
//  类型
// ════════════════════════════════════════════════

interface TaskStep {
  id: number
  label: string
  action: string
  duration_s: number
  status: 'pending' | 'active' | 'done' | 'failed'
  detail?: string
}

interface RobotStatus {
  joint_angles: number[]     // 6轴关节角度
  end_effector: [number, number, number]  // 末端位置 XYZ
  tool: string              // 当前工具
  force: number              // 末端力传感器 N
  status: 'idle' | 'moving' | 'executing' | 'error'
  confidence: number         // 任务置信度
}

interface HarnessResult {
  allowed: boolean
  reason: string
  constraints: {
    type: string
    passed: boolean
    message: string
  }[]
}

// ════════════════════════════════════════════════
//  任务模板
// ════════════════════════════════════════════════

const TASK_TEMPLATES = [
  {
    id: 'drill',
    icon: '🔨',
    label: '智能钻孔',
    desc: '承重墙检测 + 最优位置推荐 + 安全钻孔',
    steps: [
      { id: 1, label: '扫描墙面', action: 'scan_wall', duration_s: 3 },
      { id: 2, label: '材质识别', action: 'detect_material', duration_s: 2 },
      { id: 3, label: '安全检测', action: 'harness_check', duration_s: 1 },
      { id: 4, label: '定位标记', action: 'mark_position', duration_s: 2 },
      { id: 5, label: '执行钻孔', action: 'drill', duration_s: 4 },
      { id: 6, label: '质量检测', action: 'quality_check', duration_s: 2 },
    ],
  },
  {
    id: 'move',
    icon: '📦',
    label: '物体搬运',
    desc: '抓取策略 + 路径规划 + 放置执行',
    steps: [
      { id: 1, label: '识别物体', action: 'detect_object', duration_s: 2 },
      { id: 2, label: '抓取规划', action: 'grasp_planning', duration_s: 3 },
      { id: 3, label: '运动规划', action: 'path_planning', duration_s: 2 },
      { id: 4, label: '执行搬运', action: 'execute_move', duration_s: 5 },
      { id: 5, label: '放置检测', action: 'place_check', duration_s: 2 },
    ],
  },
  {
    id: 'clean',
    icon: '🧹',
    label: '智能清洁',
    desc: '污渍识别 + 清洁路径 + 工具选择',
    steps: [
      { id: 1, label: '环境扫描', action: 'scan_environment', duration_s: 3 },
      { id: 2, label: '污渍检测', action: 'detect_stains', duration_s: 2 },
      { id: 3, label: '路径规划', action: 'clean_path_plan', duration_s: 2 },
      { id: 4, label: '执行清洁', action: 'execute_clean', duration_s: 6 },
      { id: 5, label: '效果评估', action: 'cleaning_eval', duration_s: 2 },
    ],
  },
  {
    id: 'inspect',
    icon: '👁️',
    label: '场景巡检',
    desc: '自主导航 + 异常检测 + 报告生成',
    steps: [
      { id: 1, label: '环境建模', action: 'build_map', duration_s: 4 },
      { id: 2, label: '路径规划', action: 'inspect_path', duration_s: 2 },
      { id: 3, label: '自主巡检', action: 'autonomous_inspect', duration_s: 8 },
      { id: 4, label: '异常分析', action: 'anomaly_detect', duration_s: 3 },
      { id: 5, label: '生成报告', action: 'generate_report', duration_s: 2 },
    ],
  },
]

// 模拟机器人状态
function generateRobotStatus(): RobotStatus {
  const statuses: RobotStatus['status'][] = ['idle', 'moving', 'executing']
  return {
    joint_angles: Array.from({ length: 6 }, () => Math.round((Math.random() * 180 - 90) * 10) / 10),
    end_effector: [
      Math.round((Math.random() * 100 - 50) * 10) / 10,
      Math.round((Math.random() * 80 + 10) * 10) / 10,
      Math.round((Math.random() * 60 - 10) * 10) / 10,
    ],
    tool: ['drill', 'gripper', 'vacuum', 'camera'][Math.floor(Math.random() * 4)],
    force: Math.round(Math.random() * 30 * 10) / 10,
    status: statuses[Math.floor(Math.random() * 3)],
    confidence: Math.round((0.75 + Math.random() * 0.25) * 100) / 100,
  }
}

// ════════════════════════════════════════════════
//  组件
// ════════════════════════════════════════════════

export default function AgentExecutionPanel() {
  const [selectedTask, setSelectedTask] = useState<string>('drill')
  const [isExecuting, setIsExecuting] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [steps, setSteps] = useState<TaskStep[]>([])
  const [robotStatus, setRobotStatus] = useState<RobotStatus>(generateRobotStatus())
  const [harnessResult, setHarnessResult] = useState<HarnessResult | null>(null)
  const [physicsAnalysis, setPhysicsAnalysis] = useState<any>(null)
  const [execLog, setExecLog] = useState<string[]>([])
  const [agentConnected, setAgentConnected] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  // 30秒轮询
  useEffect(() => {
    const id = setInterval(() => setRefreshKey(p => p + 1), 30000)
    return () => clearInterval(id)
  }, [])

  // Agent API 健康检查
  useEffect(() => {
    fetch(API_ENDPOINTS.agent.health)
      .then(r => { if (r.ok) setAgentConnected(true) })
      .catch(() => setAgentConnected(false))
  }, [refreshKey])

  // 机器人状态模拟（执行时高频更新）
  useEffect(() => {
    if (!isExecuting) return
    const id = setInterval(() => setRobotStatus(generateRobotStatus()), 1000)
    return () => clearInterval(id)
  }, [isExecuting])

  // 加载任务模板
  const taskTemplate = TASK_TEMPLATES.find(t => t.id === selectedTask)!

  // 开始执行 - 调用后端 Agent API
  const handleStart = useCallback(async () => {
    const template = TASK_TEMPLATES.find(t => t.id === selectedTask)!
    const initialSteps: TaskStep[] = template.steps.map(s => ({ ...s, status: 'pending' as const }))
    setSteps(initialSteps)
    setIsExecuting(true)
    setCurrentStep(0)
    // 获取材质物理数据
    const materialKey = inferMaterialFromTask(template.desc)
    const physicsData = MATERIAL_PHYSICS_DB[materialKey]
    setPhysicsAnalysis(physicsData)
    setHarnessResult(null)
    setExecLog([`[${new Date().toLocaleTimeString()}] 开始执行: ${template.label}`])

    try {
      // 调用后端 Agent API 获取真实执行计划
      const command = template.id === 'drill' ? '在东墙钻一个孔' :
                      template.id === 'clean' ? '清洁淋浴玻璃' :
                      template.id === 'move' ? '搬运沙发到客厅' :
                      '巡检房间'

      setExecLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] 正在调用 Agent API...`])

      const response = await fetch(API_ENDPOINTS.agent.process, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      })

      if (!response.ok) {
        throw new Error(`Agent API 错误: ${response.status}`)
      }

      const agentResult = await response.json()
      setExecLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] Agent API 返回: ${agentResult.result || 'success'}`])

      // 如果有 Harness 约束结果，显示它
      if (agentResult.harness_constraints) {
        const constraints = agentResult.harness_constraints.map((c: any) => ({
          type: c.type,
          passed: c.passed,
          message: c.message
        }))
        setHarnessResult({
          allowed: agentResult.safe !== false,
          reason: agentResult.reason || '安全检测完成',
          constraints
        })
      }

      // 逐步骤执行（结合后端返回的步骤）
      const backendSteps = agentResult.steps || initialSteps

      for (let i = 0; i < backendSteps.length; i++) {
        setCurrentStep(i)
        setSteps(prev => prev.map((s, idx) =>
          idx === i ? { ...s, status: 'active' as const } : s
        ))
        setExecLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] 步骤 ${i + 1}: ${backendSteps[i].label || backendSteps[i].action}`])

        // 模拟执行时间
        await new Promise(resolve => setTimeout(resolve, (backendSteps[i].duration_s || 2) * 600))

        setSteps(prev => prev.map((s, idx) =>
          idx === i ? { ...s, status: 'done' as const } : s
        ))
      }

      setExecLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] 执行完成！`])

    } catch (error) {
      console.error('Agent API 调用失败:', error)
      setExecLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] ❌ Agent API 错误: ${error instanceof Error ? error.message : String(error)}`])
      // 降级到本地模拟执行
      setExecLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] 降级到本地模拟...`])

      for (let i = 0; i < initialSteps.length; i++) {
        setCurrentStep(i)
        setSteps(prev => prev.map((s, idx) =>
          idx === i ? { ...s, status: 'active' as const } : s
        ))
        await new Promise(resolve => setTimeout(resolve, initialSteps[i].duration_s * 600))
        setSteps(prev => prev.map((s, idx) =>
          idx === i ? { ...s, status: 'done' as const } : s
        ))
      }
    }

    setIsExecuting(false)
  }, [selectedTask])

  // 停止执行
  const handleStop = useCallback(() => {
    setIsExecuting(false)
    setSteps(prev => prev.map(s =>
      s.status === 'active' ? { ...s, status: 'failed' as const } : s
    ))
    setExecLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] 用户停止执行`])
  }, [])

  // 计算进度
  const doneCount = steps.filter(s => s.status === 'done').length
  const progress = steps.length > 0 ? (doneCount / steps.length) * 100 : 0

  const toolIcon: Record<string, string> = {
    drill: '🔩', gripper: '🤚', vacuum: '🧹', camera: '📷',
  }

  return (
    <div className="agent-exec-panel">
      {/* 顶部标题 */}
      <div className="exec-header">
        <div className="exec-title">
          <span className="exec-title-icon">🦾</span>
          <span>具身执行</span>
        </div>
        <div className={`exec-badge ${agentConnected ? 'online' : 'offline'}`}>
          <span className="badge-dot" />
          {agentConnected ? 'Agent在线' : 'Agent离线'}
        </div>
      </div>

      {/* 任务选择卡片 */}
      <div className="task-cards">
        {TASK_TEMPLATES.map(task => (
          <div
            key={task.id}
            className={`task-card ${selectedTask === task.id ? 'active' : ''}`}
            onClick={() => !isExecuting && setSelectedTask(task.id)}
          >
            <div className="task-card-icon">{task.icon}</div>
            <div className="task-card-name">{task.label}</div>
            <div className="task-card-desc">{task.desc}</div>
          </div>
        ))}
      </div>

      {/* 执行控制 */}
      <div className="exec-controls">
        {!isExecuting ? (
          <button className="exec-start-btn" onClick={handleStart}>
            <span>▶</span> 开始执行
          </button>
        ) : (
          <button className="exec-stop-btn" onClick={handleStop}>
            <span>■</span> 停止
          </button>
        )}
        <div className="exec-progress-bar">
          <div className="exec-progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="exec-progress-text">
          {doneCount}/{steps.length} 步骤 ({progress.toFixed(0)}%)
        </div>
      </div>

      {/* 步骤时间线 */}
      <div className="step-timeline">
        {steps.map((step, i) => (
          <div key={step.id} className={`step-item ${step.status}`}>
            <div className="step-dot">
              {step.status === 'done' ? '✓' :
               step.status === 'active' ? '▶' :
               step.status === 'failed' ? '✗' : ''}
            </div>
            <div className="step-info">
              <div className="step-label">{step.label}</div>
              <div className="step-meta">{step.action} · {step.duration_s}s</div>
            </div>
          </div>
        ))}
      </div>

      {/* Harness 安全反馈 */}
      {harnessResult && (
        <div className={`harness-result ${harnessResult.allowed ? 'allowed' : 'denied'}`}>
          <div className="harness-title">
            {harnessResult.allowed ? '✅ 安全检测通过' : '🛑 安全检测拒绝'}
          </div>
          <div className="harness-reason">{harnessResult.reason}</div>
          <div className="harness-constraints">
            {harnessResult.constraints.map((c, i) => (
              <div key={i} className={`constraint-item ${c.passed ? 'pass' : 'fail'}`}>
                {c.passed ? '✅' : '❌'} {c.type}: {c.message}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 机器人状态 */}
      <div className="robot-status-panel">
        <div className="robot-status-header">
          <span>🤖 机器人状态</span>
          <span className={`robot-state-badge ${robotStatus.status}`}>
            {robotStatus.status}
          </span>
        </div>
        <div className="robot-metrics">
          <div className="metric">
            <div className="metric-label">工具</div>
            <div className="metric-value">
              {toolIcon[robotStatus.tool] || '🔧'} {robotStatus.tool}
            </div>
          </div>
          <div className="metric">
            <div className="metric-label">末端力</div>
            <div className="metric-value">{robotStatus.force}N</div>
          </div>
          <div className="metric">
            <div className="metric-label">置信度</div>
            <div className="metric-value">{(robotStatus.confidence * 100).toFixed(0)}%</div>
          </div>
          <div className="metric wide">
            <div className="metric-label">末端位置</div>
            <div className="metric-value mono">
              {robotStatus.end_effector.map(v => v.toFixed(1)).join(', ')}
            </div>
          </div>
        </div>
        {/* 关节角度条形图 */}
        <div className="joint-bars">
          {robotStatus.joint_angles.map((angle, i) => (
            <div key={i} className="joint-bar-row">
              <span className="joint-label">J{i + 1}</span>
              <div className="joint-bar-bg">
                <div
                  className="joint-bar-fill"
                  style={{ width: `${Math.abs(angle) / 1.8}%` }}
                />
              </div>
              <span className="joint-value">{angle.toFixed(1)}°</span>
            </div>
          ))}
        </div>
      </div>

      {/* 执行日志 */}
      <div className="exec-log">
        <div className="log-header">📋 执行日志</div>
        <div className="log-entries">
          {execLog.slice(-8).map((entry, i) => (
            <div key={i} className="log-entry">{entry}</div>
          ))}
        </div>
      </div>
    </div>
  )
}
