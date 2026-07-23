<template>
  <div class="app-wrapper" :class="{ 'high-pressure-mode': isHighPressure }">
    <!-- 背景装饰光效 -->
    <div class="ambient-glow blob-1"></div>
    <div class="ambient-glow blob-2"></div>
    
    <!-- 页面切换动画 -->
    <Transition name="slide-fade" mode="out-in">
      <!-- 登录/注册面板 -->
      <div v-if="currentStep === 'login'" class="setup-container glass-bento auth-panel" key="login">
        <div class="logo-area">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>
          <h1 class="title">锐捷AI面试系统</h1>
          <p class="subtitle">AetherInterview System</p>
        </div>
        
        <!-- 考生/管理员切换 -->
        <div class="segmented-control">
          <div class="segment-bg" :class="authForm.role"></div>
          <button class="segment-btn" :class="{ active: authForm.role === 'student' }" @click="authForm.role = 'student'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg> 考生入口
          </button>
          <button class="segment-btn" :class="{ active: authForm.role === 'admin' }" @click="authForm.role = 'admin'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg> 管理员入口
          </button>
        </div>

        <!-- 登录表单 -->
        <div class="input-group">
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            <input v-model="authForm.username" placeholder="学号 / 用户名" class="sys-input" type="text"/>
          </div>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            <input v-model="authForm.password" type="password" placeholder="请输入密码" class="sys-input" @keyup.enter="handleLogin"/>
          </div>
        </div>

        <div class="btn-group">
          <button class="sys-btn primary-btn" @click="handleLogin" :disabled="isLoading">登录系统</button>
          <button class="sys-btn secondary-btn" @click="handleRegister" :disabled="isLoading">注册账号</button>
        </div>
        <p v-if="authMessage" class="auth-message" :class="authMessageType">{{ authMessage }}</p>
      </div>

      <!-- 考生仪表盘 -->
      <StudentDashboard v-else-if="currentStep === 'dashboard'" :userId="currentUserId" @back="currentStep = 'major'" key="student_db" />
      <!-- 管理员仪表盘 -->
      <AdminDashboard v-else-if="currentStep === 'admin_dashboard'" @back="currentStep = 'login'" key="admin_db" />

      <!-- 专业&难度选择面板 -->
      <div v-else-if="currentStep === 'major'" class="setup-container glass-bento setup-panel" key="major">
        <div class="logo-area">
          <h1 class="title">选择您的专业</h1>
          <p class="subtitle">Choose Your Major</p>
        </div>

        <div class="config-section">
          <h3 class="section-label">选择目标专业</h3>
          <div class="card-grid">
            <div class="option-card" :class="{ active: selectedMajor === 'software_engineering' }" @click="selectedMajor = 'software_engineering'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
              <span>软件工程开发</span>
            </div>
            <div class="option-card" :class="{ active: selectedMajor === 'cyber_security' }" @click="selectedMajor = 'cyber_security'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
              <span>网络安全攻防</span>
            </div>
          </div>
        </div>

        <div class="config-section">
          <h3 class="section-label">选择考官风格 (难度)</h3>
          <div class="segmented-control diff-control">
            <div class="segment-bg" :class="selectedDifficulty"></div>
            <button class="segment-btn" :class="{ active: selectedDifficulty === 'easy' }" @click="selectedDifficulty = 'easy'">温和引导</button>
            <button class="segment-btn" :class="{ active: selectedDifficulty === 'medium' }" @click="selectedDifficulty = 'medium'">标准压力</button>
            <button class="segment-btn" :class="{ active: selectedDifficulty === 'hard' }" @click="selectedDifficulty = 'hard'">深挖噩梦</button>
          </div>
        </div>

        <button class="sys-btn primary-btn enter-btn" @click="confirmMajor">进入模拟考场</button>
      </div>

      <!-- 面试主界面 -->
      <div v-else-if="currentStep === 'interview'" class="interview-layout" key="interview">
        
        <!-- 面试顶部状态栏 -->
        <header class="interview-header">
          <div class="header-status">
            <span class="pulse-dot" :class="ws ? 'online' : 'offline'"></span>
            <span class="mono-num status-txt">{{ currentStatus }}</span>
          </div>
          <div class="header-actions">
            <button class="pill-action" @click="pauseInterview">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg> 暂停
            </button>
            <button class="pill-action" @click="goToDashboardOverlay">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 数据面板
            </button>
            <button class="pill-action danger-pill" @click="quitInterview">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg> 结束面试
            </button>
          </div>
        </header>

        <div class="interview-body">
          <!-- 左侧侧边栏：AI信息+能力雷达图 -->
          <aside class="sidebar-panel glass-bento">
            <div class="ai-profile">
              <div class="avatar-ring" :class="{ 'is-speaking': isAiSpeaking }">
                <img src="https://api.dicebear.com/7.x/bottts/svg?seed=Felix&backgroundColor=E2E8F0" alt="AI" class="ai-avatar" />
                <div class="ring-glow"></div>
              </div>
              <h2 class="ai-name">Senior AI Director</h2>
              <div class="role-badge">{{ selectedMajor === 'software_engineering' ? '软件工程方向' : '网络安全方向' }}</div>
            </div>
            
            <div class="radar-box">
              <h3 class="box-title">实时能力评估</h3>
              <RadarChart :radarData="radarData" />
            </div>
          </aside>

          <!-- 主聊天面板 -->
          <main class="chat-panel glass-bento">
            <!-- 聊天记录区域 -->
            <div class="chat-history" ref="chatBox">
              <div v-for="(msg, index) in chatHistory" :key="index" :class="['chat-bubble', msg.role === 'ai' ? 'ai-bubble' : 'user-bubble']">
                <div class="bubble-content">{{ msg.content }}</div>
                <div v-if="msg.score" class="score-tag mono-num">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                  逻辑 {{ msg.score }} | {{ msg.expression }}
                </div>
              </div>
            </div>

            <!-- 开始作答遮罩 -->
            <Transition name="scale-fade">
              <div class="prep-overlay" v-if="currentStatus === '请准备作答' && !isReadyToAnswer">
                <button class="sleek-ready-btn" @click="startAnswering">
                  <span class="txt">开始作答</span>
                  <div class="pulse-ring"></div>
                </button>
              </div>
            </Transition>

            <!-- 交互区域：计时器+输入框 -->
            <div class="interaction-station">
              <!-- 答题计时器 -->
              <div class="timer-bar" v-if="isReadyToAnswer && ['等待回答', '🎤 正在倾听你的回答... (录音中)'].includes(currentStatus)">
                <div class="timer-info mono-num" :class="{ 'danger-text': timeLeft <= 10 }">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                  {{ timeLeft }}s 剩余
                </div>
                <div class="progress-track">
                  <div class="progress-fill" :style="{ width: (timeLeft / totalTime) * 100 + '%' }" :class="{'warning-fill': timeLeft <= 15 && timeLeft > 5, 'danger-fill': timeLeft <= 10}"></div>
                </div>
              </div>

              <!-- 统一输入框 -->
              <div class="unified-input-box" :class="{ 'is-disabled': !isReadyToAnswer || isProcessing, 'is-recording-box': isRecording }">
                <!-- 录音按钮 -->
                <button class="mic-btn" :class="{ 'recording': isRecording }" :disabled="!isReadyToAnswer" @mousedown="startRecording" @mouseup="stopRecording" @mouseleave="stopRecording">
                  <svg v-if="!isRecording" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
                  <div v-else class="recording-indicator">
                    <span class="bar"></span><span class="bar"></span><span class="bar"></span>
                  </div>
                </button>
                
                <!-- 文字输入框 -->
                <input v-model="textAnswer" @keyup.enter="submitTextAnswer" class="chat-input" :placeholder="isRecording ? '正在录音，松开结束...' : '输入文字回答，或按住左侧麦克风说话...'" :disabled="!isReadyToAnswer || isProcessing || isRecording"/>
                
                <!-- 发送按钮 -->
                <button class="send-btn" @click="submitTextAnswer" :disabled="!textAnswer.trim() || !isReadyToAnswer || isProcessing">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
              </div>
            </div>
          </main>
        </div>

        <!-- 吉祥物组件 -->
        <Nailong ref="nailongRef" class="nailong-mascot" v-show="!showDashboardOverlay" />

        <!-- 悬浮仪表盘 -->
        <Transition name="fade">
          <StudentDashboard v-if="showDashboardOverlay" :userId="currentUserId" :isOverlay="true" @resume="showDashboardOverlay = false" @back="quitInterviewFromOverlay" class="overlay-dashboard" />
        </Transition>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import confetti from 'canvas-confetti'
