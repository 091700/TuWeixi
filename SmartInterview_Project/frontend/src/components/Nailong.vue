<template>
  <div class="fixed-mascot" :class="mascotEffectClass" v-show="false">
    <img v-if="mascotState === 'idle'" src="/nailong.png" class="mascot float-anim" alt="待机" />
    <video v-else-if="mascotState === 'happy'" src="/nailongdaxiao.webm" class="mascot" autoplay loop muted></video>
    <video v-else-if="mascotState === 'warning'" src="/nailonghuishou.webm" class="mascot" autoplay loop muted></video>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const mascotState = ref('idle')
let mascotTimer = null

const changeMascotState = (state, duration = 4000) => {
  mascotState.value = state
  if (mascotTimer) clearTimeout(mascotTimer)
  mascotTimer = setTimeout(() => {
    mascotState.value = 'idle'
  }, duration)
}

const mascotEffectClass = computed(() => {
  if (mascotState.value === 'warning') return 'mascot-danger';
  if (mascotState.value === 'happy') return 'mascot-glow';
  return '';
});

// 对外暴露方法，供父组件调用
const updateMascotByScore = (score) => {
  if (score >= 80) {
    changeMascotState('happy', 5000) 
  } else {
    changeMascotState('warning', 5000) 
  }
}

defineExpose({
  changeMascotState,
  updateMascotByScore
})
</script>

<style scoped>
.fixed-mascot {
display: none !important;
  position: fixed;
  bottom: 100px;
  right: 10px;
  width: 180px;
  height: 180px;
  z-index: 9999;
  pointer-events: none; 
  transition: transform 0.3s;
}

.fixed-mascot .mascot {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 15px 20px rgba(93, 64, 55, 0.15));
}

.mascot-danger .mascot {
  filter: grayscale(40%) drop-shadow(0 15px 20px rgba(204, 79, 79, 0.4)) !important;
  animation: shake 0.5s infinite;
}

.mascot-glow .mascot {
  transform: scale(1.15);
  filter: drop-shadow(0 0 25px rgba(255, 155, 133, 0.8)) !important;
  transition: all 0.5s ease;
}

@keyframes shake {
  0% { transform: translate(1px, 1px) rotate(0deg); }
  10% { transform: translate(-1px, -2px) rotate(-1deg); }
  20% { transform: translate(-3px, 0px) rotate(1deg); }
  30% { transform: translate(3px, 2px) rotate(0deg); }
  40% { transform: translate(1px, -1px) rotate(1deg); }
  50% { transform: translate(-1px, 2px) rotate(-1deg); }
  60% { transform: translate(-3px, 1px) rotate(0deg); }
  70% { transform: translate(3px, 1px) rotate(-1deg); }
  80% { transform: translate(-1px, -1px) rotate(1deg); }
  90% { transform: translate(1px, 2px) rotate(0deg); }
  100% { transform: translate(1px, -2px) rotate(-1deg); }
}

.float-anim {
  animation: smooth-float 4s ease-in-out infinite;
}

@keyframes smooth-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
</style>