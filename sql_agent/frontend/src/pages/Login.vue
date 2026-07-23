<template>
  <div class="login-page">
    <canvas ref="bgCanvas" class="bg-canvas"></canvas>

    <!-- 主卡片 -->
    <div class="auth-card">
      <!-- 左侧：品牌区 -->
      <div class="card-left">
        <div class="left-content">
          <!-- Logo -->
          <div class="brand-row">
            <svg class="brand-logo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <ellipse cx="12" cy="5" rx="9" ry="3"/>
              <path d="M3 5v6c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>
              <path d="M3 11v6c0 1.66 4.03 3 9 3s9-1.34 9-3v-6"/>
            </svg>
          </div>

          <!-- 标题 -->
          <h1>SQL 智能代理系统</h1>
          <p class="subtitle">以微光洞察数据万象</p>

          <!-- 描述 -->
          <p class="desc">
            自然语言驱动精准 SQL，一站式数据库智慧中枢。<br/>
            集成表结构巡检、慢查询诊断、备份策略评估与安全审计。
          </p>

          <!-- 功能列表 -->
          <div class="feature-list">
            <div class="feature-item">
              <svg class="feat-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              <span>自然语言转精准 SQL</span>
            </div>
            <div class="feature-item">
              <svg class="feat-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
              <span>表结构巡检与优化</span>
            </div>
            <div class="feature-item">
              <svg class="feat-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              <span>慢查询根因诊断</span>
            </div>
            <div class="feature-item">
              <svg class="feat-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>
              <span>备份策略与安全审计</span>
            </div>
          </div>
        </div>

        <div class="left-footer">
          <span>  </span>
          <span class="footer-divider">·</span>
          <span>   </span>
          //占位页脚不要添加东西
        </div>
      </div>

      <!-- 右侧：登录表单 -->
      <div class="card-right">
        <div class="form-wrap">
          <!-- 标签切换 -->
          <div class="tab-bar">
            <button class="tab" :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
            <button class="tab" :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
          </div>

          <form class="auth-form" @submit.prevent="handleSubmit">
            <div class="input-group">
              <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
              <input v-model="username" type="text" placeholder="用户名" autocomplete="username" :disabled="loading" />
            </div>

            <div class="input-group">
              <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
              </svg>
              <input v-model="password" type="password" placeholder="密码" autocomplete="current-password" :disabled="loading" />
            </div>

            <div class="input-group" v-if="mode === 'register'">
              <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
              <input v-model="displayName" type="text" placeholder="显示名称（选填）" :disabled="loading" />
            </div>

            <div class="error-msg" v-if="errorMsg">{{ errorMsg }}</div>

            <button type="submit" class="btn-submit" :disabled="loading || !username.trim() || !password.trim()">
              <template v-if="!loading">{{ mode === 'login' ? '登 录' : '注 册' }}</template>
              <template v-else>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32">
                    <animate attributeName="stroke-dashoffset" values="32;0" dur="1.2s" repeatCount="indefinite"/>
                  </circle>
                </svg>
                处理中...
              </template>
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- 背景柔光 -->
    <div class="ambient-glow glow-1"></div>
    <div class="ambient-glow glow-2"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuth } from '../store/auth.js'
import { API_BASE } from '../config.js'

const router = useRouter()
const auth = useAuth()
const mode = ref('login')
const username = ref('admin')
const password = ref('admin123')
const displayName = ref('')
const loading = ref(false)
const errorMsg = ref('')

// ═══════════ Canvas 星空背景 ═══════════
const bgCanvas = ref(null)
let anim = null

function applyStoredTheme() {
  const t = localStorage.getItem('db_agent_theme')
  const html = document.querySelector('html')
  if (!html) return
  if (t === 'light') html.classList.add('light-theme')
  else html.classList.remove('light-theme')
}