import AdminDashboard from './AdminDashboard.vue'
import StudentDashboard from './StudentDashboard.vue'
import { ref, nextTick, onUnmounted } from 'vue'
import RadarChart from './RadarChart.vue'
import Nailong from './Nailong.vue'
import axios from 'axios'

// 全局响应式变量定义
const textAnswer = ref('')
const isProcessing = ref(false)
const currentStep = ref('login') 
const authForm = ref({ username: '', password: '', role: 'student' })
const isLoading = ref(false)
const authMessage = ref('')
const authMessageType = ref('error')
const currentUsername = ref('')
const radarData = ref({ tech: 80, logic: 70, confidence: 85, clarity: 90, relax: 75 })
const isStarted = ref(false)
const selectedMajor = ref('software_engineering')
const currentStatus = ref('等待就绪...')
const isAiSpeaking = ref(false)
const isRecording = ref(false)
const chatHistory = ref([])
const chatBox = ref(null)
const currentUserId = ref('')
const nailongRef = ref(null)
const selectedDifficulty = ref('medium')

// 计时器配置
const totalTime = 60
const timeLeft = ref(totalTime)
let countdownTimer = null
let currentAudio = null

// 面试状态控制
const isHighPressure = ref(false)
const isReadyToAnswer = ref(false)
const showDashboardOverlay = ref(false)

