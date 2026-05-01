/**
 * API 配置模块
 * 支持本地开发和云端部署
 */

// 从环境变量读取后端地址，默认为本地
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
export const AGENT_API_URL = import.meta.env.VITE_AGENT_API_URL || 'http://localhost:5002'
export const SCENE_API_URL = import.meta.env.VITE_SCENE_API_URL || 'http://localhost:5001'
export const VLA_API_URL = import.meta.env.VITE_VLA_API_URL || 'http://localhost:5004'

// API 端点配置
export const API_ENDPOINTS = {
  // Neural Inference (5000)
  neural: {
    health: `${API_BASE_URL}/api/health`,
    predictPhysics: `${API_BASE_URL}/api/predict_physics`,
    predictRelations: `${API_BASE_URL}/api/predict_relations`,
    encodeScene: `${API_BASE_URL}/api/encode_scene`,
    scene: `${API_BASE_URL}/api/scene`,
    relation: `${API_BASE_URL}/api/relation`,
    relationBatch: `${API_BASE_URL}/api/relation_batch`,
    physicsQuery: `${API_BASE_URL}/api/physics/query`,
  },
  // Agent API (5002)
  agent: {
    health: `${AGENT_API_URL}/api/health`,
    process: `${AGENT_API_URL}/api/agent/process`,
    checkDrill: `${AGENT_API_URL}/api/constraint/check-drill`,
    spatialQuery: `${AGENT_API_URL}/api/spatial/query`,
    locateObject: `${AGENT_API_URL}/api/spatial/locate-object`,
    findPath: `${AGENT_API_URL}/api/spatial/find-path`,
    stats: `${AGENT_API_URL}/api/data/stats`,
    walls: `${AGENT_API_URL}/api/walls`,
  },
  // Scene API (5001)
  scene: {
    health: `${SCENE_API_URL}/`,
    scene: `${SCENE_API_URL}/api/scene`,
  },
  // VLA Service (5004)
  vla: {
    health: `${VLA_API_URL}/api/health`,
    classify: `${VLA_API_URL}/api/classify`,
  },
}

// 健康检查配置
export const HEALTH_CHECK_CONFIG = {
  neural: { url: API_ENDPOINTS.neural.health, interval: 10000 },
  agent: { url: API_ENDPOINTS.agent.health, interval: 10000 },
  scene: { url: API_ENDPOINTS.scene.health, interval: 10000 },
  vla: { url: API_ENDPOINTS.vla.health, interval: 10000 },
}
