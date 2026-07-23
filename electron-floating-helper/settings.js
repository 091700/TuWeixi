document.addEventListener('DOMContentLoaded', async () => {
  const api = window.electronAPI;
  const config = await api.getConfig();

  const inpAutoStart = document.getElementById('inp-autostart');
  const inpTop = document.getElementById('inp-top');
  const selZoom = document.getElementById('sel-zoom');
  const selTheme = document.getElementById('sel-theme');
  const inpOpacity = document.getElementById('inp-opacity');
  const opacityVal = document.getElementById('opacity-val');
  const inpShortcut = document.getElementById('inp-shortcut');
  const btnClose = document.getElementById('btn-close');
  const btnClearChat = document.getElementById('btn-clear-chat');
  const selClearRange = document.getElementById('sel-clear-range');
  // 在 DOMContentLoaded 里面添加

  // 辅助函数：应用主题
  function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme || 'light');
  }

  // --- 初始化数据 ---
  if(inpAutoStart) inpAutoStart.checked = config.autoStart;
  if(inpTop) inpTop.checked = config.alwaysOnTop;
  if(selZoom) selZoom.value = config.zoomFactor || 1.0;
  if(selTheme) selTheme.value = config.theme || 'light';
  if(inpOpacity) {
    const op = Math.round((config.opacity || 0.8) * 100);
    inpOpacity.value = op;
    opacityVal.innerText = op + '%';
  }
  if(inpShortcut) inpShortcut.value = config.shortcut || 'Ctrl+Alt+Q';
  if (btnClearChat && selClearRange) {
    btnClearChat.addEventListener('click', async () => {
      const range = selClearRange.value;
      const originalText = btnClearChat.innerText;
      
      btnClearChat.innerText = '清理中...';
      btnClearChat.disabled = true;
      
      // 调用主进程清理历史记录
      await api.clearChatHistory(range);
      
      btnClearChat.innerText = '已清理！';
      setTimeout(() => {
        btnClearChat.innerText = originalText;
        btnClearChat.disabled = false;
      }, 1500);
    });
  }
  // 立即应用当前主题
  applyTheme(config.theme);

  // --- 监听来自主进程的配置同步 (例如主窗口改了，这里也要改，或者自身改了触发更新) ---
  api.onConfigUpdated((newConfig) => {
    applyTheme(newConfig.theme);
  });

  // --- 绑定事件 ---
  inpAutoStart.addEventListener('change', e => api.updateSetting('autoStart', e.target.checked));
  inpTop.addEventListener('change', e => api.updateSetting('alwaysOnTop', e.target.checked));
  selZoom.addEventListener('change', e => api.updateSetting('zoomFactor', parseFloat(e.target.value)));
  
  // 主题切换：发送给主进程，主进程会广播给所有窗口
  selTheme.addEventListener('change', e => {
    const theme = e.target.value;
    api.updateSetting('theme', theme);
    applyTheme(theme); // 立即让当前窗口生效
  });

  inpOpacity.addEventListener('input', e => {
    const val = e.target.value;
    opacityVal.innerText = val + '%';
    api.updateSetting('opacity', val / 100);
  });

  inpShortcut.addEventListener('keydown', (e) => {
    e.preventDefault();
    const modifiers = [];
    if (e.ctrlKey) modifiers.push('Ctrl');
    if (e.metaKey) modifiers.push('Super');
    if (e.altKey) modifiers.push('Alt');
    if (e.shiftKey) modifiers.push('Shift');
    let key = e.key.toUpperCase();
    if (['CONTROL', 'ALT', 'SHIFT', 'META'].includes(key)) return;
    const shortcutStr = [...modifiers, key].join('+');
    inpShortcut.value = shortcutStr;
    api.updateSetting('shortcut', shortcutStr);
  });

  btnClose.addEventListener('click', () => api.closeSettings());
});