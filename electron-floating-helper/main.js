const { app, BrowserWindow, globalShortcut, Tray, Menu, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');
const si = require('systeminformation');
const { spawn } = require('child_process');

const store = new Store();

let localConfig = {};
try {
  const configPath = path.join(__dirname, 'config.json');
  if (require('fs').existsSync(configPath)) {
    localConfig = JSON.parse(require('fs').readFileSync(configPath, 'utf8'));
  }
} catch (e) { console.log("本地配置读取失败"); }

const DEFAULTS = {
  width: 300, height: 170, opacity: 0.8, alwaysOnTop: true, autoStart: false, zoomFactor: 1.0, theme: 'light', shortcut: 'Ctrl+Alt+Q'
};

let voiceProcess = null;
let voiceStopTimer = null;
function startVoiceEngine() {
    const isPackaged = app.isPackaged;
    const baseDir = isPackaged 
        ? path.join(process.resourcesPath, 'voice_engine') 
        : path.join(__dirname, 'voice_engine');
    const batPath = path.join(baseDir, 'start_voice.bat');

    voiceProcess = spawn('cmd.exe', ['/c', batPath], { cwd: baseDir, windowsHide: true });
    voiceProcess.stdout.on('data', (data) => console.log(`[语音引擎]: ${data}`));
    voiceProcess.stderr.on('data', (data) => console.error(`[语音引擎错误]: ${data}`));
}

let config = { ...DEFAULTS, ...localConfig, ...store.get('config') };
let mainWindow;
let settingsWindow = null;
let tray;

function stopVoiceEngine() {
    if (voiceProcess) {
        console.log("正在关闭语音引擎...");
        // Windows 下使用 taskkill /F /T 确保杀掉 cmd 及其启动的 python 子进程
        const { exec } = require('child_process');
        exec(`taskkill /pid ${voiceProcess.pid} /T /F`, (err) => {
            if (err) console.error("强制关闭引擎失败:", err);
            voiceProcess = null;
        });
    }
}

function createWindow() {
  const currentWidth = Math.round(config.width * config.zoomFactor);
  const currentHeight = Math.round(config.height * config.zoomFactor);

  mainWindow = new BrowserWindow({
    width: currentWidth, 
    height: currentHeight, 
    frame: false,
    alwaysOnTop: config.alwaysOnTop,
    transparent: true, 
    skipTaskbar: true, 
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), 
      nodeIntegration: false, 
      contextIsolation: true
    }
  });
  mainWindow.loadFile('index.html');
  mainWindow.setOpacity(config.opacity);
  
  // === 【重构】完美的吸附与防抖拖拽逻辑 ===
  let isDocked = false;      
  let dockSide = null; 
  let isResizing = false;
  let snapTimeout = null; // 防抖定时器
  const DOCK_THRESHOLD = 20; 
  const BALL_SIZE = 60; 

  mainWindow.on('move', () => {
    if (isResizing) return;
    const bounds = mainWindow.getBounds();
    const { workArea } = require('electron').screen.getDisplayNearestPoint({ x: bounds.x, y: bounds.y });
    
    const distLeft = bounds.x - workArea.x;
    const distRight = (workArea.x + workArea.width) - (bounds.x + bounds.width);

    if (!isDocked) {
      if (distLeft < DOCK_THRESHOLD) {
        dockWindow('left', workArea.x, bounds.y);
      } else if (distRight < DOCK_THRESHOLD) {
        dockWindow('right', workArea.x + workArea.width - BALL_SIZE, bounds.y);
      }
    } else {
      let pullDistance = 0;
      if (dockSide === 'left') {
        pullDistance = bounds.x - workArea.x;
      } else if (dockSide === 'right') {
        pullDistance = (workArea.x + workArea.width) - (bounds.x + bounds.width);
      }

      if (pullDistance > 45) {
        // 用户铁了心要拉出来，直接恢复
        clearTimeout(snapTimeout);
        restoreWindow(bounds.x, bounds.y);
      } else if (pullDistance !== 0) {
        // 用户在拖拽中（还没拉出足够距离），【千万不要在这时设 bounds 抢鼠标】
        // 开启防抖：如果停顿 150ms 没动静，说明松手了，才自动弹回边缘
        clearTimeout(snapTimeout);
        snapTimeout = setTimeout(() => {
          if (isDocked && mainWindow && !mainWindow.isDestroyed()) {
            const targetX = dockSide === 'left' ? workArea.x : (workArea.x + workArea.width - BALL_SIZE);
            mainWindow.setBounds({ x: Math.round(targetX), y: bounds.y, width: BALL_SIZE, height: BALL_SIZE });
          }
        }, 150);
      }
    }
  });

  function dockWindow(side, x, y) {
    isDocked = true; dockSide = side; isResizing = true;
    mainWindow.webContents.send('dock-state', `dock-${side}`);
    mainWindow.setBounds({ x: Math.round(x), y: Math.round(y), width: BALL_SIZE, height: BALL_SIZE });
    mainWindow.setAlwaysOnTop(true);
    setTimeout(() => { isResizing = false; }, 200);
  }

  function restoreWindow(currentX, currentY) {
    isDocked = false; isResizing = true;
    mainWindow.webContents.send('dock-state', 'normal');

    const originalW = Math.round(config.width * config.zoomFactor);
    const originalH = Math.round(config.height * config.zoomFactor);
    const { workArea } = require('electron').screen.getDisplayNearestPoint({ x: currentX, y: currentY });
    
    // 【核心修复】计算正确的生成坐标，防止碰到右边缘瞬间再次吸附
    let newX = currentX;
    if (dockSide === 'right') newX = currentX + BALL_SIZE - originalW; // 右边缘对齐
    
    const BUFFER = DOCK_THRESHOLD + 15; // 弹出的安全缓冲距离
    if (dockSide === 'left' && newX < workArea.x + BUFFER) {
      newX = workArea.x + BUFFER;
    } else if (dockSide === 'right' && (newX + originalW) > workArea.x + workArea.width - BUFFER) {
      newX = workArea.x + workArea.width - originalW - BUFFER;
    }

    dockSide = null;
    mainWindow.setResizable(true);
    mainWindow.setBounds({ x: Math.round(newX), y: currentY, width: originalW, height: originalH });
    mainWindow.setResizable(false);
    
    // 给长一点的冷却时间，防止恢复瞬间判定触发 move
    setTimeout(() => { isResizing = false; }, 600);
  }
}

