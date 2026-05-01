const { app, BrowserWindow, ipcMain, shell, Menu } = require('electron')
const { spawn, exec } = require('child_process')
const path = require('path')
const fs = require('fs')
const http = require('http')

// 日志目录和文件
const LOG_DIR = path.join(__dirname, 'logs')
const LOG_FILE = path.join(LOG_DIR, 'main.log')

// 确保日志目录存在
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true })
}

// 日志函数
function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString()
  const logMessage = `[${timestamp}] [${level}] ${message}\n`
  fs.appendFileSync(LOG_FILE, logMessage)
  console.log(logMessage.trim())
}

// 服务配置
const SERVICES = [
  {
    name: 'Neural Inference',
    script: 'src/neural_inference_server.py',
    args: ['--mode', 'api', '--port', '5000'],
    port: 5000,
    healthPath: '/api/health',
    maxRetries: 3,
    retryDelay: 5000,
  },
  {
    name: 'Scene API',
    script: 'src/four_layer_api.py',
    args: [],
    port: 5001,
    healthPath: '/',
    maxRetries: 3,
    retryDelay: 5000,
  },
  {
    name: 'Agent API',
    script: 'agent_api_simple.py',
    args: [],
    port: 5002,
    healthPath: '/api/health',
    maxRetries: 3,
    retryDelay: 5000,
  },
  {
    name: 'VLA Service',
    script: 'src/vla_server.py',
    args: [],
    port: 5004,
    healthPath: '/api/health',
    maxRetries: 3,
    retryDelay: 5000,
  },
  {
    name: 'Render Server',
    script: 'tmp_http_server.py',
    args: [],
    port: 8888,
    healthPath: null,
    maxRetries: 3,
    retryDelay: 5000,
  },
]

// 服务管理器类
class ServiceManager {
  constructor() {
    this.services = new Map()
    this.statusCallbacks = []
    // __dirname = resources/app in packaged app, resources/ in dev
    this.projectRoot = __dirname
  }

  // 注册状态更新回调
  onServiceStatusUpdate(callback) {
    this.statusCallbacks.push(callback)
  }

  // 通知状态更新
  notifyStatusUpdate(serviceName, status, message) {
    const data = { serviceName, status, message, timestamp: Date.now() }
    this.statusCallbacks.forEach(cb => cb(data))
    log(`Service ${serviceName}: ${status} - ${message}`)
  }

  // 检查端口是否就绪
  checkPortReady(port, healthPath = null) {
    return new Promise((resolve) => {
      if (healthPath) {
        // HTTP健康检查
        const req = http.get(`http://localhost:${port}${healthPath}`, (res) => {
          if (res.statusCode === 200) {
            resolve(true)
          } else {
            resolve(false)
          }
        })
        req.on('error', () => resolve(false))
        req.setTimeout(2000, () => {
          req.destroy()
          resolve(false)
        })
      } else {
        // 简单端口检测（对于没有health端点的服务）
        const net = require('net')
        const client = new net.Socket()
        client.setTimeout(2000)
        client.on('connect', () => {
          client.destroy()
          resolve(true)
        })
        client.on('error', () => resolve(false))
        client.on('timeout', () => {
          client.destroy()
          resolve(false)
        })
        client.connect(port, 'localhost')
      }
    })
  }

  // 启动单个服务
  async startService(config) {
    const { name, script, args, port, healthPath, maxRetries, retryDelay } = config
    
    // 如果服务已存在，先停止
    if (this.services.has(name)) {
      await this.stopService(name)
    }

    let retries = 0
    let started = false

    while (retries <= maxRetries && !started) {
      if (retries > 0) {
        this.notifyStatusUpdate(name, 'retrying', `重试 ${retries}/${maxRetries}...`)
        await new Promise(resolve => setTimeout(resolve, retryDelay))
      }

      try {
        this.notifyStatusUpdate(name, 'starting', '正在启动...')
        
        const scriptPath = path.join(this.projectRoot, script)
        
        // 检查脚本是否存在
        if (!fs.existsSync(scriptPath)) {
          this.notifyStatusUpdate(name, 'error', `脚本不存在: ${script}`)
          return false
        }

        // 启动Python进程
        const proc = spawn('python', [scriptPath, ...args], {
          cwd: this.projectRoot,
          stdio: ['ignore', 'pipe', 'pipe'],
          detached: false,
        })

        // 存储服务信息
        this.services.set(name, {
          process: proc,
          config,
          status: 'starting',
          retryCount: retries,
        })

        // 处理输出
        proc.stdout.on('data', (data) => {
          log(`[${name}] ${data.toString().trim()}`)
        })

        proc.stderr.on('data', (data) => {
          log(`[${name} ERROR] ${data.toString().trim()}`, 'ERROR')
        })

        // 处理进程退出
        proc.on('exit', (code) => {
          log(`Service ${name} exited with code ${code}`, code !== 0 ? 'ERROR' : 'INFO')
          const service = this.services.get(name)
          if (service && service.status !== 'stopping') {
            this.notifyStatusUpdate(name, 'crashed', `进程退出，代码: ${code}`)
            // 自动重启
            setTimeout(() => this.restartService(name), 10000)
          }
        })

        // 等待端口就绪
        let portReady = false
        for (let i = 0; i < 30; i++) {
          await new Promise(resolve => setTimeout(resolve, 1000))
          portReady = await this.checkPortReady(port, healthPath)
          if (portReady) break
        }

        if (portReady) {
          this.notifyStatusUpdate(name, 'running', '运行正常')
          const service = this.services.get(name)
          if (service) {
            service.status = 'running'
          }
          started = true
          // 启动守护进程
          this.startGuardian(name)
          return true
        } else {
          this.notifyStatusUpdate(name, 'error', '端口检测超时')
          proc.kill()
          retries++
        }
      } catch (error) {
        this.notifyStatusUpdate(name, 'error', `启动失败: ${error.message}`)
        retries++
      }
    }

    this.notifyStatusUpdate(name, 'failed', `启动失败，已重试 ${maxRetries} 次`)
    return false
  }

