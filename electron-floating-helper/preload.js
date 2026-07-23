const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // 拖动
  startDragging: () => ipcRenderer.send('start-drag'),
  
  // 系统信息
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // 设置
  saveConfig: (config) => ipcRenderer.send('save-config', config),
  
  openSettings: () => ipcRenderer.send('open-settings'),
  closeSettings: () => ipcRenderer.send('close-settings'),
  getConfig: () => ipcRenderer.invoke('get-config'),
  updateSetting: (key, value) => ipcRenderer.send('update-setting', { key, value }),

  // 监听配置变化（可选，如果需要主窗口也被动更新）
  onConfigUpdated: (callback) => ipcRenderer.on('config-updated', (event, newConfig) => callback(newConfig)),

  minimizeWindow: () => ipcRenderer.send('window-min'),
  closeWindow: () => ipcRenderer.send('window-close'),
  // preload.js 补充
  onUpdateSystemInfo: (callback) => ipcRenderer.on('system-info', (event, value) => callback(value)),
  
  toggleExpand: (isExpanded) => ipcRenderer.invoke('toggle-expand', isExpanded),
  chatWithDeepSeek: (text) => ipcRenderer.invoke('chat-with-deepseek', text),
  getChatHistory: () => ipcRenderer.invoke('get-chat-history'),
  clearChatHistory: (range) => ipcRenderer.invoke('clear-chat-history', range),
  // 快捷键
  registerShortcut: (key) => ipcRenderer.send('register-shortcut', key),
  unregisterShortcut: (key) => ipcRenderer.send('unregister-shortcut', key),

  // 监听吸附状态
  onDockState: (callback) => ipcRenderer.on('dock-state', (event, state) => callback(state))
});