/**
 * 开始作答：启动计时器，更新面试状态
 */
const startAnswering = () => {
  isReadyToAnswer.value = true
  currentStatus.value = '等待回答'
  startTimer()
}

/**
 * 暂停面试：停止计时器，暂停音频，重置状态
 */
const pauseInterview = () => {
  stopTimer()
  isReadyToAnswer.value = false
  currentStatus.value = '请准备作答'
  isHighPressure.value = false
  if (currentAudio) {
    currentAudio.pause()
    currentAudio.currentTime = 0 
    currentAudio = null 
  }
  isAiSpeaking.value = false
}

/**
 * 打开悬浮数据面板
 */
const goToDashboardOverlay = () => {
  pauseInterview() 
  showDashboardOverlay.value = true
}

/**
 * 从悬浮面板退出面试
 */
const quitInterviewFromOverlay = () => {
  showDashboardOverlay.value = false
  quitInterview()
}

/**
 * 启动答题计时器
 */
const startTimer = () => {
  clearInterval(countdownTimer)
  timeLeft.value = totalTime
  countdownTimer = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--
      if (timeLeft.value <= 5) isHighPressure.value = true
    } else {
      clearInterval(countdownTimer)
      isHighPressure.value = false
      handleTimeOut() 
    }
  }, 1000)
}

/**
 * 停止计时器并重置时间
 */
const stopTimer = () => {
  clearInterval(countdownTimer)
  timeLeft.value = totalTime 
}

/**
 * 答题超时处理：自动提交默认答案
 */
const handleTimeOut = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    if (!textAnswer.value.trim()) {
      textAnswer.value = "抱歉，这道题我不太清楚，请问下一题吧。"
    }
    submitTextAnswer()
  }
}

// 录音/语音识别相关变量
let mediaRecorder = null
let audioChunks = []
let ws = null
let audioStream = null 
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
const recognition = SpeechRecognition ? new SpeechRecognition() : null

/**
 * 提交文字答案到后端
 */
const submitTextAnswer = () => {
  if (!textAnswer.value.trim() || isProcessing.value) return
  stopTimer()
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "text_answer", content: textAnswer.value }))
    textAnswer.value = '' 
    currentStatus.value = '大模型思考中...'
    isProcessing.value = true 
  } else {
    alert("网络连接不稳定，请刷新重试！")
  }
}

/**
 * 用户登录请求
 */
const handleLogin = async () => {
    if(!authForm.value.username || !authForm.value.password) {
        return showAuthMessage('请输入完整账号和密码')
    }
    isLoading.value = true
    try {
        const response = await axios.post('http://127.0.0.1:8081/api/user/login', authForm.value)
        const res = response.data
        if (res.status === 'success') {
            currentUserId.value = res.data.userId
            currentUsername.value = res.data.username
            const userRole = res.data.role
            showAuthMessage(userRole === 'admin' ? '欢迎回来，Admin' : '登录成功，' + currentUsername.value, 'success')
            setTimeout(() => {
                if (userRole === 'admin') currentStep.value = 'admin_dashboard' 
                else currentStep.value = 'major' 
                authForm.value.password = '' 
            }, 800)
        } else { 
          showAuthMessage(res.msg) 
        }
    } catch (error) { 
      showAuthMessage('连接鉴权服务器失败') 
    } finally { 
      isLoading.value = false 
    }
}