  // 启动守护进程（定期检查服务健康状态）
  startGuardian(serviceName) {
    const check = async () => {
      const service = this.services.get(serviceName)
      if (!service || service.status === 'stopping') return

      const { config } = service
      const isHealthy = await this.checkPortReady(config.port, config.healthPath)
      
      if (!isHealthy && service.status === 'running') {
        this.notifyStatusUpdate(serviceName, 'unhealthy', '服务无响应')
        service.status = 'unhealthy'
        // 重启服务
        setTimeout(() => this.restartService(serviceName), 10000)
      } else if (isHealthy && service.status === 'unhealthy') {
        this.notifyStatusUpdate(serviceName, 'running', '恢复运行')
        service.status = 'running'
      }

      // 继续监控
      if (service && service.status !== 'stopping') {
        setTimeout(check, 10000)
      }
    }

    setTimeout(check, 10000)
  }

  // 重启服务
  async restartService(name) {
    const service = this.services.get(name)
    if (!service) return false

    const { config, retryCount } = service
    
    if (retryCount >= config.maxRetries) {
      this.notifyStatusUpdate(name, 'failed', '超过最大重试次数')
      return false
    }

    service.retryCount++
    this.notifyStatusUpdate(name, 'restarting', '正在重启...')
    
    await this.stopService(name)
    return await this.startService(config)
  }

  // 停止单个服务
  async stopService(name) {
    const service = this.services.get(name)
    if (!service) return

    service.status = 'stopping'
    const { process: proc } = service

    if (proc && !proc.killed) {
      try {
        proc.kill('SIGTERM')
        // 等待进程结束
        await new Promise((resolve) => {
          const timer = setTimeout(() => {
            proc.kill('SIGKILL')
            resolve()
          }, 5000)
          proc.on('exit', () => {
            clearTimeout(timer)
            resolve()
          })
        })
      } catch (error) {
        log(`Error stopping service ${name}: ${error.message}`, 'ERROR')
      }
    }

    this.services.delete(name)
    this.notifyStatusUpdate(name, 'stopped', '已停止')
  }

  // 启动所有服务
  async startAllServices() {
    log('Starting all services...')
    const results = []
    
    for (const config of SERVICES) {
      const result = await this.startService(config)
      results.push({ name: config.name, success: result })
    }

    const allSuccess = results.every(r => r.success)
    log(`All services started. Success: ${allSuccess}`)
    return allSuccess
  }

  // 停止所有服务
  async killAllServices() {
    log('Stopping all services...')
    const names = Array.from(this.services.keys())
    for (const name of names) {
      await this.stopService(name)
    }
    log('All services stopped.')
  }
}

