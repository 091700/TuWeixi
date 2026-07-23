<template>
  <div class="student-dashboard-container" :class="{ 'is-overlay-mode': isOverlay }">
    <!-- 背景装饰光效（非悬浮模式显示） -->
    <div class="ambient-glow blob-1" v-if="!isOverlay"></div>
    <div class="ambient-glow blob-2" v-if="!isOverlay"></div>

    <!-- 仪表盘主内容 -->
    <div class="dashboard-content glass-bento">
      
      <!-- 头部标题与操作栏 -->
      <header class="bento-header">
        <div class="header-title">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
          <h2>个人面试能力图鉴 <span class="badge-pro">Student Profile</span></h2>
        </div>
        
        <div class="action-group">
          <!-- 悬浮模式：返回面试按钮 -->
          <button v-if="isOverlay" class="exit-btn sys-blue-btn" @click="$emit('resume')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            返回面试
          </button>
          <!-- 返回大厅按钮 -->
          <button class="exit-btn sys-red-btn" @click="$emit('back')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
            返回大厅
          </button>
        </div>
      </header>

      <!-- 图表网格：趋势图 + 雷达图 -->
      <div class="charts-grid">
        <div class="chart-card bento-card">
          <div ref="trendChart" class="echart-container"></div>
        </div>
        <div class="chart-card bento-card">
          <div ref="dimChart" class="echart-container"></div>
        </div>
      </div>

      <!-- 面试历史记录面板 -->
      <div class="history-panel bento-card">
        <div class="panel-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          你的面试足迹
        </div>

        <!-- 空数据状态 -->
        <div v-if="historyData.length === 0" class="empty-state">
          <div class="empty-icon">🌱</div>
          <p>暂无面试记录，快去开启你的第一场挑战吧！</p>
        </div>

        <!-- 历史记录列表 -->
        <div class="history-list" v-else>
          <div class="history-item" v-for="(item, index) in historyData" :key="index">
            <div class="item-main">
              <div class="stat-icon" :class="item.role === '软件工程' ? 'sys-blue' : 'sys-purple'">
                <svg v-if="item.role === '软件工程'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
              </div>
              <div class="item-info">
                <div class="info-top">
                  <span class="user-name">{{ item.role }}</span>
                  <span class="role-tag tag-normal">共 {{ item.turnCount }} 轮对话</span>
                </div>
                <div class="info-bottom mono-num">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                  {{ item.date }}
                </div>
              </div>
            </div>

            <div class="item-actions">
              <div class="score-display mono-num" :class="item.score >= 80 ? 'score-high' : 'score-mid'">
                {{ item.score }} <span class="score-unit">分</span>
              </div>
              <div class="btn-group">
                <button class="action-btn outline-btn" @click="openReport(item.report)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                  评估报告
                </button>
                <button class="action-btn fill-btn" @click="openReview(item.sessionId)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                  实况回放
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 评估报告弹窗 -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div class="modal-overlay" v-if="selectedReport" @click.self="closeReport">
          <div class="modal-content glass-bento">
            <button class="close-icon-btn" @click="closeReport">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
            <div class="modal-header">
              <h3>📄 综合评估报告</h3>
              <p class="modal-subtitle">AI Comprehensive Analysis Report</p>
            </div>
            <div class="report-text-container">
              <div class="report-text" v-html="formatReport(selectedReport)"></div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 面试实况回放弹窗 -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div class="modal-overlay" v-if="isReviewModalOpen" @click.self="closeReview">
          <div class="modal-content glass-bento">
            <button class="close-icon-btn" @click="closeReview">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
            <div class="modal-header">
              <h3>🎧 面试实况还原</h3>
              <p class="modal-subtitle">Interview Playback & Trace</p>
            </div>
            
            <div class="review-chat-box">
              <div v-if="reviewDetails.length === 0" class="empty-state">暂无对话明细记录</div>
              <div class="turn-record" v-for="(turn, idx) in reviewDetails" :key="idx">
                
                <!-- AI提问气泡 -->
                <div class="chat-bubble ai-bubble">
                  <div class="bubble-avatar ai-avatar">AI</div>
                  <div class="bubble-content">
                    <div class="bubble-title">Round {{ turn.turnNumber }} - 面试官提问</div>
                    <div class="bubble-text">{{ turn.questionText }}</div>
                  </div>
                </div>

                <!-- 用户回答气泡 -->
                <div class="chat-bubble user-bubble">
                  <div class="bubble-content">
                    <div class="bubble-title">我的回答</div>
                    <div class="bubble-text">{{ turn.userAnswerText || '（未识别到有效音频）' }}</div>
                    
                    <!-- 音频回放按钮 -->
                    <button 
                      v-if="turn.audioUrl && turn.audioUrl !== 'TEXT_ONLY'" 
                      class="audio-pill-btn" 
                      :class="{ 'is-playing': playingUrl === turn.audioUrl }"
                      @click="playAudio(turn.audioUrl)">
                      <svg v-if="playingUrl === turn.audioUrl" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
                      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                      <span>{{ playingUrl === turn.audioUrl ? '正在复盘...' : '原声回放' }}</span>
                      <div v-if="playingUrl === turn.audioUrl" class="wave-anim"></div>
                    </button>
                    
                    <!-- 声学特征详情 -->
                    <div class="acoustic-details">
                      <span class="detail-tag nervousness">😨 紧张度: {{ turn.nervousness }}</span>
                      <span class="detail-tag confidence">🔥 自信度: {{ turn.confidence }}</span>
                      <span class="detail-tag clarity">📢 清晰度: {{ turn.clarity }}</span>
                    </div>

                  </div>
                  <div class="bubble-avatar user-avatar-chat">我</div>
                </div>

                <!-- AI评价面板 -->
                <div class="evaluation-panel">
                  <div class="eval-header">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                    智能诊断反馈
                  </div>
                  <div class="eval-scores mono-num">
                    <div class="score-pill"><span class="label">内容硬核度</span> <span class="val">{{ turn.contentScore }}</span></div>
                    <div class="score-pill"><span class="label">声学表达力</span> <span class="val">{{ turn.expressionScore }}</span></div>
                  </div>
                  <div class="eval-text">{{ turn.aiFeedback || '暂无详细评价' }}</div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

