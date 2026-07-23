<template>
  <div class="admin-dashboard-container">
    <!-- 背景装饰元素 -->
    <div class="ambient-glow blob-1"></div>
    <div class="ambient-glow blob-2"></div>

    <!-- 仪表盘主内容区域 -->
    <div class="dashboard-content glass-bento">
      <!-- 头部标题栏 -->
      <header class="bento-header">
        <div class="header-title">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
          <h2>全局面试大盘 <span class="badge-pro">Admin Cockpit</span></h2>
        </div>
        <button class="exit-btn" @click="$emit('back')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
          退出
        </button>
      </header>

      <!-- 数据统计卡片网格 -->
      <div class="stats-grid">
        <div class="stat-card bento-card">
          <div class="stat-icon sys-blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          </div>
          <div class="stat-info">
            <div class="stat-title">注册考生总数</div>
            <div class="stat-value mono-num">{{ stats.totalStudents }} <span class="unit">人</span></div>
          </div>
        </div>
        
        <div class="stat-card bento-card">
          <div class="stat-icon sys-purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
          </div>
          <div class="stat-info">
            <div class="stat-title">已完成面试场次</div>
            <div class="stat-value mono-num">{{ stats.totalSessions }} <span class="unit">场</span></div>
          </div>
        </div>

        <div class="stat-card bento-card">
          <div class="stat-icon sys-orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>
          </div>
          <div class="stat-info">
            <div class="stat-title">全局平均得分</div>
            <div class="stat-value mono-num highlight-score">{{ stats.avgScore }} <span class="unit">分</span></div>
          </div>
        </div>
      </div>

      <!-- 最新面试记录面板 -->
      <div class="history-panel bento-card">
        <div class="panel-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
          最新面试战报
        </div>
        
        <!-- 空数据状态 -->
        <div v-if="stats.recentSessions.length === 0" class="empty-state">
          <div class="empty-icon">☁️</div>
          <p>当前系统暂无面试数据</p>
        </div>

        <!-- 面试记录列表 -->
        <div class="history-list" v-else>
          <div class="history-item" v-for="(item, index) in stats.recentSessions" :key="index">
            <div class="item-main">
              <div class="user-avatar">
                {{ item.username ? item.username.charAt(0).toUpperCase() : 'U' }}
              </div>
              <div class="item-info">
                <div class="info-top">
                  <span class="user-name">{{ item.username }}</span>
                  <span class="role-tag" :class="item.role === '软件工程' ? 'tag-se' : 'tag-sec'">{{ item.role }}</span>
                </div>
                <div class="info-bottom">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                  {{ item.endTime }}
                </div>
              </div>
            </div>
            
            <div class="item-actions">
              <div class="score-display mono-num" :class="item.score >= 80 ? 'score-high' : 'score-mid'">
                {{ item.score }} <span class="score-unit">分</span>
              </div>
              <button class="review-btn" @click="viewDetails(item.sessionId)">
                查看复盘 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 面试详情弹窗 -->
    <Transition name="modal-fade">
      <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
        <div class="modal-content glass-bento">
          <button class="close-icon-btn" @click="closeModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
          
          <div class="modal-header">
            <h3>面试深度复盘记录</h3>
            <p class="modal-subtitle">System AI Evaluation Engine</p>
          </div>

          <!-- 对话复盘内容 -->
          <div class="review-chat-box">
            <div v-if="currentSessionDetails.length === 0" class="empty-state">
              暂无对话明细记录
            </div>
            
            <div class="turn-record" v-for="(turn, idx) in currentSessionDetails" :key="idx">
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
                  <div class="bubble-title">考生回答</div>
                  <div class="bubble-text">{{ turn.userAnswerText || '（未识别到有效音频）' }}</div>
                </div>
                <div class="bubble-avatar user-avatar-chat">考</div>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// 仪表盘统计数据
const stats = ref({
  totalStudents: 0,
  totalSessions: 0,
  avgScore: 0,
  recentSessions: []
})

// 弹窗控制变量
const showModal = ref(false)
// 当前选中的面试详情数据
const currentSessionDetails = ref([])

/**
 * 获取管理员仪表盘统计数据
 */
const fetchStats = async () => {
  try {
    const res = await axios.get('http://localhost:8081/api/admin/dashboard/stats')
    if (res.data.status === 'success') {
      stats.value = res.data.data
    }
  } catch (error) {
    console.error("获取大盘数据失败", error)
  }
}

/**
 * 查看面试详情复盘
 * @param {string} sessionId - 面试场次ID
 */