// 创建启动画面HTML
function getSplashHTML() {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Physical AI 世界模型 - 启动中</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0a0a0a;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      overflow: hidden;
    }
    .container {
      width: 600px;
      text-align: center;
    }
    .title {
      font-size: 32px;
      font-weight: 600;
      margin-bottom: 8px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .subtitle {
      font-size: 14px;
      color: #888;
      margin-bottom: 40px;
    }
    .progress-container {
      background: #1a1a1a;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
    }
    .service-item {
      display: flex;
      align-items: center;
      padding: 10px;
      border-bottom: 1px solid #2a2a2a;
      font-size: 14px;
    }
    .service-item:last-child { border-bottom: none; }
    .service-name {
      flex: 1;
      text-align: left;
    }
    .service-status {
      width: 80px;
      text-align: center;
    }
    .status-starting { color: #f59e0b; }
    .status-running { color: #10b981; }
    .status-error { color: #ef4444; }
    .status-failed { color: #ef4444; }
    .status-crashed { color: #f97316; }
    .status-retrying { color: #f59e0b; }
    .spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid #333;
      border-top-color: #667eea;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .footer {
      margin-top: 20px;
      font-size: 12px;
      color: #666;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="title">Physical AI 世界模型</div>
    <div class="subtitle">正在初始化服务，请稍候...</div>
    <div class="progress-container" id="serviceList"></div>
    <div class="footer">版本 1.0.0</div>
  </div>
  
  <script>
    const { ipcRenderer } = require('electron')
    
    const services = [
      { name: 'Neural Inference', status: 'pending' },
      { name: 'Scene API', status: 'pending' },
      { name: 'Agent API', status: 'pending' },
      { name: 'VLA Service', status: 'pending' },
      { name: 'Render Server', status: 'pending' },
    ]
    
    function render() {
      const container = document.getElementById('serviceList')
      container.innerHTML = services.map(s => {
        let statusHtml = ''
        if (s.status === 'pending') {
          statusHtml = '<span class="service-status" style="color:#666">等待中</span>'
        } else if (s.status === 'starting' || s.status === 'retrying' || s.status === 'restarting') {
          statusHtml = '<span class="service-status status-starting"><span class="spinner"></span> 启动中</span>'
        } else if (s.status === 'running') {
          statusHtml = '<span class="service-status status-running">✅ 成功</span>'
        } else if (s.status === 'error' || s.status === 'failed' || s.status === 'crashed') {
          statusHtml = '<span class="service-status status-error">❌ 失败</span>'
        }
        return \`
          <div class="service-item">
            <span class="service-name">\${s.name}</span>
            \${statusHtml}
          </div>
        \`
      }).join('')
    }
    
    render()
    
    ipcRenderer.on('service-status', (_, data) => {
      const service = services.find(s => s.name === data.serviceName)
      if (service) {
        service.status = data.status
        render()
      }
    })
  </script>
</body>
</html>
  `
}

// 全局变量
let mainWindow = null
let splashWindow = null
let serviceManager = null
let allServicesReady = false

// IPC处理
ipcMain.handle('open-external', (_, url) => {
  shell.openExternal(url)
})

ipcMain.handle('get-version', () => {
  return app.getVersion()
})

ipcMain.on('window-minimize', () => {
  if (mainWindow) mainWindow.minimize()
})

ipcMain.on('window-maximize', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize()
    } else {
      mainWindow.maximize()
    }
  }
})

ipcMain.on('window-close', () => {
  if (mainWindow) mainWindow.close()
})

// 创建主窗口
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    title: 'Physical AI 世界模型',
    backgroundColor: '#0a0a0a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    show: false,
    icon: path.join(__dirname, '../web-app/public/icon.ico'),
  })

  // 移除默认菜单
  Menu.setApplicationMenu(null)

  // 加载URL
  const isDev = process.argv.includes('--dev')
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000')
  } else {
    // 打包模式：加载本地文件
    const indexPath = path.join(__dirname, '../web-app/dist/index.html')
    if (fs.existsSync(indexPath)) {
      mainWindow.loadFile(indexPath)
    } else {
      // 如果dist不存在，显示错误页面
      mainWindow.loadURL('data:text/html,<h1 style="color:white;background:#0a0a0a;padding:50px;text-align:center;">前端文件未找到，请先运行 npm run build</h1>')
    }
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 创建启动画面
function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 700,
    height: 500,
    frame: false,
    resizable: false,
    transparent: false,
    backgroundColor: '#0a0a0a',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    center: true,
    skipTaskbar: true,
  })

  // 加载启动画面HTML
  const splashHTML = getSplashHTML()
  splashWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(splashHTML)}`)

  splashWindow.on('closed', () => {
    splashWindow = null
  })
}

// 当所有服务就绪后显示主窗口
function showMainWindow() {
  if (splashWindow) {
    splashWindow.close()
    splashWindow = null
  }
  
  if (mainWindow) {
    mainWindow.show()
    mainWindow.focus()
  }
  
  allServicesReady = true
}

// App事件
app.whenReady().then(async () => {
  log('App starting...')
  
  // 创建服务管理器
  serviceManager = new ServiceManager()
  
  // 监听服务状态更新
  serviceManager.onServiceStatusUpdate((data) => {
    // 转发到启动画面
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.webContents.send('service-status', data)
    }
    // 转发到主窗口
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('service-status', data)
    }
  })

  // 创建窗口
  createMainWindow()
  createSplashWindow()

  // 启动所有服务
  const success = await serviceManager.startAllServices()
  
  if (success) {
    log('All services started successfully.')
    setTimeout(showMainWindow, 1000)
  } else {
    log('Some services failed to start.', 'WARN')
    // 即使有服务失败，也显示主窗口（用户可以手动重启）
    setTimeout(showMainWindow, 2000)
  }
})

// 所有窗口关闭时退出（Windows/Linux）
app.on('window-all-closed', async () => {
  if (serviceManager) {
    await serviceManager.killAllServices()
  }
  app.quit()
})

// 应用退出前清理
app.on('before-quit', async (event) => {
  if (serviceManager) {
    event.preventDefault()
    await serviceManager.killAllServices()
    app.exit()
  }
})

// 处理进程信号
process.on('SIGTERM', async () => {
  log('Received SIGTERM', 'WARN')
  if (serviceManager) {
    await serviceManager.killAllServices()
  }
  app.exit()
})

process.on('SIGINT', async () => {
  log('Received SIGINT', 'WARN')
  if (serviceManager) {
    await serviceManager.killAllServices()
  }
  app.exit()
})

log('Main process loaded.')
