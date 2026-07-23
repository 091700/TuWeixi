document.addEventListener('DOMContentLoaded', async () => {
  const api = window.electronAPI;
  
  const timeEl = document.getElementById('time');
  const cpuEl = document.getElementById('cpu');
  const memEl = document.getElementById('mem');
  const netDownEl = document.getElementById('net-down');
  const netUpEl = document.getElementById('net-up');
  
  const btnSettings = document.getElementById('btn-settings');
  const btnMin = document.getElementById('btn-min');
  const btnClose = document.getElementById('btn-close');
  const btnExpand = document.getElementById('btn-expand');
  
  const container = document.getElementById('avatar-container');
  const imgStatic = document.getElementById('avatar-static');
  const vWave = document.getElementById('video-wave');
  const vLaugh = document.getElementById('video-laugh');
  const ballsContainer = document.getElementById('balls-container') || document.body;
  const danmakuSlot = document.getElementById('danmaku-slot');
  const windowEl = document.getElementById('window');
  const chatInput = document.getElementById('chat-input');
  const chatOutput = document.getElementById('chat-output');
  
  let isExpanded = false;

  if (btnSettings) btnSettings.addEventListener('click', () => api.openSettings());
  if (btnMin) btnMin.addEventListener('click', () => api.minimizeWindow());
  if (btnClose) btnClose.addEventListener('click', () => api.closeWindow());

  api.getSystemInfo().then(info => updateUI(info)).catch(e => {});
  api.getConfig().then(config => { if(config.theme) document.body.setAttribute('data-theme', config.theme); }).catch(e=>{});

  // 【修改三】：精简前端展开逻辑，利用 CSS 动画自然过渡
  if (btnExpand) {
    btnExpand.addEventListener('click', async () => {
      isExpanded = !isExpanded;
      
      if (isExpanded) {
        // 先调用主进程拉长外部窗口，再展开内部 CSS，防止被截断
        await api.toggleExpand(true);
        windowEl.classList.add('expanded');
        btnExpand.textContent = '▲';
      } else {
        // 先收起内部 CSS 动画，等待动画完毕后再缩小外部窗口
        windowEl.classList.remove('expanded');
        btnExpand.textContent = '▼';
        setTimeout(() => { 
          api.toggleExpand(false); 
        }, 300); // 这里的 300ms 正好配合 style.css 里的 transition 时间
      }
    });
  }
  
  function appendMessageToUI(role, text) {
    const msgDiv = document.createElement('div');
    // 根据角色分配 CSS class，'user' 是用户自己，'assistant' 对应系统的回复
    msgDiv.className = `chat-msg ${role === 'user' ? 'user' : 'system'}`;
    msgDiv.textContent = text;
    chatOutput.appendChild(msgDiv);
    chatOutput.scrollTop = chatOutput.scrollHeight; // 滚动到底部
  }

  async function loadHistory() {
    const history = await api.getChatHistory();
    // 遍历所有历史记录并显示出来
    history.forEach(msg => {
      // 排除掉可能存在的一些系统预设 prompt (role: 'system')，只显示 user 和 assistant 的对话
      if (msg.role === 'user' || msg.role === 'assistant') {
         appendMessageToUI(msg.role, msg.content);
      }
    });
  }
  loadHistory();

  function appendMessage(text, type) {
    const div = document.createElement('div');
    div.className = `chat-msg ${type}`;
    div.innerText = text;
    chatOutput.appendChild(div);
    chatOutput.scrollTop = chatOutput.scrollHeight; 
  }

  if (chatInput) {
    chatInput.addEventListener('keydown', async (e) => {
      if (e.key === 'Enter' && chatInput.value.trim() !== '') {
        const text = chatInput.value.trim();
        chatInput.value = ''; 
        appendMessage(text, 'user');
        appendMessage('奶龙思考中...', 'system');
        const reply = await api.chatWithDeepSeek(text);
        chatOutput.lastChild.remove();
        appendMessage(reply, 'system');
        nailongSpeak(reply);
      }
    });
  }

  let idleTimer = null;
  const danmakuMessages = ["我是奶龙", "我才是奶龙", "涂维兮yyds", "今夜星光闪闪", "哈哈哈哈哈哈哈哈哈", "涂维兮666", "我乃奶龙天尊！","mimimimi","嘿嘿嘿哈"];
  function fireDanmaku() {
    const text = danmakuMessages[Math.floor(Math.random() * danmakuMessages.length)];
    const el = document.createElement('div');
    el.className = 'danmaku-item'; el.innerText = text; el.style.left = (Math.random() * 20 - 10) + 'px';
    danmakuSlot.appendChild(el); setTimeout(() => el.remove(), 2500);
  }

  function resetIdleTimer() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => { if (!isDockedNow) fireDanmaku(); resetIdleTimer(); }, 20000); 
  }
  resetIdleTimer();

  function updateUI(data) {
    if (!data) return;
    if (cpuEl && data.cpu !== undefined) cpuEl.textContent = `CPU: ${data.cpu.toFixed(1)}%`;
    if (memEl && data.memory !== undefined) memEl.textContent = `内存: ${data.memory}`;
    if (netDownEl && data.download !== undefined) netDownEl.textContent = data.download;
    if (netUpEl && data.upload !== undefined) netUpEl.textContent = data.upload;
  }
  api.onUpdateSystemInfo(updateUI);

  api.onConfigUpdated(config => { if (config.theme) document.body.setAttribute('data-theme', config.theme); });

  let balls = []; let animationId = null; let isBouncing = false; 

  class NailongBall {
      constructor() {
          this.el = document.createElement('video');
          this.el.src = 'assets/nailongdaxiao.webm'; this.el.className = 'nailong-ball';
          this.el.muted = true; this.el.loop = true; this.el.playsInline = true;
          const size = 30 + Math.random() * 20;
          this.width = size; this.height = size;
          this.el.style.width = `${size}px`; this.el.style.height = `${size}px`;
          this.x = (window.innerWidth / 3) - (size / 2); this.y = (window.innerHeight / 2) - (size / 2);
          this.vx = (Math.random() - 0.5) * 14; this.vy = (Math.random() - 0.5) * 14;
          ballsContainer.appendChild(this.el); this.el.play().catch(() => {});
      }
      update(allowBounce) {
          this.x += this.vx; this.y += this.vy;
          const winW = window.innerWidth, winH = window.innerHeight;
          if (allowBounce) {
              if (this.x <= 0) { this.vx = Math.abs(this.vx); this.x = 0; } 
              else if (this.x + this.width >= winW) { this.vx = -Math.abs(this.vx); this.x = winW - this.width; }
              if (this.y <= 0) { this.vy = Math.abs(this.vy); this.y = 0; } 
              else if (this.y + this.height >= winH) { this.vy = -Math.abs(this.vy); this.y = winH - this.height; }
          } else { this.vx *= 1.05; this.vy *= 1.05; }
          this.el.style.transform = `translate(${this.x}px, ${this.y}px)`;
      }
      isfZOffScreen() { return (this.x < -100 || this.x > window.innerWidth + 100 || this.y < -100 || this.y > window.innerHeight + 100); }
      destroy() { if (this.el && this.el.parentNode) this.el.parentNode.removeChild(this.el); }
  }

  function spawnMoreBalls(count = 3) {
      for (let i = 0; i < count; i++) balls.push(new NailongBall());
      if (!animationId) loop(); 
  }

  function startBouncing() { if (isBouncing) return; isBouncing = true; for (let i = 0; i < 10; i++) balls.push(new NailongBall()); loop(); }
  function stopBouncing() { isBouncing = false; }

  function loop() {
      if (balls.length === 0) { cancelAnimationFrame(animationId); return; }
      balls.forEach((ball, index) => { ball.update(isBouncing); if (!isBouncing && ball.isfZOffScreen()) { ball.destroy(); balls.splice(index, 1); } });
      animationId = requestAnimationFrame(loop);
  }

  let currentDockState = 'normal';
  function showState(activeEl) {
      if (isDockedNow || currentDockState !== 'normal') return;
      [imgStatic, vWave, vLaugh].forEach(el => el.classList.remove('active'));
      activeEl.classList.add('active');
      vWave.pause(); vWave.currentTime = 0; vLaugh.pause(); vLaugh.currentTime = 0;
      if (activeEl.tagName === 'VIDEO') activeEl.play().catch(e => {});
      if (activeEl === vLaugh) startBouncing(); else stopBouncing(); 
  }

  container.addEventListener('mouseenter', () => { if (isDockedNow) return; showState(vWave); fireDanmaku(); resetIdleTimer(); });
  container.addEventListener('mouseleave', () => { if (isDockedNow) return; showState(imgStatic); resetIdleTimer(); });
  
  // 【重构】把 mousedown 改为了 click，彻底解决拖动时误触点击逻辑的问题
  container.addEventListener('click', (e) => {
      if (isDockedNow) return; 
      showState(vLaugh);
      spawnMoreBalls(1);
  });
  
  vLaugh.onended = () => { if (container.matches(':hover')) showState(vWave); else showState(imgStatic); };

  let isDockedNow = false;
  api.onDockState((state) => {
      if (state && state.startsWith('dock')) {
          isDockedNow = true; 
          const side = state.includes('-') ? state.split('-')[1] : '';
          windowEl.className = `window mini-mode ${side}`;
          imgStatic.src = 'assets/nailongbg.ico'; 
          [vWave, vLaugh].forEach(v => { v.pause(); v.classList.remove('active'); });
          imgStatic.classList.add('active');
      } else {
          isDockedNow = false; 
          windowEl.className = 'window';
          imgStatic.src = 'assets/nailong.png';
          if (document.getElementById('avatar-container').matches(':hover')) {
              vWave.classList.add('active'); imgStatic.classList.remove('active'); vWave.play().catch(()=>{});
          } else { imgStatic.classList.add('active'); }
      }
  });

  function updateLocalTime() { timeEl.textContent = new Date().toLocaleTimeString('zh-CN', { hour12: false }); }
  setInterval(updateLocalTime, 1000); updateLocalTime(); 

  async function nailongSpeak(text) {
    const cleanText = text.replace(/[^\u4e00-\u9fa5a-zA-Z0-9，。！？、]/g, '');
    if (!cleanText) return; 
    const url = `http://127.0.0.1:9880/?text=${encodeURIComponent(cleanText)}&text_language=zh`;
    const audio = new Audio(url);
    audio.play().catch(err => {});
  }
});