const viewDetails = async (sessionId) => {
  try {
    const res = await axios.get(`http://localhost:8081/api/admin/session/${sessionId}/details`)
    if (res.data.status === 'success') {
      currentSessionDetails.value = res.data.data
      showModal.value = true
    }
  } catch (error) {
    console.error("获取详情失败", error)
  }
}

/**
 * 关闭详情弹窗并清空数据
 */
const closeModal = () => {
  showModal.value = false
  currentSessionDetails.value = []
}

// 组件挂载后获取数据
onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
/* ==========================================
   Apple/Vercel 级极简智算风 (Minimalist Glass)
============================================= */

/* 基础排版与变量 */
* {
  box-sizing: border-box;
}
.admin-dashboard-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  background-color: #F8FAFC; /* 极浅的冷灰底色 */
  color: #0F172A;
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

/* 等宽数字字体 */
.mono-num {
  font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', monospace;
  letter-spacing: -0.5px;
}

/* --- 背景环境光 (Ambient Glow) --- */
.ambient-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
  z-index: 0;
  animation: float 15s infinite ease-in-out alternate;
}
.blob-1 {
  top: -10%; left: -10%;
  width: 50vw; height: 50vw;
  background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, rgba(255,255,255,0) 70%);
}
.blob-2 {
  bottom: -10%; right: -10%;
  width: 40vw; height: 40vw;
  background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, rgba(255,255,255,0) 70%);
  animation-delay: -5s;
}
@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, 50px) scale(1.1); }
}

/* --- 核心面板 (Glass Bento Box) --- */
.glass-bento {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 10px 40px -10px rgba(15, 23, 42, 0.05), inset 0 1px 0 rgba(255, 255, 255, 1);
  border-radius: 24px;
}

.dashboard-content {
  position: relative;
  z-index: 1;
  width: 90%;
  max-width: 1200px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  padding: 30px;
  gap: 24px;
}

/* --- 头部 --- */
.bento-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}
.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-title .icon {
  width: 28px; height: 28px;
  color: #3B82F6;
}
.header-title h2 {
  font-size: 22px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}
