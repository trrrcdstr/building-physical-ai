import React, { useState, useEffect } from 'react'
import { ErrorBoundary } from './components/ErrorBoundary'
import TopBar from './components/TopBar'
import SceneNavigator from './components/SceneNavigator'
import PhysicsPanel from './components/PhysicsPanel'
import AgentCommandPanel from './components/AgentCommandPanel'
import StatusBar from './components/StatusBar'
import VRSceneSelector from './components/VRSceneSelector'
import RenderingGallery from './components/RenderingGallery'
import { useBuildingStore } from './store/buildingStore'
import { worldObjects } from './data/sceneData'
import './App.css'
import { API_BASE_URL } from './config/api'

// Railway 云端 API 基础地址（netlify.toml 已配置 VITE_API_URL）
const RAILWAY_BASE = 'https://scene-production.up.railway.app'

// 替换 localhost 为 Railway 云端
const cloudUrl = (path: string) => {
  // 如果是 Neural API (5000) -> Railway /neural
  // 如果是 Scene API (5001) -> Railway /scene  
  // 其他保持 Railway 前缀
  return `${RAILWAY_BASE}${path}`
}

// VR全景模式 — 移除3D场景，保留基础store逻辑
export default function App() {
  const activeScene = useBuildingStore(s => s.activeScene)
  const currentSceneType = useBuildingStore(s => s.currentSceneType)
  const loadObjects = useBuildingStore(s => s.loadObjects)

  // VR模式下保留worldObjects加载（兼容旧逻辑）
  useEffect(() => {
    loadObjects(worldObjects as any)
  }, [activeScene])

  return (
    <div className="app-container">

      {/* 顶部导航栏 */}
      <TopBar />

      {/* 皮·骨·肉场景卡片导航 */}
      <SceneNavigator />

      {/* 主区域（三栏叙事流） */}
      <div className="main-body">

        {/* 左栏：VR全景场景（可切换场景 + 物理数据） */}
        <div className="scene-column">
          <VRSceneSelector />
        </div>

        {/* 中栏：物理常识面板（分析层） */}
        <PhysicsPanel />

        {/* 右栏：Agent任务面板（执行层） */}
        <AgentCommandPanel />

      </div>

      {/* 底层组件（始终存在） */}
      <StatusBar />

    </div>
  )
}