/**
 * 显示登录/注册提示信息
 */
const showAuthMessage = (msg, type='error') => {
    authMessage.value = msg
    authMessageType.value = type
    setTimeout(() => authMessage.value = '', 3000)
}

/**
 * 用户注册请求
 */
const handleRegister = async () => {
     if(!authForm.value.username || !authForm.value.password) return showAuthMessage('请输入注册账号和密码')
    isLoading.value = true
    try {
        const response = await axios.post('http://127.0.0.1:8081/api/user/register', authForm.value)
        if (response.data.status === 'success') {
            showAuthMessage('注册成功，请登录', 'success')
            authForm.value.password = ''
        } else { 
          showAuthMessage(response.data.msg) 
        }
    } catch (error) { 
      showAuthMessage('注册请求失败') 
    } finally { 
      isLoading.value = false 
    }
}

// 语音识别初始化配置
if (recognition) { 
  recognition.lang = 'zh-CN'
  recognition.continuous = true
  recognition.interimResults = false
}
let currentTranscript = ''

/**
 * 确认专业选择，进入面试界面
 */
const confirmMajor = () => { 
  currentStep.value = 'interview'
  startInterview()
}

/**
 * 初始化麦克风等媒体设备
 */
const initMediaDevice = async () => {
  try {
    audioStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(audioStream)
    audioChunks = []
    mediaRecorder.ondataavailable = (e) => { 
      if (e.data.size > 0) audioChunks.push(e.data) 
    }
    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' })
      setTimeout(() => { 
        if (ws && ws.readyState === WebSocket.OPEN) ws.send(blob) 
      }, 500)
      audioChunks = [] 
    }
    currentStatus.value = '外设检测完毕'
  } catch (error) {
    currentStatus.value = '麦克风权限受限'
  }
}

/**
 * 添加聊天消息到历史记录
 */
const addMessage = (role, content, extra = {}) => {
  chatHistory.value.push({ role, content, ...extra })
  nextTick(() => { 
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight 
  })
}

/**
 * 退出面试，关闭所有连接和设备
 */
const quitInterview = () => {
  if (ws) ws.close()
  if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop()
  if (audioStream) audioStream.getTracks().forEach(track => track.stop())
  if (recognition && recognition.state === 'started') recognition.stop()
  if (currentAudio) { 
    currentAudio.pause()
    currentAudio = null
  }
  isAiSpeaking.value = false
  currentStep.value = 'login'
  currentStatus.value = '会话结束'
  chatHistory.value = []
  isStarted.value = false
}

/**
 * 调用TTS接口播放音频
 */
const playAudioFromText = async (text) => {
  try {
    if (currentAudio) { 
      currentAudio.pause()
      currentAudio.currentTime = 0
      isAiSpeaking.value = false
    }
    const res = await axios.post('http://127.0.0.1:8000/api/tts/generate', { text: text, voice: "BV007_streaming" })
    if (res.data.status === 'success') {
      currentAudio = new Audio("data:audio/mp3;base64," + res.data.data.audio_base64)
      currentAudio.onended = () => { 
        isAiSpeaking.value = false
        currentAudio = null
      }
      isAiSpeaking.value = true
      currentAudio.play()
    }
  } catch (error) { 
    isAiSpeaking.value = false
  }
}

/**
 * 启动WebSocket面试连接
 */