.badge-pro {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  background: #0F172A;
  color: #fff;
  border-radius: 6px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.exit-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(15, 23, 42, 0.05);
  border: 1px solid transparent;
  border-radius: 10px;
  color: #475569;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.exit-btn svg { width: 16px; height: 16px; }
.exit-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

/* --- 顶部统计卡片 --- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.bento-card {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
  border-radius: 20px;
  padding: 24px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.bento-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.05);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}
.stat-icon {
  width: 56px; height: 56px;
  border-radius: 16px;
  display: flex; justify-content: center; align-items: center;
}
.stat-icon svg { width: 28px; height: 28px; }
.sys-blue { background: #EFF6FF; color: #3B82F6; }
.sys-purple { background: #FAF5FF; color: #A855F7; }
.sys-orange { background: #FFF7ED; color: #F97316; }

.stat-info { display: flex; flex-direction: column; gap: 4px; }
.stat-title { font-size: 14px; color: #64748B; font-weight: 500; }
.stat-value { font-size: 32px; font-weight: 700; color: #0F172A; }
.stat-value .unit { font-size: 14px; color: #94A3B8; font-weight: 500; }
.highlight-score { color: #F97316; }

/* --- 列表区域 --- */
.history-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0; /* Override */
}
.panel-title {
  padding: 20px 24px;
  font-size: 16px; font-weight: 600; color: #0F172A;
  border-bottom: 1px solid rgba(15, 23, 42, 0.04);
  display: flex; align-items: center; gap: 8px;
}
.panel-title svg { width: 18px; height: 18px; color: #64748B; }

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}
.history-list::-webkit-scrollbar { width: 6px; }
.history-list::-webkit-scrollbar-thumb { background: rgba(15, 23, 42, 0.1); border-radius: 10px; }

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  margin-bottom: 8px;
  background: transparent;
  border-radius: 16px;
  transition: all 0.2s ease;
}
.history-item:hover {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

.item-main { display: flex; align-items: center; gap: 16px; }
.user-avatar {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #E2E8F0, #F1F5F9);
  color: #475569;
  display: flex; justify-content: center; align-items: center;
  font-size: 18px; font-weight: 600;
  border: 1px solid #fff;
}
.info-top { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.user-name { font-size: 15px; font-weight: 600; color: #1E293B; }
.role-tag {
  font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600;
}
.tag-se { background: #DBEAFE; color: #1D4ED8; }
.tag-sec { background: #DCFCE7; color: #15803D; }

.info-bottom {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; color: #94A3B8;
}
.info-bottom svg { width: 14px; height: 14px; }

.item-actions { display: flex; align-items: center; gap: 24px; }
.score-display { font-size: 20px; font-weight: 700; }
.score-high { color: #059669; }
.score-mid { color: #D97706; }
.score-unit { font-size: 12px; font-weight: 500; opacity: 0.7; }

.review-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px;
  background: #0F172A;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 13px; font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.review-btn svg { width: 14px; height: 14px; transition: transform 0.2s; }
.review-btn:hover { background: #334155; }
.review-btn:hover svg { transform: translateX(2px); }

/* --- 弹窗 Modal (Chat UI) --- */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  display: flex; justify-content: center; align-items: center;
  z-index: 999;
}
.modal-content {
  width: 90%; max-width: 760px; height: 85vh;
  padding: 0;
  display: flex; flex-direction: column;
  position: relative;
  overflow: hidden;
}
.close-icon-btn {
  position: absolute; top: 20px; right: 20px;
  background: rgba(15, 23, 42, 0.05); border: none; border-radius: 50%;
  width: 32px; height: 32px;
  display: flex; justify-content: center; align-items: center;
  color: #64748B; cursor: pointer; transition: all 0.2s;
  z-index: 10;
}
.close-icon-btn:hover { background: rgba(15, 23, 42, 0.1); color: #0F172A; }

.modal-header {
  padding: 24px 30px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  background: rgba(255, 255, 255, 0.5);
}
.modal-header h3 { margin: 0 0 4px 0; font-size: 18px; color: #0F172A; }
.modal-subtitle { margin: 0; font-size: 13px; color: #64748B; font-family: 'JetBrains Mono', monospace; }

.review-chat-box {
  flex: 1; overflow-y: auto;
  padding: 24px 30px;
  display: flex; flex-direction: column; gap: 30px;
}
.review-chat-box::-webkit-scrollbar { width: 6px; }
.review-chat-box::-webkit-scrollbar-thumb { background: rgba(15, 23, 42, 0.1); border-radius: 10px; }

.turn-record {
  display: flex; flex-direction: column; gap: 16px;
  padding-bottom: 24px; border-bottom: 1px dashed rgba(15, 23, 42, 0.1);
}
.turn-record:last-child { border-bottom: none; }

/* 气泡通用 */
.chat-bubble { display: flex; gap: 16px; max-width: 90%; }
.ai-bubble { align-self: flex-start; }
.user-bubble { align-self: flex-end; justify-content: flex-end; }

.bubble-avatar {
  width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
  display: flex; justify-content: center; align-items: center;
  font-size: 12px; font-weight: bold;
}
.ai-avatar { background: #0F172A; color: #fff; }
.user-avatar-chat { background: #3B82F6; color: #fff; }

.bubble-content {
  padding: 16px; border-radius: 16px;
  font-size: 14px; line-height: 1.6;
}
.ai-bubble .bubble-content {
  background: #F1F5F9; border-top-left-radius: 4px; color: #334155;
}
.user-bubble .bubble-content {
  background: #EFF6FF; border-top-right-radius: 4px; color: #1E3A8A;
}
.bubble-title { font-size: 12px; font-weight: 600; margin-bottom: 6px; opacity: 0.7; }

/* 评估面板 */
.evaluation-panel {
  margin-left: 52px; margin-top: 4px;
  background: #FFFBEB; border: 1px solid #FEF3C7; border-radius: 12px;
  padding: 16px;
}
.eval-header {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 600; color: #D97706; margin-bottom: 12px;
}
.eval-header svg { width: 14px; height: 14px; }
.eval-scores {
  display: flex; gap: 12px; margin-bottom: 12px;
}
.score-pill {
  background: #fff; padding: 4px 10px; border-radius: 8px; border: 1px solid #FDE68A;
  font-size: 12px; display: flex; gap: 8px; align-items: center;
}
.score-pill .label { color: #92400E; }
.score-pill .val { font-weight: 700; color: #B45309; }
.eval-text { font-size: 13px; color: #78350F; line-height: 1.6; }

/* 空状态 */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 200px; color: #94A3B8; font-size: 14px;
}
.empty-icon { font-size: 32px; margin-bottom: 12px; opacity: 0.5; }

/* 动画 */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-active .modal-content { animation: scaleUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes scaleUp {
  0% { transform: scale(0.95) translateY(10px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}
</style>