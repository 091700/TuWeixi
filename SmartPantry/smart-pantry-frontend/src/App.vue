<template>
  <div class="aurora-bg"></div>

  <div class="nexus-dashboard">
    <div class="glass-container">
      <header class="glass-header">
        <div class="brand-zone">
          <h1 class="brand-title">美味鲜造屋 <span class="brand-badge">by twx</span></h1>
          <span class="brand-subtitle">智能食材管理与风味搭配分析中心</span>
        </div>
        <button class="action-btn-premium primary" @click="addFormVisible = true">
          <div class="btn-glow"></div>
          <Plus :size="20" stroke-width="3" /> 
          <span>添加新食材</span>
        </button>
      </header>

      <div class="workspace-grid">
        <section class="glass-panel main-panel">
          <div class="panel-header">
            <div class="title-icon"><Clock :size="20" /></div>
            <h2 class="panel-title">食材新鲜度监控中心</h2>
          </div>
          
          <el-empty v-if="fridgeItems.length === 0" description="暂无食材记录，快来添加吧～" class="empty-state" />
          
          <div v-else class="material-grid">
            <MaterialCard 
              v-for="item in fridgeItems" 
              :key="item.id" 
              :item="item" 
              :name="getDictName(item.ingredientId)"
              @consume="consumeItem"
              @discard="discardItem"
            />
          </div>
        </section>

        <aside class="sidebar-grid">
          
          <section class="glass-panel chart-panel">
            <div class="panel-header compact">
              <div class="title-icon magic"><PieChart :size="20" /></div>
              <h2 class="panel-title">食材库存分类统计</h2>
            </div>
            <div ref="chartRef" class="echarts-container"></div>
          </section>

          <section class="glass-panel magic-panel">
            <div class="panel-header compact">
              <div class="title-icon magic"><Wand2 :size="20" /></div>
              <h2 class="panel-title">食材风味搭配分析</h2>
            </div>
            
            <div class="magic-core">
              <el-select 
                v-model="recipeSelection" multiple 
                placeholder="选择要搭配的食材..." 
                class="nexus-select">
                <el-option v-for="dict in dictItems" :key="dict.id" :label="dict.name" :value="dict.id" />
              </el-select>
              
              <button class="action-btn-premium magic" @click="checkRecipe" :disabled="checking || recipeSelection.length === 0">
                <div class="btn-glow"></div>
                <Zap v-if="!checking" :size="18" />
                <span>{{ checking ? '分析中...' : '分析食材搭配' }}</span>
              </button>

              <transition name="fade">
                <div v-if="harmonyResultVisible" class="result-display">
                  <div class="score-display" :style="{ color: harmonyColor }">
                    <span class="score-val">{{ harmonyScore }}</span><span class="score-unit">分</span>
                  </div>
                  <div class="harmony-comment">{{ harmonyText }}</div>
                </div>
              </transition>
            </div>
          </section>
        </aside>
      </div>
    </div>

    <el-dialog v-model="addFormVisible" width="620px" class="premium-dialog" :show-close="false" align-center>
      <div class="p-dialog-content">
        <div class="p-dialog-side">
          <div class="side-icon"><Plus :size="32" /></div>
          <h3>添加新食材</h3>
          <p>将食材录入系统，我们会实时监控其新鲜度，提醒您及时食用。</p>
        </div>
        <div class="p-dialog-main">
          <el-form :model="addForm" layout="vertical" label-position="top">
            <el-form-item label="食材名称">
              <el-select v-model="addForm.ingredientInput" filterable allow-create default-first-option placeholder="搜索或新增食材..." style="width: 100%">
                <el-option v-for="dict in dictItems" :key="dict.id" :label="dict.name" :value="dict.id" />
              </el-select>
            </el-form-item>
            <div class="form-split">
              <el-form-item label="储存方式">
                <el-select v-model="addForm.storageType" style="width: 100%">
                  <el-option label="冷冻（-18℃）" :value="0" />
                  <el-option label="冷藏（4℃）" :value="1" />
                  <el-option label="常温保存" :value="2" />
                </el-select>
              </el-form-item>
              <el-form-item label="初始温度 (°C)">
                <el-input-number v-model="addForm.currentTemp" :min="-20" :max="40" :step="0.5" controls-position="right" style="width: 100%" />
              </el-form-item>
            </div>
            <div class="p-dialog-footer">
              <button class="btn-flat" @click="addFormVisible = false">取消</button>
              <button class="action-btn-premium primary" @click="submitAdd" :disabled="adding">
                <span>{{ adding ? '添加中...' : '确认添加' }}</span>
              </button>
            </div>
          </el-form>
        </div>
      </div>
    </el-dialog>

    <div class="fixed-mascot" @click="pokeMascot">
      <img v-if="mascotState === 'idle'" src="/nailong.png" class="mascot float-anim" alt="待机" />
      <video v-else-if="mascotState === 'happy'" src="/nailongdaxiao.webm" class="mascot" autoplay loop muted></video>
      <video v-else-if="mascotState === 'warning'" src="/nailonghuishou.webm" class="mascot" autoplay loop muted></video>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, shallowRef, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage, ElNotification } from 'element-plus'