// 组件参数定义
const props = defineProps({
  userId: { type: [String, Number], required: true },
  isOverlay: { type: Boolean, default: false } 
})

// 接口基础地址
const API_BASE = "http://127.0.0.1:8081"

// DOM 引用
const trendChart = ref(null)
const dimChart = ref(null)

// 响应式数据
const historyData = ref([])
const selectedReport = ref(null)
const isReviewModalOpen = ref(false)
const reviewDetails = ref([])
const currentAudio = ref(null)
const playingUrl = ref('')

/**
 * 打开评估报告弹窗
 * @param {string} reportText - 评估报告文本
 */
const openReport = (reportText) => {
  selectedReport.value = reportText || "报告还在快马加鞭生成中，大模型需要十几秒钟思考，请稍后刷新页面查看哦~"
}

/**
 * 关闭评估报告弹窗
 */
const closeReport = () => {
  selectedReport.value = null
}

/**
 * 格式化评估报告文本（富文本渲染）
 * @param {string} text - 原始报告文本
 * @returns {string} 格式化后的HTML文本
 */
const formatReport = (text) => {
  if (!text) return '<p style="text-align:center; color:#94A3B8; margin-top:20px;">报告还在生成中...</p>';
  return text
    .replace(/### (.*?)(?:\n|$)/g, '<h3 class="report-h3">✦ $1</h3>') 
    .replace(/\*\*(.*?)\*\*/g, '<strong class="report-bold">$1</strong>') 
    .replace(/《(.*?)》/g, '<span class="res-tag tag-book"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg> $1</span>')
    .replace(/\[(.*?)\]/g, '<span class="res-tag tag-concept"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg> $1</span>')
    .replace(/- (.*?)(?:\n|$)/g, '<li class="report-li">$1</li>')
    .replace(/\n/g, '<br/>'); 
}

/**
 * 音频播放/暂停控制
 * @param {string} url - 音频地址
 */
const playAudio = (url) => {
  if (!url) return;
  // 暂停当前播放音频
  if (playingUrl.value === url && currentAudio.value) {
    currentAudio.value.pause();
    playingUrl.value = '';
    return;
  }
  // 切换新音频
  if (currentAudio.value) {
    currentAudio.value.pause();
  }
  currentAudio.value = new Audio(url);
  playingUrl.value = url;
  currentAudio.value.play();
  currentAudio.value.onended = () => {
    playingUrl.value = '';
  }
}

/**
 * 打开面试实况回放弹窗
 * @param {string} sessionId - 面试场次ID
 */
const openReview = async (sessionId) => {
  try {
    const res = await axios.get(`${API_BASE}/api/admin/session/${sessionId}/details`);
    if (res.data.status === 'success') {
      reviewDetails.value = Array.isArray(res.data) ? res.data : (res.data.data || []);
      isReviewModalOpen.value = true;
    }
  } catch (error) {
    console.error("获取复盘详情失败", error);
  }
}

/**
 * 关闭实况回放弹窗并停止音频
 */
const closeReview = () => {
  isReviewModalOpen.value = false;
  if (currentAudio.value) {
    currentAudio.value.pause();
    playingUrl.value = '';
  }
}

/**
 * 获取用户仪表盘数据
 */
const fetchRealDashboardData = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/dashboard/history/${props.userId}`)
    if (res.data.status === 'success') {
      const realData = res.data.data
      historyData.value = realData.historyList
      renderCharts(realData)
    }
  } catch (error) {
    console.error("获取真实面板数据失败:", error)
  }
}

/**
 * 渲染ECharts图表（趋势图+雷达图）
 * @param {object} data - 图表数据
 */
const renderCharts = (data) => {
  if (data.trendDates.length === 0) return;
  
  // 渲染得分趋势折线图
  const tc = echarts.init(trendChart.value)
  tc.setOption({
    title: { text: '综合得分趋势', textStyle: { fontSize: 15, fontWeight: 600, color: '#0F172A' }, left: '4%' },
    grid: { left: '8%', right: '8%', bottom: '15%', top: '25%' },
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.9)', borderColor: '#E2E8F0', textStyle: { color: '#0F172A' } },
    xAxis: { type: 'category', data: data.trendDates, axisLine: { lineStyle: { color: '#CBD5E1' } }, axisLabel: { color: '#64748B' } },
    yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { type: 'dashed', color: '#F1F5F9' } }, axisLabel: { color: '#64748B' } },
    series: [{ 
      data: data.trendScores, type: 'line', smooth: true, symbolSize: 8,
      itemStyle: { color: '#3B82F6', borderWidth: 2, borderColor: '#fff' },
      lineStyle: { width: 3, color: '#3B82F6' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(59,130,246,0.2)'}, {offset: 1, color: 'rgba(59,130,246,0)'}]) }
    }]
  })

  // 渲染能力雷达图
  const dc = echarts.init(dimChart.value)
  const latestRole = historyData.value.length > 0 ? historyData.value[0].role : '软件工程';
  const indicator = latestRole === '网络安全' ? [
    { name: '漏洞挖掘', max: 100 }, { name: '攻防逻辑', max: 100 },
    { name: '应急抗压', max: 100 }, { name: '安全自信', max: 100 }, { name: '风险汇报', max: 100 }
  ] : [
    { name: '架构深度', max: 100 }, { name: '业务逻辑', max: 100 },
    { name: '线上抗压', max: 100 }, { name: '技术自信', max: 100 }, { name: '需求沟通', max: 100 }
  ];

  const getAvg = (arr) => arr && arr.length ? (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1) : 0;

  dc.setOption({
    title: { text: `能力雷达 (${latestRole})`, textStyle: { fontSize: 15, fontWeight: 600, color: '#0F172A' }, left: 'center' },
    tooltip: { backgroundColor: 'rgba(255,255,255,0.9)', borderColor: '#E2E8F0', textStyle: { color: '#0F172A' } },
    radar: {
      center: ['50%', '55%'], radius: '60%', indicator: indicator,
      axisName: { color: '#475569', fontSize: 12, fontWeight: 500 },
      splitNumber: 4,
      splitArea: { areaStyle: { color: ['rgba(241,245,249,0.3)', 'rgba(248,250,252,0.3)'] } },
      splitLine: { lineStyle: { color: '#E2E8F0' } },
      axisLine: { lineStyle: { color: '#E2E8F0' } }
    },
    series: [{
      type: 'radar', 
      itemStyle: { color: '#8B5CF6' },
      lineStyle: { width: 2, color: '#8B5CF6' },
      areaStyle: { color: 'rgba(139,92,246,0.2)' },
      data: [{
        value: [ getAvg(data.dimensions.tech), getAvg(data.dimensions.logic), getAvg(data.dimensions.relax), getAvg(data.dimensions.conf), getAvg(data.dimensions.clarity) ],
        name: '能力均值'
      }]
    }]
  })

  // 监听窗口缩放，自适应图表尺寸
  window.addEventListener('resize', () => { tc.resize(); dc.resize(); })
}

// 组件挂载后获取数据
onMounted(() => { fetchRealDashboardData() })
</script>

<style scoped>
/* ==========================================
   Apple/Vercel 级极简智算风 (Minimalist Glass)
   - 保持与 Admin 面板完全一致的视觉语言
============================================= */
* { box-sizing: border-box; }

.student-dashboard-container {
  position: relative; width: 100vw; height: 100vh;
  background-color: #F8FAFC; color: #0F172A;
  font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
  display: flex; justify-content: center; align-items: center; overflow: hidden;
}

/* Overlay 模式样式重置 */
.is-overlay-mode {
  position: absolute; top: 0; left: 0; 
  width: 100vw; height: 100vh;
  overflow-y: auto;
  z-index: 2000;
  background-color: rgba(248, 250, 252, 0.4);
  backdrop-filter: blur(16px);
  display: flex; justify-content: center; align-items: flex-start;
  padding: 40px 0; 
}
.is-overlay-mode .glass-bento { box-shadow: 0 20px 50px rgba(15,23,42,0.1); }

.mono-num { font-family: 'JetBrains Mono', 'SF Mono', monospace; letter-spacing: -0.5px; }

/* 背景光晕 */
.ambient-glow { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.5; z-index: 0; animation: float 15s infinite ease-in-out alternate; }
.blob-1 { top: -10%; left: -10%; width: 50vw; height: 50vw; background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, rgba(255,255,255,0) 70%); }
.blob-2 { bottom: -10%; right: -10%; width: 40vw; height: 40vw; background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, rgba(255,255,255,0) 70%); animation-delay: -5s; }
@keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(30px, 50px) scale(1.1); } }

/* 核心面板 Bento Box */
.glass-bento {
  background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.8); box-shadow: 0 10px 40px -10px rgba(15, 23, 42, 0.05); border-radius: 24px;
}

.acoustic-details {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}
.detail-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.nervousness { background: rgba(255, 155, 133, 0.2); color: #E67E22; }
.confidence { background: rgba(135, 211, 124, 0.2); color: #27AE60; }
.clarity { background: rgba(129, 207, 224, 0.2); color: #2980B9; }

/* 让它动起来，更符合你的“小清新”风格 */
.detail-tag:hover {
  transform: translateY(-2px);
  transition: all 0.3s ease;
}


.dashboard-content { 
  position: relative; 
  z-index: 1; 
  width: 90%; 
  max-width: 1200px; 
  min-height: 85vh;
  height: auto;
  display: flex; 
  flex-direction: column; 
  padding: 30px; 
  gap: 24px; }

/* 头部 */
.bento-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px solid rgba(15, 23, 42, 0.06); }
.header-title { display: flex; align-items: center; gap: 12px; }
.header-title .icon { width: 28px; height: 28px; color: #3B82F6; }
.header-title h2 { font-size: 22px; font-weight: 600; margin: 0; display: flex; align-items: center; gap: 12px; }
.badge-pro { font-size: 11px; font-weight: 700; padding: 4px 8px; background: #0F172A; color: #fff; border-radius: 6px; text-transform: uppercase;}
.action-group { display: flex; gap: 12px; }

.exit-btn {
  display: flex; align-items: center; gap: 8px; padding: 8px 16px; 
  border: none; border-radius: 10px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;
}
.exit-btn svg { width: 16px; height: 16px; }
.sys-red-btn { background: rgba(15, 23, 42, 0.05); color: #475569; }
.sys-red-btn:hover { background: rgba(239, 68, 68, 0.1); color: #EF4444; }
.sys-blue-btn { background: rgba(59, 130, 246, 0.1); color: #2563EB; }
.sys-blue-btn:hover { background: #3B82F6; color: #fff; }

/* 图表区 */
.charts-grid { display: flex; gap: 24px; height: 320px; flex-shrink: 0; }
.chart-card { flex: 1; background: rgba(255, 255, 255, 0.7); border: 1px solid rgba(255, 255, 255, 0.9); border-radius: 20px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
.echart-container { width: 100%; height: 100%; }

/* 列表区 */
.history-panel { flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 0; background: rgba(255, 255, 255, 0.7); border: 1px solid rgba(255, 255, 255, 0.9); border-radius: 20px; }
.panel-title { padding: 20px 24px; font-size: 16px; font-weight: 600; border-bottom: 1px solid rgba(15, 23, 42, 0.04); display: flex; align-items: center; gap: 8px; }
.panel-title svg { width: 18px; height: 18px; color: #64748B; }
.history-list { 
  flex: none; 
  overflow-y: visible; 
  padding: 12px; }
.history-list::-webkit-scrollbar { width: 6px; }
.history-list::-webkit-scrollbar-thumb { background: rgba(15, 23, 42, 0.1); border-radius: 10px; }

.history-item { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; margin-bottom: 8px; border-radius: 16px; transition: background 0.2s; }
.history-item:hover { background: rgba(255, 255, 255, 0.8); box-shadow: 0 4px 12px rgba(0,0,0,0.02); }
.item-main { display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; justify-content: center; align-items: center; }
.stat-icon svg { width: 22px; height: 22px; }
.sys-blue { background: #EFF6FF; color: #3B82F6; }
.sys-purple { background: #FAF5FF; color: #A855F7; }

.info-top { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.user-name { font-size: 15px; font-weight: 600; color: #1E293B; }
.role-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.tag-normal { background: #F1F5F9; color: #475569; }
.info-bottom { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #94A3B8; }
.info-bottom svg { width: 14px; height: 14px; }

.item-actions { display: flex; align-items: center; gap: 24px; }
.score-display { font-size: 20px; font-weight: 700; }
.score-high { color: #059669; }
.score-mid { color: #D97706; }
.score-unit { font-size: 12px; font-weight: 500; opacity: 0.7; }
.btn-group { display: flex; gap: 8px; }

.action-btn { display: flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.action-btn svg { width: 14px; height: 14px; }
.outline-btn { background: transparent; border: 1px solid #CBD5E1; color: #475569; }
.outline-btn:hover { background: #F8FAFC; border-color: #94A3B8; color: #0F172A; }
.fill-btn { background: #0F172A; border: 1px solid #0F172A; color: #fff; }
.fill-btn:hover { background: #334155; }

/* --- 弹窗 Modal --- */
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(8px); display: flex; justify-content: center; align-items: center; z-index: 9999; }
.modal-content { width: 90%; max-width: 800px; height: 85vh; padding: 0; display: flex; flex-direction: column; position: relative; overflow: hidden; }
.close-icon-btn { position: absolute; top: 20px; right: 20px; background: rgba(15, 23, 42, 0.05); border: none; border-radius: 50%; width: 32px; height: 32px; display: flex; justify-content: center; align-items: center; color: #64748B; cursor: pointer; transition: all 0.2s; z-index: 10; }
.close-icon-btn:hover { background: rgba(15, 23, 42, 0.1); color: #0F172A; }
.modal-header { padding: 24px 30px; border-bottom: 1px solid rgba(15, 23, 42, 0.06); background: rgba(255, 255, 255, 0.5); }
.modal-header h3 { margin: 0 0 4px 0; font-size: 18px; color: #0F172A; }
.modal-subtitle { margin: 0; font-size: 13px; color: #64748B; font-family: 'JetBrains Mono', monospace; }

/* 实况回放气泡样式 (复用 Admin) */
.review-chat-box { flex: 1; overflow-y: auto; padding: 24px 30px; display: flex; flex-direction: column; gap: 30px; }
.review-chat-box::-webkit-scrollbar { width: 6px; }
.review-chat-box::-webkit-scrollbar-thumb { background: rgba(15, 23, 42, 0.1); border-radius: 10px; }
.turn-record { padding-bottom: 24px; border-bottom: 1px dashed rgba(15, 23, 42, 0.1); }
.chat-bubble { display: flex; gap: 16px; margin-bottom: 16px; max-width: 90%; }
.bubble-avatar { width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0; display: flex; justify-content: center; align-items: center; font-size: 12px; font-weight: bold; }
.ai-avatar { background: #0F172A; color: #fff; }
.user-avatar-chat { background: #3B82F6; color: #fff; }
.bubble-content { padding: 16px; border-radius: 16px; font-size: 14px; line-height: 1.6; }
.ai-bubble .bubble-content { background: #F1F5F9; border-top-left-radius: 4px; color: #334155;}
.user-bubble { align-self: flex-end; justify-content: flex-end; }
.user-bubble .bubble-content { background: #EFF6FF; border-top-right-radius: 4px; color: #1E3A8A; }
.bubble-title { font-size: 12px; font-weight: 600; margin-bottom: 6px; opacity: 0.7; }
.evaluation-panel { margin-left: 52px; background: #FFFBEB; border: 1px solid #FEF3C7; border-radius: 12px; padding: 16px; }
.eval-header { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: #D97706; margin-bottom: 12px; }
.eval-header svg { width: 14px; height: 14px; }
.score-pill { background: #fff; padding: 4px 10px; border-radius: 8px; border: 1px solid #FDE68A; font-size: 12px; display: inline-flex; gap: 8px; margin-right: 10px; }
.score-pill .label { color: #92400E; }
.score-pill .val { font-weight: 700; color: #B45309; }
.eval-text { font-size: 13px; color: #78350F; line-height: 1.6; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; color: #94A3B8; font-size: 14px; }

/* 极简原声回放按钮 */
.audio-pill-btn { display: inline-flex; align-items: center; gap: 6px; margin-top: 10px; padding: 6px 12px; border-radius: 12px; border: 1px solid #BFDBFE; background: #fff; color: #2563EB; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; position: relative; overflow: hidden; }
.audio-pill-btn svg { width: 14px; height: 14px; }
.audio-pill-btn:hover { background: #EFF6FF; }
.audio-pill-btn.is-playing { background: #3B82F6; color: #fff; border-color: #3B82F6; }
.wave-anim { position: absolute; inset: 0; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); background-size: 200% 100%; animation: waveLoading 1.5s infinite linear; pointer-events: none; }

/* 报告排版 (Report Typo) */
.report-text-container { flex: 1; overflow-y: auto; padding: 24px 30px; }
.report-text-container::-webkit-scrollbar { width: 6px; }
.report-text-container::-webkit-scrollbar-thumb { background: rgba(15, 23, 42, 0.1); border-radius: 10px; }
.report-text { font-size: 15px; color: #334155; line-height: 1.8; }
:deep(.report-h3) { color: #0F172A; font-size: 18px; margin: 28px 0 12px 0; border-bottom: 1px solid #E2E8F0; padding-bottom: 8px; display: flex; align-items: center; gap: 8px; }
:deep(.report-bold) { color: #1E293B; background: rgba(241, 245, 249, 0.8); padding: 2px 6px; border-radius: 6px; }
:deep(.res-tag) { display: inline-flex; align-items: center; gap: 6px; margin: 6px 8px 6px 0; padding: 6px 12px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: default; }
:deep(.tag-book) { background: #F8FAFC; border: 1px solid #E2E8F0; color: #475569; }
:deep(.tag-concept) { background: #EFF6FF; border: 1px solid #BFDBFE; color: #2563EB; }
:deep(.res-tag svg) { width: 14px; height: 14px; }
:deep(.report-li) { position: relative; padding-left: 20px; margin-bottom: 8px; list-style: none; }
:deep(.report-li::before) { content: ""; position: absolute; left: 0; top: 10px; width: 6px; height: 6px; border-radius: 50%; background: #3B82F6; }

.modal-fade-enter-active { animation: scaleUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes scaleUp { 0% { transform: scale(0.95); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
@keyframes waveLoading { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }
</style>