const startInterview = async () => {
  isStarted.value = true
  currentStatus.value = '建立加密通信信道...'
  await initMediaDevice()
  try {
    ws = new WebSocket(`ws://127.0.0.1:8081/ws/interview/${currentUserId.value}/${selectedMajor.value}/${selectedDifficulty.value}`)
    ws.onopen = () => { 
      currentStatus.value = '已接入考场网络' 
      addMessage('ai', '我们已经对你的情况有了了解，接下来你无需进行自我介绍，我们直接开始面试，你准备好了吗？')
      addMessage('user', '我已经准备好了！')
    }
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'question') {
        isAiSpeaking.value = true
        currentStatus.value = '面试官提问中'
        addMessage('ai', data.content)
        playAudioFromText(data.content)
        setTimeout(() => {
          isAiSpeaking.value = false
          if (!isReadyToAnswer.value) currentStatus.value = '请准备作答'
          else { 
            currentStatus.value = '等待回答'
            startTimer() 
          }
        }, 2000)
      } else if (data.type === 'status') { 
        currentStatus.value = data.content 
      }
      else if (data.type === 'feedback') {
        addMessage('user', data.user_answer)
        addMessage('ai', data.ai_reply, { score: data.content_score, expression: `清晰${data.expression_scores.clarity}, 自信${data.expression_scores.confidence}` })
        playAudioFromText(data.ai_reply)
        radarData.value = {
          tech: data.content_score, 
          logic: data.content_score > 0 ? Math.min(100, data.content_score + 5) : 0, 
          confidence: data.expression_scores.confidence, 
          clarity: data.expression_scores.clarity, 
          relax: 100 - data.expression_scores.nervousness 
        }
        const relaxScore = 100 - data.expression_scores.nervousness
        const totalScore = Math.round((data.content_score + radarData.value.logic + data.expression_scores.confidence + data.expression_scores.clarity + relaxScore) / 5)
        
        // 高分礼花效果
        if (data.content_score >= 88) confetti({ particleCount: 150, spread: 80, origin: { y: 0.6 }, colors: ['#3B82F6', '#60A5FA', '#FFFFFF'] })
        // 低分压力模式
        if (data.content_score < 60) { 
          isHighPressure.value = true
          setTimeout(() => { isHighPressure.value = false }, 3000)
        }
        if (nailongRef.value) nailongRef.value.updateMascotByScore(totalScore)
        isProcessing.value = false
        
        if (isReadyToAnswer.value) { 
          currentStatus.value = '等待回答'
          startTimer()
        }
        else { 
          currentStatus.value = '请准备作答' 
        }
      }
    }
    ws.onerror = () => { currentStatus.value = '网络波动，尝试重连' }
    ws.onclose = () => { currentStatus.value = '信道已关闭' }
  } catch (error) { 
    currentStatus.value = '考场接入失败' 
  }
}

/**
 * 开始录音
 */
const startRecording = () => {
  if (!mediaRecorder) return
  if (mediaRecorder.state === 'inactive') {
    currentTranscript = ''
    if (recognition) {
      recognition.start()
      recognition.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) currentTranscript += event.results[i][0].transcript
        }
      }
    }
    mediaRecorder.start()
    isRecording.value = true
    currentStatus.value = '🎤 正在倾听你的回答... (录音中)'
  }
  if (currentAudio) { 
    currentAudio.pause()
    currentAudio = null
  }
  isAiSpeaking.value = false
}

/**
 * 停止录音并提交文本
 */
const stopRecording = () => {
  if (!mediaRecorder) return
  if (mediaRecorder.state === 'recording') {
    if (recognition) recognition.stop()
    mediaRecorder.stop()
    isRecording.value = false
    stopTimer()
    currentStatus.value = 'AI 算力评估中...'
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'user_text', content: currentTranscript || "抱歉，我刚才没听清。" }))
    }
  }
}

// 组件卸载时退出面试，释放资源
onUnmounted(() => { quitInterview() })
</script>

<style scoped>
/* ==========================================
   Apple/Vercel 级极简智算风 (Minimalist Glass)
============================================= */
* { box-sizing: border-box; }
.mono-num { font-family: 'JetBrains Mono', 'SF Mono', monospace; }

.app-wrapper {
  position: relative; width: 100vw; height: 100vh; overflow: hidden;
  background-color: #F8FAFC; color: #0F172A;
  font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
  transition: background 0.8s ease-in-out;
}

/* 极简流体背景光晕 */
.ambient-glow { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.5; z-index: 0; animation: float 15s infinite ease-in-out alternate; }
.blob-1 { top: -10%; left: -10%; width: 50vw; height: 50vw; background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, rgba(255,255,255,0) 70%); }
.blob-2 { bottom: -10%; right: -10%; width: 40vw; height: 40vw; background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, rgba(255,255,255,0) 70%); animation-delay: -5s; }
@keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(30px, 50px) scale(1.1); } }

/* 升级版红温模式：深色脉冲边缘，冷峻压迫感 */
.high-pressure-mode { background-color: #FEF2F2; }
.high-pressure-mode .ambient-glow { background: radial-gradient(circle, rgba(239,68,68,0.2) 0%, transparent 70%); animation: pulse-red 2s infinite alternate; }
@keyframes pulse-red { 0% { transform: scale(1); opacity: 0.5; } 100% { transform: scale(1.1); opacity: 0.8; } }

/* 通用毛玻璃卡片 */
.glass-bento {
  background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.8); box-shadow: 0 10px 40px -10px rgba(15, 23, 42, 0.05); border-radius: 24px;
}