import * as echarts from 'echarts'
// 加入了 Zap 图标用于魔法按钮
import { Plus, Clock, Wand2, PieChart, X, Zap } from 'lucide-vue-next'
// 严格使用你的原版路径
import MaterialCard from './components/MaterialCard.vue'

// 绝对不改你的基础路径和接口！
const API_BASE = 'http://localhost:8080/api/pantry'
const dictItems = ref([])
const fridgeItems = ref([])

const mascotState = ref('idle')
let mascotTimer = null
const changeMascotState = (state, duration = 4000) => {
  mascotState.value = state
  if (mascotTimer) clearTimeout(mascotTimer)
  mascotTimer = setTimeout(() => { mascotState.value = 'idle' }, duration)
}
const pokeMascot = () => { changeMascotState('happy', 2000) }

const addFormVisible = ref(false)
const adding = ref(false)
const addForm = reactive({ ingredientInput: null, storageType: 1, currentTemp: 4.0, initialStatus: 5 })

const recipeSelection = ref([])
const checking = ref(false)
const harmonyResultVisible = ref(false)
const harmonyScore = ref(0)
const harmonyText = ref('')

const chartRef = ref(null)
const pieChart = shallowRef(null)

onMounted(() => { 
  fetchDict(); 
  fetchFridge();
  window.addEventListener('resize', () => pieChart.value?.resize());
})

// 辅助方法：获取完整字典项，用于图表分类
const getDictEntry = (id) => dictItems.value.find(d => d.id === id)
// 保持你原有的方法名，供模板调用
const getDictName = (id) => getDictEntry(id)?.name || '未知'

// 优化后的图表渲染逻辑：按 category 分类
const updateChart = () => {
  if (fridgeItems.value.length === 0 || !chartRef.value) return
  if (!pieChart.value) pieChart.value = echarts.init(chartRef.value)

  const categoryMap = {}
  
  fridgeItems.value.forEach(item => {
    const entry = getDictEntry(item.ingredientId)
    // 假设后端字典有 category 字段，如果没有则归为“未归类”
    const catName = entry?.category || '未归类'
    const itemName = entry?.name || '未知食材'
    
    if (!categoryMap[catName]) {
      categoryMap[catName] = { total: 0, details: {} }
    }
    categoryMap[catName].total++
    categoryMap[catName].details[itemName] = (categoryMap[catName].details[itemName] || 0) + 1
  })

  const chartData = Object.entries(categoryMap).map(([name, data]) => ({
    name, value: data.total, details: data.details
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderRadius: 12,
      borderWidth: 0,
      shadowBlur: 15,
      shadowColor: 'rgba(0,0,0,0.1)',
      padding: 12,
      formatter: (params) => {
        const data = params.data;
        let detailHtml = `<div style="font-weight:800; color:#5D4037; margin-bottom:8px; border-bottom:1px solid #eee; padding-bottom:4px">${data.name}</div>`;
        Object.entries(data.details).forEach(([name, count]) => {
          detailHtml += `<div style="display:flex; justify-content:space-between; gap:20px; font-size:12px; color:#8D7B68">
            <span>${name}</span> <span>${count} 份</span>
          </div>`;
        });
        return detailHtml;
      }
    },
    series: [{
      name: '库存分布', type: 'pie', radius: ['30%', '70%'], center: ['50%', '55%'],
      roseType: 'radius',
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 3 },
      label: {
        show: true, position: 'outside', formatter: '{b}\n{c}件',
        color: '#5D4037', fontSize: 12, fontWeight: 600
      },
      labelLine: { length: 10, length2: 15, lineStyle: { color: '#D2B48C' } },
      data: chartData
    }],
    color: ['#E07A5F', '#81B29A', '#F2CC8F', '#FF8FAB', '#A8DADC', '#D4A373']
  }
  pieChart.value.setOption(option)
}

