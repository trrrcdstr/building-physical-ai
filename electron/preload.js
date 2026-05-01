// preload.js - 安全暴露IPC通道给渲染进程
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // 服务状态
  onServiceStatus: (callback) => ipcRenderer.on('service-status', (_, data) => callback(data)),
  
  // 打开外部链接
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // 获取版本
  getVersion: () => ipcRenderer.invoke('get-version'),
  
  // 最小化/最大化/关闭
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close'),
})