/* --- 登录/配置面板 --- */
.setup-container {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 90%; max-width: 480px; padding: 40px; display: flex; flex-direction: column; align-items: center; z-index: 10;
}
.setup-panel { max-width: 540px; }
.logo-area { text-align: center; margin-bottom: 30px; }
.logo-area svg { width: 40px; height: 40px; color: #3B82F6; margin-bottom: 12px; }
.title { font-size: 24px; font-weight: 700; color: #0F172A; margin: 0 0 8px 0; }
.subtitle { font-size: 14px; color: #64748B; font-family: 'JetBrains Mono', monospace; margin: 0; }

/* Apple 风格分段控制器 */
.segmented-control { position: relative; display: flex; background: rgba(15, 23, 42, 0.05); padding: 4px; border-radius: 12px; margin-bottom: 24px; width: 100%; }
.segment-btn { flex: 1; position: relative; z-index: 1; background: transparent; border: none; padding: 10px; font-size: 14px; font-weight: 600; color: #64748B; cursor: pointer; transition: color 0.3s; display: flex; justify-content: center; align-items: center; gap: 6px; }
.segment-btn svg { width: 16px; height: 16px; }
.segment-btn.active { color: #0F172A; }
.segment-bg { position: absolute; top: 4px; bottom: 4px; width: calc(50% - 4px); background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
.segment-bg.student { transform: translateX(0); }
.segment-bg.admin { transform: translateX(100%); }
.diff-control .segment-btn { font-size: 13px; }
.diff-control .segment-bg { width: calc(33.33% - 2.6px); }
.diff-control .segment-bg.easy { transform: translateX(0); }
.diff-control .segment-bg.medium { transform: translateX(100%); }
.diff-control .segment-bg.hard { transform: translateX(200%); }

/* 输入框组合 */
.input-group { width: 100%; display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }
.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 16px; width: 18px; height: 18px; color: #94A3B8; }
.sys-input { width: 100%; padding: 14px 16px 14px 44px; border: 1px solid rgba(15, 23, 42, 0.1); border-radius: 12px; background: rgba(255, 255, 255, 0.8); font-size: 15px; color: #0F172A; outline: none; transition: all 0.2s; }
.sys-input:focus { border-color: #3B82F6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); background: #fff; }

/* 按钮组合 */
.btn-group { width: 100%; display: flex; gap: 12px; }
.sys-btn { flex: 1; padding: 14px; border: none; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; justify-content: center; align-items: center; }
.primary-btn { background: #0F172A; color: #fff; }
.primary-btn:hover:not(:disabled) { background: #334155; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(15,23,42,0.15); }
.secondary-btn { background: #fff; color: #0F172A; border: 1px solid rgba(15, 23, 42, 0.1); }
.secondary-btn:hover:not(:disabled) { background: #F8FAFC; border-color: #94A3B8; }
.sys-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.enter-btn { width: 100%; margin-top: 10px; }

/* 配置选项卡 */
.config-section { width: 100%; margin-bottom: 24px; }
.section-label { font-size: 13px; font-weight: 600; color: #64748B; margin: 0 0 12px 0; text-align: left; }
.card-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.option-card { padding: 20px; border-radius: 16px; background: rgba(255, 255, 255, 0.5); border: 1px solid rgba(15, 23, 42, 0.05); display: flex; flex-direction: column; align-items: center; gap: 10px; cursor: pointer; transition: all 0.2s; color: #475569; font-weight: 600; font-size: 14px; }
.option-card svg { width: 28px; height: 28px; color: #94A3B8; transition: color 0.2s; }
.option-card:hover { background: rgba(255, 255, 255, 0.8); }
.option-card.active { background: #EFF6FF; border-color: #3B82F6; color: #1E3A8A; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1); }
.option-card.active svg { color: #3B82F6; }

/* 提示信息 */
.auth-message { margin-top: 16px; font-size: 13px; font-weight: 500; }
.error { color: #EF4444; }
.success { color: #10B981; }

/* ================= 核心考场布局 ================= */
.interview-layout { position: relative; width: 100vw; height: 100vh; display: flex; flex-direction: column; z-index: 10; padding: 20px; max-width: 1400px; margin: 0 auto; }

/* 顶栏 */
.interview-header { display: flex; justify-content: space-between; align-items: center; height: 60px; margin-bottom: 20px; }
.header-status { display: flex; align-items: center; gap: 10px; background: rgba(255, 255, 255, 0.6); padding: 8px 16px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.8); }
.pulse-dot { width: 8px; height: 8px; border-radius: 50%; }
.online { background: #10B981; box-shadow: 0 0 8px #10B981; animation: pulse-green 2s infinite; }
.offline { background: #94A3B8; }
.status-txt { font-size: 13px; font-weight: 500; color: #475569; }
@keyframes pulse-green { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

.header-actions { display: flex; gap: 12px; }
.pill-action { display: flex; align-items: center; gap: 6px; padding: 8px 16px; background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(15,23,42,0.1); border-radius: 20px; font-size: 13px; font-weight: 600; color: #0F172A; cursor: pointer; transition: all 0.2s; }
.pill-action svg { width: 14px; height: 14px; }
.pill-action:hover { background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.danger-pill { color: #EF4444; border-color: rgba(239, 68, 68, 0.2); }
.danger-pill:hover { background: #FEF2F2; }

/* 主体分栏 */
.interview-body { flex: 1; display: flex; gap: 24px; min-height: 0; }
.sidebar-panel { width: 320px; display: flex; flex-direction: column; padding: 30px 24px; flex-shrink: 0; }
.chat-panel { flex: 1; display: flex; flex-direction: column; padding: 24px; position: relative; overflow: hidden; }

/* 左侧 AI Profile */
.ai-profile { display: flex; flex-direction: column; align-items: center; margin-bottom: 40px; text-align: center; }
.avatar-ring { position: relative; width: 100px; height: 100px; margin-bottom: 16px; }
.ai-avatar { width: 100%; height: 100%; border-radius: 50%; border: 2px solid #fff; position: relative; z-index: 2; background: #F8FAFC; }
.ring-glow { position: absolute; inset: -6px; border-radius: 50%; background: conic-gradient(from 0deg, #3B82F6, #8B5CF6, #3B82F6); filter: blur(8px); opacity: 0; transition: opacity 0.3s; z-index: 1; }
.is-speaking .ring-glow { opacity: 0.6; animation: spin-glow 4s linear infinite; }
@keyframes spin-glow { 100% { transform: rotate(360deg); } }
.ai-name { font-size: 18px; font-weight: 700; color: #0F172A; margin: 0 0 6px 0; }
.role-badge { font-size: 11px; padding: 4px 10px; background: #EFF6FF; color: #1E3A8A; border-radius: 12px; font-weight: 600; }

.radar-box { flex: 1; display: flex; flex-direction: column; }
.box-title { font-size: 13px; font-weight: 600; color: #64748B; margin: 0 0 16px 0; text-transform: uppercase; letter-spacing: 0.5px; text-align: center;}

/* 右侧对话区 */
.chat-history { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; padding-right: 10px; margin-bottom: 20px; }
.chat-history::-webkit-scrollbar { width: 6px; }
.chat-history::-webkit-scrollbar-thumb { background: rgba(15, 23, 42, 0.1); border-radius: 10px; }
.chat-bubble { max-width: 85%; display: flex; flex-direction: column; gap: 8px; }
.bubble-content { padding: 16px 20px; border-radius: 18px; font-size: 15px; line-height: 1.6; }
.ai-bubble { align-self: flex-start; }
.ai-bubble .bubble-content { background: rgba(255, 255, 255, 0.8); color: #1E293B; border-top-left-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.user-bubble { align-self: flex-end; align-items: flex-end;}
.user-bubble .bubble-content { background: #3B82F6; color: #fff; border-top-right-radius: 4px; box-shadow: 0 4px 12px rgba(59,130,246,0.2); }
.score-tag { font-size: 11px; color: #64748B; background: rgba(255,255,255,0.6); padding: 4px 10px; border-radius: 8px; display: inline-flex; align-items: center; gap: 4px; }
.score-tag svg { width: 12px; height: 12px; }

/* 悬浮准备遮罩 */
.prep-overlay { position: absolute; inset: 0; background: rgba(248, 250, 252, 0.5); backdrop-filter: blur(8px); display: flex; justify-content: center; align-items: center; z-index: 50; border-radius: 24px; }
.sleek-ready-btn { position: relative; width: 140px; height: 140px; border-radius: 50%; border: none; background: #0F172A; color: #fff; display: flex; justify-content: center; align-items: center; cursor: pointer; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.3); outline: none; transition: transform 0.2s; }
.sleek-ready-btn:hover { transform: scale(1.05); }
.sleek-ready-btn:active { transform: scale(0.95); }
.sleek-ready-btn .txt { font-size: 16px; font-weight: 700; z-index: 2; letter-spacing: 1px; }
.pulse-ring { position: absolute; inset: -4px; border-radius: 50%; border: 2px solid #0F172A; opacity: 0.5; animation: sleek-pulse 2s infinite cubic-bezier(0.2, 0, 0.2, 1); pointer-events: none; }
@keyframes sleek-pulse { 0% { transform: scale(1); opacity: 0.5; border-width: 2px; } 100% { transform: scale(1.4); opacity: 0; border-width: 0; } }

/* 底部交互区 (统一输入框) */
.interaction-station { display: flex; flex-direction: column; gap: 12px; flex-shrink: 0; }
.timer-bar { display: flex; flex-direction: column; gap: 6px; padding: 0 10px; }
.timer-info { font-size: 12px; font-weight: 600; color: #64748B; display: flex; align-items: center; gap: 6px; }
.timer-info svg { width: 14px; height: 14px; }
.danger-text { color: #EF4444; animation: pulse-txt 1s infinite; }
@keyframes pulse-txt { 50% { opacity: 0.5; } }
.progress-track { width: 100%; height: 6px; background: rgba(15,23,42,0.05); border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: #10B981; transition: width 1s linear, background-color 0.5s; }
.warning-fill { background: #F59E0B; }
.danger-fill { background: #EF4444; }

.unified-input-box { display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.8); border: 1px solid rgba(15,23,42,0.1); border-radius: 24px; padding: 8px 12px 8px 8px; transition: all 0.3s; box-shadow: 0 4px 12px rgba(0,0,0,0.02); }
.unified-input-box:focus-within { border-color: #3B82F6; box-shadow: 0 4px 20px rgba(59,130,246,0.15); background: #fff; }
.is-disabled { opacity: 0.6; background: rgba(248,250,252,0.8); }
.is-recording-box { border-color: #EF4444; box-shadow: 0 4px 20px rgba(239,68,68,0.15); }

.mic-btn { width: 40px; height: 40px; border-radius: 50%; border: none; background: #F1F5F9; color: #475569; display: flex; justify-content: center; align-items: center; cursor: pointer; transition: all 0.2s; flex-shrink: 0; }
.mic-btn svg { width: 18px; height: 18px; }
.mic-btn:hover:not(:disabled) { background: #E2E8F0; color: #0F172A; }
.mic-btn.recording { background: #EF4444; color: #fff; animation: mic-pulse 1.5s infinite; }
@keyframes mic-pulse { 0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); } 70% { box-shadow: 0 0 0 10px rgba(239,68,68,0); } 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); } }

.recording-indicator { display: flex; gap: 3px; align-items: center; height: 12px; }
.bar { width: 3px; background: #fff; border-radius: 2px; animation: sound-wave 1s ease-in-out infinite; }
.bar:nth-child(2) { animation-delay: 0.1s; }
.bar:nth-child(3) { animation-delay: 0.2s; }
@keyframes sound-wave { 0%, 100% { height: 4px; } 50% { height: 12px; } }

.chat-input { flex: 1; background: transparent; border: none; font-size: 15px; color: #0F172A; outline: none; padding: 0 8px; }
.chat-input::placeholder { color: #94A3B8; }

.send-btn { width: 36px; height: 36px; border-radius: 12px; border: none; background: #0F172A; color: #fff; display: flex; justify-content: center; align-items: center; cursor: pointer; transition: all 0.2s; flex-shrink: 0; }
.send-btn svg { width: 16px; height: 16px; }
.send-btn:disabled { background: #E2E8F0; color: #94A3B8; cursor: not-allowed; }
.send-btn:hover:not(:disabled) { background: #3B82F6; transform: translateY(-1px); }

/* 过渡动画 */
.slide-fade-enter-active {
  transition: opacity 0.47s cubic-bezier(0.4, 0, 0.2, 1),
              filter 0.47s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: opacity 0.37s ease, filter 0.37s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  filter: blur(0.1px); 
}
.scale-fade-enter-active, .scale-fade-leave-active { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
.scale-fade-enter-from, .scale-fade-leave-to { transform: scale(0.9); opacity: 0; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.4s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>