watch(fridgeItems, () => {
  nextTick(() => { updateChart() })
}, { deep: true })

// 坚决不改这里的接口路径
const fetchDict = async () => { const res = await axios.get(`${API_BASE}/dict`); dictItems.value = res.data }
const fetchFridge = async () => { const res = await axios.get(`${API_BASE}/my-fridge`); fridgeItems.value = res.data }

const submitAdd = async () => {
  if (!addForm.ingredientInput) { ElMessage.warning('请选择要添加的食材'); return }
  adding.value = true
  try {
    const payload = { ...addForm }
    const res = await axios.post(`${API_BASE}/add`, payload)
    ElNotification({ title: '添加成功', message: res.data, type: 'success' })
    addFormVisible.value = false
    setTimeout(() => { fetchDict(); fetchFridge() }, 500)
    changeMascotState('happy', 3000)
  } catch (error) {
    ElMessage.error('添加失败，请稍后重试')
    setTimeout(fetchFridge, 1000)
  } finally { adding.value = false }
}

const consumeItem = async (id) => {
  try { await axios.delete(`${API_BASE}/consume/${id}`); changeMascotState('happy', 3000); fetchFridge() } 
  catch (e) { ElMessage.error('操作失败，请稍后重试') }
}

const discardItem = async (id) => {
  try { await axios.delete(`${API_BASE}/discard/${id}`); changeMascotState('warning', 3000); fetchFridge() } 
  catch (e) { ElMessage.error('操作失败，请稍后重试') }
}

const checkRecipe = async () => {
  if (recipeSelection.value.length === 0) return
  checking.value = true
  harmonyResultVisible.value = false
  try {
    const res = await axios.post(`${API_BASE}/check-recipe`, { ids: recipeSelection.value })
    const resultStr = res.data
    const scoreMatch = resultStr.match(/味觉和谐度：([\d.]+)分/)
    if (scoreMatch) {
      harmonyScore.value = parseFloat(scoreMatch[1])
      harmonyText.value = resultStr.split('。')[1] || resultStr
      harmonyResultVisible.value = true
      if (harmonyScore.value >= 70) changeMascotState('happy', 5000)
      else if (harmonyScore.value < 50) changeMascotState('warning', 5000)
    }
  } catch (e) { ElMessage.error('搭配分析失败，请稍后重试') } 
  finally { checking.value = false }
}

const harmonyColor = computed(() => {
  if (harmonyScore.value >= 75) return 'var(--success-color)'
  if (harmonyScore.value >= 50) return 'var(--warning-color)'
  return 'var(--danger-color)'
})
</script>

