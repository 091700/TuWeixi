<template>
  <div :class="['material-card', levelClass]">
    <div class="glow-backdrop"></div>
    <div class="card-content">
      <div class="header-row">
        <h3 class="item-name">{{ name }}</h3>
        <div class="status-indicator"></div>
      </div>
      
      <div class="meta-group">
        <div class="meta-row">
          <span class="label">收录纪元</span>
          <span class="value">{{ item.entryDate }}</span>
        </div>
        <div class="meta-row highlight">
          <span class="label">临界奇点</span>
          <span class="value">{{ item.predictedExpireDate }}</span>
        </div>
      </div>
      
      <div class="footer-row">
        <div class="countdown">{{ daysLeftText }}</div>
        <div class="actions">
          <button class="btn-icon eat" @click="$emit('consume', item.id)" title="提取能量">
            <Utensils :size="16" stroke-width="2.5" />
          </button>
          <button class="btn-icon trash" @click="$emit('discard', item.id)" title="销毁物质">
            <Trash2 :size="16" stroke-width="2.5" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Utensils, Trash2 } from 'lucide-vue-next'

const props = defineProps({ item: Object, name: String })
defineEmits(['consume', 'discard'])

const diffDays = computed(() => {
  if (!props.item.predictedExpireDate) return null
  return Math.ceil((new Date(props.item.predictedExpireDate) - new Date()) / (1000 * 60 * 60 * 24))
})

const daysLeftText = computed(() => {
  if (diffDays.value === null) return '演算中...'
  if (diffDays.value < 0) return `已衰败 ${Math.abs(diffDays.value)} 天`
  if (diffDays.value === 0) return '即将过期'
  return `剩余 ${diffDays.value} 天`
})

const levelClass = computed(() => {
  if (diffDays.value < 0) return 'danger'
  if (diffDays.value <= 2) return 'warning'
  return 'safe'
})
</script>

<style scoped>
.material-card {
  position: relative;
  background: var(--glass-bg);
  backdrop-filter: blur(24px) saturate(120%);
  border: 1px solid var(--glass-border);
  border-radius: var(--sharp-radius);
  /* 【调整】缩减内边距，使卡片更扁平 */
  padding: 16px 20px; 
  transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
  box-shadow: var(--glass-shadow);
  z-index: 1;
  overflow: hidden;
}

.material-card:hover { 
  transform: translateY(-4px) scale(1.01); 
  box-shadow: 0 15px 30px rgba(93, 64, 55, 0.1); 
}

/* 柔和的底部弥散光源 */
.glow-backdrop { 
  position: absolute; inset: 0; z-index: -1; 
  opacity: 0; 
}

/* 【修复】临期（黄色）和过期（红色）都加入呼吸动画 */
.warning .glow-backdrop {
  /* 颜色调深，向橙红靠拢 */
  background: radial-gradient(circle at center bottom, rgba(242, 160, 80, 0.6) 0%, transparent 75%);
  animation: soft-breathe 2.5s infinite alternate ease-in-out;
}

.danger .glow-backdrop {
  /* 显著调红，增加不透明度 */
  background: radial-gradient(circle at center bottom, rgba(224, 60, 50, 0.7) 0%, transparent 75%);
  animation: soft-breathe 1.8s infinite alternate ease-in-out;
}

@keyframes soft-breathe {
  0% { 
    opacity: 0.5; 
    transform: scale(0.9) translateY(15px); 
    filter: blur(5px);
  }
  100% { 
    opacity: 1; 
    transform: scale(1.15) translateY(0); 
    filter: blur(2px);
  }
}

.card-content { position: relative; z-index: 2; display: flex; flex-direction: column; gap: 12px; }
.header-row { display: flex; justify-content: space-between; align-items: center; }
.item-name { margin: 0; font-size: 16px; font-weight: 700; color: var(--primary-color); letter-spacing: -0.3px; }
.status-indicator { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 10px currentColor; }

.safe .status-indicator { color: var(--success-color); background: var(--success-color); }
.warning .status-indicator { color: var(--warning-color); background: var(--warning-color); }
.danger .status-indicator { color: var(--danger-color); background: var(--danger-color); }

.meta-group { display: flex; flex-direction: column; gap: 6px; }
.meta-row { display: flex; justify-content: space-between; font-size: 12px; color: #8D7B68; }
.meta-row.highlight { color: var(--danger-color); font-weight: 600; background: rgba(255, 255, 255, 0.5); padding: 4px 8px; border-radius: 6px; margin: 0 -8px; }

/* 【调整】将倒计时和按钮放在同一行，节省垂直空间 */
.footer-row { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; }
.countdown { font-size: 16px; font-weight: 800; color: var(--primary-color); }
.actions { display: flex; gap: 8px; }
.btn-icon { 
  padding: 8px 12px; border-radius: 8px; 
  border: 1px solid rgba(255,255,255,0.8); background: rgba(255,255,255,0.4); 
  color: #8D7B68; display: flex; align-items: center; justify-content: center; 
  cursor: pointer; transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1); 
}
.btn-icon:hover { background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.btn-icon.eat:hover { color: var(--success-color); border-color: var(--success-color); }
.btn-icon.trash:hover { color: var(--danger-color); border-color: var(--danger-color); }
</style>