function createSettingsWindow() {
  if (settingsWindow && !settingsWindow.isDestroyed()) { settingsWindow.focus(); return; }
  settingsWindow = new BrowserWindow({
    width: 580, height: 500, frame: false, parent: mainWindow, resizable: false, backgroundColor: '#ffffff',
    webPreferences: { preload: path.join(__dirname, 'preload.js') }
  });
  settingsWindow.loadFile('settings.html');
}

function createTray() {
  const iconPath = path.join(__dirname, 'assets/nailong.ico'); 
  tray = new Tray(iconPath);
  const contextMenu = Menu.buildFromTemplate([
    { label: '显示助手', click: () => mainWindow.show() },
    { label: '设置', click: () => createSettingsWindow() },
    { type: 'separator' },
    { label: '退出', click: () => { app.isQuiting = true; app.quit(); } }
  ]);
  tray.setToolTip('涂维兮御用助手');
  tray.setContextMenu(contextMenu);
  tray.on('click', () => mainWindow.isVisible() ? mainWindow.focus() : mainWindow.show());
}

async function getSystemData() {
  try {
    const cpu = await si.currentLoad();
    const mem = await si.mem();
    let totalRx = 0, totalTx = 0;
    try {
        const net = await si.networkStats();
        if (net && net.length > 0) {
          net.forEach(iface => { totalRx += (iface.rx_sec || 0); totalTx += (iface.tx_sec || 0); });
        }
    } catch (netErr) {}
    return {
      cpu: Math.round(cpu.currentLoad),
      memory: `${((mem.active / mem.total) * 100).toFixed(1)}%`,
      download: (totalRx / 1024).toFixed(1) + ' KB/s', upload: (totalTx / 1024).toFixed(1) + ' KB/s'
    };
  } catch (e) { return null; }
}