<style scoped>
/* 原有基础布局样式 */
.nexus-dashboard { padding: 5vh 40px; min-height: 100vh; box-sizing: border-box; }
.glass-container { max-width: 1400px; margin: 0 auto; }
.glass-header { display: flex; justify-content: space-between; align-items: center; background: var(--glass-bg); backdrop-filter: blur(30px) saturate(120%); border: 1px solid var(--glass-border); border-radius: var(--sharp-radius); padding: 24px 40px; margin-bottom: 32px; box-shadow: var(--glass-shadow); }
.brand-title { margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px; color: var(--primary-color); }
.brand-badge { font-size: 12px; background: var(--accent-color); color: white; padding: 4px 10px; border-radius: 6px; vertical-align: middle; margin-left: 10px; font-weight: 600; }
.brand-subtitle { font-size: 14px; color: #8D7B68; font-weight: 500; margin-top: 6px; display: block; }

.workspace-grid { display: grid; grid-template-columns: 1fr 360px; gap: 32px; align-items: start; }
.sidebar-grid { display: grid; gap: 32px; }
.glass-panel { background: var(--glass-bg); backdrop-filter: blur(30px) saturate(120%); border: 1px solid var(--glass-border); border-radius: var(--sharp-radius); padding: 32px; box-shadow: var(--glass-shadow); }
.panel-header { display: flex; align-items: center; margin-bottom: 28px; }
.panel-header.compact { margin-bottom: 20px; }
.title-icon { width: 40px; height: 40px; border-radius: 12px; background: rgba(255, 255, 255, 0.6); color: var(--primary-color); display: flex; align-items: center; justify-content: center; margin-right: 16px; border: 1px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.02); }
.title-icon.magic { color: var(--accent-color); }
.panel-title { margin: 0; font-size: 20px; font-weight: 700; color: var(--primary-color); }
.material-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
.echarts-container { width: 100%; height: 260px; } /* 稍微加高一点给标签留空间 */
.magic-core { display: flex; flex-direction: column; gap: 16px; }
.result-display { text-align: center; padding-top: 24px; }
.score-display { font-size: 72px; font-weight: 800; line-height: 1; letter-spacing: -2px; }
.score-unit { font-size: 20px; margin-left: 6px; font-weight: 600; }
.harmony-comment { margin-top: 16px; font-size: 14px; font-weight: 500; color: #5D4037; background: rgba(255,255,255,0.6); padding: 16px; border-radius: var(--card-radius); line-height: 1.5; }

/* 你的原版奶龙样式，一字未改 */
.fixed-mascot {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 190px;
  height: 190px;
  z-index: 9999;
  cursor: pointer;
  transition: transform 0.3s;
}
.fixed-mascot:hover { transform: scale(1.05); }
.fixed-mascot .mascot { 
  width: 100%; 
  height: 100%; 
  object-fit: contain; 
  filter: drop-shadow(0 15px 20px rgba(93, 64, 55, 0.15)); 
}
.float-anim { animation: smooth-float 4s ease-in-out infinite; }
@keyframes smooth-float { 
  0%, 100% { transform: translateY(0); } 
  50% { transform: translateY(-10px); } 
}

/* ================== 以下为新增的高级优化 CSS ================== */

/* 1. 按钮优化：Premium 风格 */
.action-btn-premium {
  position: relative; border: none; padding: 12px 28px; border-radius: 14px;
  font-size: 15px; font-weight: 700; color: white; cursor: pointer;
  display: flex; align-items: center; gap: 10px; overflow: hidden;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 8px 20px rgba(93, 64, 55, 0.15);
}
.action-btn-premium.primary { background: linear-gradient(135deg, #5D4037 0%, #3E2723 100%); }
.action-btn-premium.magic { background: linear-gradient(135deg, #FF8FAB 0%, #E07A5F 100%); width: 100%; justify-content: center; margin-top: 8px;}
.action-btn-premium:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 15px 30px rgba(93, 64, 55, 0.25); }
.action-btn-premium:active { transform: translateY(0) scale(0.98); }
.btn-glow { position: absolute; inset: 0; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); transform: translateX(-100%); transition: 0.6s; }
.action-btn-premium:hover .btn-glow { transform: translateX(100%); }

/* 2. 弹窗深度大改：左右结构高级布局 */
:deep(.premium-dialog) { 
  background: transparent !important; box-shadow: none !important; border: none !important; margin-top: 15vh !important;
}
.p-dialog-content {
  display: flex; background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(40px);
  border-radius: 24px; overflow: hidden; border: 1px solid rgba(255,255,255,0.8);
  box-shadow: 0 40px 100px rgba(0,0,0,0.1);
}
.p-dialog-side {
  width: 200px; background: linear-gradient(180deg, rgba(93,64,55,0.05) 0%, transparent 100%);
  padding: 40px 30px; border-right: 1px solid rgba(0,0,0,0.03);
}
.side-icon { 
  width: 60px; height: 60px; border-radius: 18px; background: white; 
  display: flex; align-items: center; justify-content: center; color: #FF8FAB;
  box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 24px;
}
.p-dialog-side h3 { font-size: 20px; color: #5D4037; margin-bottom: 12px; margin-top: 0; }
.p-dialog-side p { font-size: 13px; color: #8D7B68; line-height: 1.6; margin: 0; }
.p-dialog-main { flex: 1; padding: 40px; }
.form-split { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.p-dialog-footer { display: flex; justify-content: flex-end; align-items: center; gap: 20px; margin-top: 30px; }
.btn-flat { background: transparent; border: none; color: #8D7B68; font-weight: 600; cursor: pointer; padding: 10px 20px; transition: color 0.3s; }
.btn-flat:hover { color: var(--danger-color); }
:deep(.el-form-item__label) { font-weight: 600; color: #5D4037; padding-bottom: 8px !important; }
</style>