function initBg() {
  const c = bgCanvas.value
  if (!c) return
  const ctx = c.getContext('2d')
  let w = 0, h = 0
  const stars = [], meteors = []

  function rs() { w = c.width = c.offsetWidth; h = c.height = c.offsetHeight }
  rs()
  window.addEventListener('resize', rs)

  for (let i = 0; i < 200; i++) {
    stars.push({
      x: Math.random() * 1920,
      y: Math.random() * 1080,
      r: Math.random() * 1.8 + 0.3,
      s: Math.random() * 0.02 + 0.005,
      p: Math.random() * Math.PI * 2,
      b: Math.random() * 0.4 + 0.25
    })
  }

  function sm() {
    meteors.push({
      x: Math.random() * w * 0.8 + w * 0.1,
      y: Math.random() * h * 0.2,
      l: Math.random() * 80 + 40,
      v: Math.random() * 4 + 3,
      life: 1,
      d: Math.random() * 0.008 + 0.003
    })
  }

  function draw() {
    ctx.clearRect(0, 0, w, h)
    const n = Date.now() * 0.001

    // 星星
    for (const s of stars) {
      const a = s.b + Math.sin(n * s.s * 50 + s.p) * 0.3
      ctx.beginPath()
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(200,220,255,${Math.max(0.08, a)})`
      ctx.fill()
    }

    // 流星
    for (let i = meteors.length - 1; i >= 0; i--) {
      const m = meteors[i]
      m.x -= m.v
      m.y += m.v * 0.5
      m.life -= m.d
      if (m.life <= 0) { meteors.splice(i, 1); continue }
      const g = ctx.createLinearGradient(m.x, m.y, m.x + m.l, m.y - m.l * 0.5)
      g.addColorStop(0, `rgba(180,210,255,${m.life * 0.8})`)
      g.addColorStop(1, 'rgba(255,255,255,0)')
      ctx.beginPath()
      ctx.moveTo(m.x, m.y)
      ctx.lineTo(m.x + m.l, m.y - m.l * 0.5)
      ctx.strokeStyle = g
      ctx.lineWidth = 1.5
      ctx.stroke()
    }

    if (Math.random() < 0.005) sm()

    anim = requestAnimationFrame(draw)
  }

  for (let i = 0; i < 4; i++) sm()
  draw()
}

async function handleSubmit() {
  errorMsg.value = ''
  loading.value = true
  try {
    if (mode.value === 'login') {
      const r = await axios.post(`${API_BASE}/auth/login`, { username: username.value, password: password.value })
      auth.setAuth(r.data.access_token, r.data.username, r.data.role, r.data.display_name)
    } else {
      const r = await axios.post(`${API_BASE}/auth/register`, { username: username.value, password: password.value, display_name: displayName.value || null })
      auth.setAuth(r.data.access_token, r.data.username, r.data.role, r.data.display_name)
    }
    router.push('/')
  } catch (e) {
    const d = e.response?.data?.detail || e.message
    errorMsg.value = typeof d === 'string' ? d : '操作失败，请重试'
  }
  loading.value = false
}

onMounted(() => { applyStoredTheme(); initBg() })
onUnmounted(() => { if (anim) cancelAnimationFrame(anim) })
</script>

<style scoped>
/* ═══════════ 页面容器 ═══════════ */
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  background: radial-gradient(ellipse 80% 60% at 50% 40%, #0f1328 0%, #060912 60%, #02040a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* ═══════════ Canvas 背景 ═══════════ */
.bg-canvas {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  width: 100%;
  height: 100%;
}

/* ═══════════ 背景柔光 ═══════════ */
.ambient-glow {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  filter: blur(120px);
  animation: glowFloat 14s ease-in-out infinite;
}
.glow-1 {
  width: 500px;
  height: 500px;
  background: rgba(100, 140, 220, 0.06);
  top: -20%;
  left: -12%;
  animation-delay: 0s;
}
.glow-2 {
  width: 400px;
  height: 400px;
  background: rgba(140, 120, 220, 0.04);
  bottom: -15%;
  right: -10%;
  animation-delay: -7s;
}
@keyframes glowFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(25px, -18px) scale(1.06); }
  66% { transform: translate(-18px, 15px) scale(0.95); }
}

/* ═══════════ 主卡片 ═══════════ */
.auth-card {
  position: relative;
  z-index: 1;
  display: flex;
  width: 92%;
  max-width: 900px;
  min-height: 520px;
  border-radius: 16px;
  overflow: hidden;
  background: rgba(12, 16, 32, 0.45);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 0 0 1px rgba(138, 180, 248, 0.04),
    0 16px 64px rgba(0, 0, 0, 0.45),
    0 0 140px rgba(80, 130, 220, 0.05);
  animation: cardIn 0.7s cubic-bezier(0.22, 0.61, 0.36, 1) both;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(28px) scale(0.96); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ═══════════ 左侧：品牌区 ═══════════ */
.card-left {
  flex: 1.1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 40px 44px 52px;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.left-content {
  display: flex;
  flex-direction: column;
}

/* Logo */
.brand-row {
  margin-bottom: 18px;
}
.brand-logo {
  width: 38px;
  height: 38px;
  color: #8ab4f8;
  filter: drop-shadow(0 0 14px rgba(138, 180, 248, 0.35));
  animation: logoGlow 3.5s ease-in-out infinite;
}
@keyframes logoGlow {
  0%, 100% { filter: drop-shadow(0 0 10px rgba(138, 180, 248, 0.3)); }
  50%      { filter: drop-shadow(0 0 24px rgba(138, 180, 248, 0.55)); }
}

/* 标题 */
.card-left h1 {
  font-size: 26px;
  font-weight: 700;
  color: #e4e8f0;
  margin: 0 0 8px;
  letter-spacing: -0.3px;
}
.subtitle {
  font-size: 13.5px;
  color: #7688b8;
  margin: 0 0 26px;
  font-weight: 400;
  letter-spacing: 0.5px;
}

/* 描述 */
.desc {
  font-size: 13.5px;
  line-height: 1.75;
  color: #8890b0;
  margin: 0 0 32px;
  max-width: 360px;
}

/* 功能列表 */
.feature-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #a0a8c0;
}
.feat-icon {
  flex-shrink: 0;
  color: #6b8fd4;
  opacity: 0.7;
}

/* 左下角 */
.left-footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #586080;
  opacity: 0.55;
  padding-top: 40px;
}
.footer-divider {
  font-weight: 700;
  opacity: 0.4;
}

/* ═══════════ 右侧：登录表单 ═══════════ */
.card-right {
  flex: 0.9;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 44px 44px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.form-wrap {
  width: 100%;
  max-width: 320px;
}

/* 标签切换 */
.tab-bar {
  display: flex;
  margin-bottom: 28px;
  gap: 28px;
}
.tab {
  padding: 0 0 10px;
  border: none;
  background: none;
  font-size: 15px;
  font-weight: 600;
  color: #5f6888;
  cursor: pointer;
  transition: color 0.2s;
  font-family: inherit;
  position: relative;
}
.tab:hover { color: #8890b8; }
.tab.active { color: #dce0f0; }
.tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  border-radius: 1px;
  background: #8ab4f8;
  box-shadow: 0 0 8px rgba(138, 180, 248, 0.4);
}

/* 表单 */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 输入框 */
.input-group {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.07);
  transition: all 0.25s;
}
.input-group:focus-within {
  border-color: rgba(138, 180, 248, 0.4);
  background: rgba(138, 180, 248, 0.05);
  box-shadow: 0 0 0 3px rgba(138, 180, 248, 0.06);
}
.input-group input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: #e4e8f0;
  font-family: inherit;
}
.input-group input::placeholder { color: #506080; }
.input-group input:disabled { opacity: 0.35; }
.input-icon {
  flex-shrink: 0;
  color: #506080;
  transition: color 0.25s;
}
.input-group:focus-within .input-icon { color: #8ab4f8; }

/* 错误提示 */
.error-msg {
  padding: 10px 14px;
  border-radius: 8px;
  background: rgba(242, 139, 130, 0.08);
  color: #f28b82;
  font-size: 12.5px;
  font-weight: 500;
  border: 1px solid rgba(242, 139, 130, 0.12);
  animation: shake 0.4s ease;
}
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-6px); }
  40% { transform: translateX(6px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(3px); }
}

/* 提交按钮 */
.btn-submit {
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #4a7fd4, #6b9ff8);
  color: #fff;
  font-size: 14.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
  position: relative;
  overflow: hidden;
}
.btn-submit::after {
  content: '';
  position: absolute;
  top: 0;
  left: -70%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  transform: skewX(-20deg);
  transition: left 0.5s ease;
}
.btn-submit:hover:not(:disabled)::after { left: 120%; }
.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(74, 127, 212, 0.4);
}
.btn-submit:active:not(:disabled) { transform: scale(0.97); }
.btn-submit:disabled { opacity: 0.35; cursor: not-allowed; transform: none; box-shadow: none; }

/* ═══════════ 响应式 ═══════════ */
@media (max-width: 700px) {
  .auth-card {
    flex-direction: column;
    max-width: 420px;
    margin: 20px;
  }
  .card-left {
    padding: 32px 28px 24px;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }
  .desc { margin-bottom: 20px; }
  .feature-item { font-size: 12px; }
  .left-footer { padding-top: 24px; }
  .card-right { padding: 28px 28px 32px; }
}
</style>