function startSystemUpdate() {
  const run = async () => {
    const data = await getSystemData();
    if (data && mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send('system-info', data);
    setTimeout(run, 1000);
  };
  run();
}

function registerShortcuts() {
  globalShortcut.unregisterAll();
  if (config.shortcut) {
    try {
      globalShortcut.register(config.shortcut, () => {
        if (mainWindow && !mainWindow.isDestroyed()) mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
      });
    } catch (e) {}
  }
}

app.whenReady().then(() => {
  ipcMain.handle('get-config', () => config);
  ipcMain.handle('get-system-info', async () => getSystemData());
  ipcMain.on('open-settings', createSettingsWindow);
  ipcMain.on('close-settings', () => settingsWindow?.close());
  ipcMain.on('window-min', () => mainWindow.hide());
  ipcMain.on('window-close', () => { app.quit(); });

  ipcMain.handle('toggle-expand', (event, isExpanded) => {
    const bounds = mainWindow.getBounds();
    const originalW = Math.round(config.width * config.zoomFactor);
    const originalH = Math.round(config.height * config.zoomFactor);
    const targetHeight = isExpanded ? Math.round(500 * config.zoomFactor) : originalH;
    if (bounds.width === 60) return false; 
    mainWindow.setResizable(true);
    mainWindow.setSize(originalW, targetHeight);
    mainWindow.setResizable(false);

    if (isExpanded) {
      if (voiceStopTimer) clearTimeout(voiceStopTimer);
      if (!voiceProcess) {
          console.log("检测到面板展开，正在按需启动语音引擎...");
          startVoiceEngine();
      }
  } else {
      console.log("检测到面板收缩，正在释放内存...");
      voiceStopTimer = setTimeout(() => {
          stopVoiceEngine();
      }, 14000);
  }
});

  // 在 main.js 顶部引入依赖的地方，额外创建一个用于存储聊天的实例
const Store = require('electron-store');
const store = new Store(); // 现有的配置 store
const chatStore = new Store({ name: 'chat-history' }); // 新增：专门存聊天记录的本地文件

// ... (其他代码保持不变) ...

// 1. 新增一个接口，让前端能够获取历史记录
ipcMain.handle('get-chat-history', () => {
  // 默认返回一个空数组，如果是第一次打开
  return chatStore.get('messages', []);
});

// 2. 修改你原有的 deepseek 聊天接口
ipcMain.handle('chat-with-deepseek', async (event, text) => {
  try {
    // 每次聊天前，先从本地读取历史记录
    const history = chatStore.get('messages', []);
    const apiMessages = [
      { 
        role: "system", 
        content: "你是一个可爱，幽默的助手奶龙，但你也不需要太代入这个奶龙角色。除非必要，没太多必要的可以不要说，否则尽量控制在100字以内。" 
      },...history.map(m => ({ role: m.role, content: m.content })),
      { role: "user", content: text }
    ];
    // 把用户的最新发言加进历史记录
    history.push({ role: "user", content: text, timestamp: Date.now() });

    // 这里替换成你实际使用的 DeepSeek API 地址和你的 API Key
    const response = await fetch('https://api.deepseek.com/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk-1e40463b32c44078bce9fb9d9db24b43' // 请确保这里是你的 key
      },
      body: JSON.stringify({
        model: "deepseek-chat",
        messages: apiMessages, // 【正确】这里使用我们组合好的 apiMessages
        temperature: 0.7
      })
    });

    const data = await response.json();
    if (!response.ok) return `奶龙肚子疼(错误码: ${response.status})：${data.error?.message || '未知错误'}`;
    
    if (data.choices && data.choices.length > 0) {
      const aiResponse = data.choices[0].message.content;
      history.push({ role: "assistant", content: aiResponse, timestamp: Date.now() });

      chatStore.set('messages', history);
      return aiResponse;
    }
    return "奶龙刚才发呆了，没接住你的话，再试一次？";
  } catch (error) { 
    console.error(error);
    return "奶龙的大脑断网了呜呜呜，快检查网线！"; 
  }
});
  
  ipcMain.handle('clear-chat-history', (event, range) => {
  const history = chatStore.get('messages', []);
  if (range === 'all') {
    chatStore.set('messages', []);
    return true;
  }

  const now = Date.now();
  const daysMap = { '7days': 7, '30days': 30, '1year': 365 };
  const cutoffTime = now - (daysMap[range] * 24 * 60 * 60 * 1000);

  // 过滤出比 cutoffTime 新的消息保留下来
  const newHistory = history.filter(msg => {
    // 兼容以前没存 timestamp 的老数据，没存一律当作过期数据清理掉
    const msgTime = msg.timestamp || 0; 
    return msgTime >= cutoffTime; 
  });

  chatStore.set('messages', newHistory);
  return true;
});

  ipcMain.on('update-setting', (event, { key, value }) => {
    config[key] = value; store.set('config', config);
    if (key === 'opacity') mainWindow.setOpacity(value);
    if (key === 'alwaysOnTop') mainWindow.setAlwaysOnTop(value);
    if (key === 'autoStart') app.setLoginItemSettings({ openAtLogin: value, path: app.getPath('exe') });
    if (key === 'zoomFactor') {
      const newW = Math.round(DEFAULTS.width * value); const newH = Math.round(DEFAULTS.height * value);
      mainWindow.setResizable(true); mainWindow.setSize(newW, newH); mainWindow.setResizable(false); 
    }
    if (key === 'shortcut') registerShortcuts();
    mainWindow.webContents.send('config-updated', config);
  });
 createWindow(); 
 createTray(); 
 registerShortcuts(); 
 startSystemUpdate();
  app.setLoginItemSettings({ openAtLogin: config.autoStart, path: app.getPath('exe') });

  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
// 在 main.js 的退出事件里增加强制清理
app.on('will-quit', () => {
  if (voiceProcess) {
    // 使用 Windows 的 taskkill 命令强制杀死整个进程树 (/t)
    const { exec } = require('child_process');
    exec(`taskkill /pid ${voiceProcess.pid} /t /f`, (err) => {
      if (err) console.error("强制关闭语音引擎失败:", err);
    });
  }
});

// 监听窗口全部关闭
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});