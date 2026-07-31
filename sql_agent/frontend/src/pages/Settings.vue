<template>
  <div class="page">
    <canvas ref="bgCanvas" class="bg-canvas"></canvas>
    <header class="page-topbar">
      <div class="flex items-center gap-3">
        <button class="btn btn-ghost btn-sm" @click="$router.push('/')">← 返回</button>
        <span class="page-title">设置</span>
      </div>
    </header>
    <div class="page-body">
      <div class="settings-container">
        <div class="card" style="margin-bottom:14px"><div class="card-header">外观</div><div class="card-body"><div class="setting-row"><div><div class="setting-label">暗色模式</div><div class="setting-desc">切换深色/浅色主题</div></div><div class="toggle-track" :class="{on:darkMode}" @click="toggleDarkMode"><div class="toggle-knob"></div></div></div></div></div>
        <div class="card" style="margin-bottom:14px"><div class="card-header">AI 模型</div><div class="card-body"><div class="setting-row"><div><div class="setting-label">当前模型</div><div class="setting-desc">选择用于对话的 LLM 模型</div></div><el-select v-model="selectedModel" size="small" style="width:180px"><el-option v-for="m in models" :key="m.value" :label="m.label" :value="m.value" /></el-select></div></div></div>
        <div class="card" style="margin-bottom:14px"><div class="card-header">查询设置</div><div class="card-body"><div class="setting-row"><div><div class="setting-label">结果行数上限</div><div class="setting-desc">单次查询最多返回的行数</div></div><el-input-number v-model="resultLimit" :min="10" :max="500" :step="50" size="small" style="width:120px" /></div></div></div>
        <div class="card" style="margin-bottom:14px"><div class="card-header">数据管理</div><div class="card-body"><div class="setting-row"><div><div class="setting-label">重建知识库</div><div class="setting-desc">清除并重新初始化 ChromaDB 知识库</div></div><button class="btn btn-sm" @click="initKnowledge">重建</button></div><div class="setting-row" style="border-bottom:none;padding-bottom:0"><div><div class="setting-label">清除所有会话</div><div class="setting-desc">删除所有本地会话历史记录</div></div><button class="btn btn-sm btn-danger" @click="clearAllSessions">清除</button></div></div></div>
        <div class="card" style="margin-bottom:14px"><div class="card-header">系统监控</div><div class="card-body"><div class="setting-row" style="border-bottom:none;padding-bottom:0"><div><div class="setting-label">React 仪表盘</div><div class="setting-desc">查看系统性能指标、查询统计和健康度监控</div></div><a class="btn btn-sm" href="/dashboard.html" target="_blank" style="text-decoration:none;color:var(--text-primary)">📊 打开</a></div></div></div>
        <div class="card"><div class="card-header">关于</div><div class="card-body"><div class="setting-row" style="border-bottom:none;padding-bottom:0"><div><div class="setting-label">数据库 AI 助手</div><div class="setting-desc"> --- </div></div></div></div></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuth } from '../store/auth.js'
import { API_BASE } from '../config.js'
const router = useRouter(); const auth = useAuth()
function authHeaders() { return auth.getAuthHeaders() }

const darkMode = ref(localStorage.getItem('db_agent_theme') !== 'light')
const selectedModel = ref(localStorage.getItem('db_agent_model') || 'deepseek-chat')
const models = [{ value: 'deepseek-chat', label: 'DeepSeek V3' },{ value: 'deepseek-reasoner', label: 'DeepSeek R1' }]
const resultLimit = ref(100)
watch(selectedModel, (v) => localStorage.setItem('db_agent_model', v))

function applyTheme() { const h = document.querySelector('html'); if (!h) return; if (darkMode.value) { h.classList.remove('light-theme'); localStorage.setItem('db_agent_theme', 'dark') } else { h.classList.add('light-theme'); localStorage.setItem('db_agent_theme', 'light') } }
function toggleDarkMode() { darkMode.value = !darkMode.value; applyTheme() }

// ═══════════ Canvas: same as Chat.vue ═══════════
const bgCanvas = ref(null); let anim = null, effTimer = null
let effIdx = 0, effTT = 0, drops = [], petals = [], motes = [], sunAngle = 0

function applyStoredTheme(){const t=localStorage.getItem('db_agent_theme');const html=document.querySelector('html');if(!html)return;if(t==='light')html.classList.add('light-theme');else html.classList.remove('light-theme')}
onMounted(()=>{applyStoredTheme();initBg()})
onUnmounted(()=>{if(anim)cancelAnimationFrame(anim);if(effTimer)clearTimeout(effTimer)})

function initBg(){
  const c=bgCanvas.value;if(!c)return;const ctx=c.getContext('2d');let w=0,h=0;const stars=[],meteors=[]
  function rs(){w=c.width=c.offsetWidth;h=c.height=c.offsetHeight}rs();window.addEventListener('resize',rs)
  for(let i=0;i<180;i++)stars.push({x:Math.random()*1920,y:Math.random()*1080,r:Math.random()*1.6+0.2,s:Math.random()*0.015+0.003,p:Math.random()*Math.PI*2,b:Math.random()*0.35+0.2})
  function sm(){meteors.push({x:Math.random()*w*0.8+w*0.1,y:Math.random()*h*0.3,l:Math.random()*80+40,v:Math.random()*5+3,life:1,d:Math.random()*0.01+0.004})}
  for(let i=0;i<120;i++)drops.push({x:Math.random()*w,y:Math.random()*h,l:Math.random()*22+10,spd:Math.random()*6+4,op:Math.random()*0.5+0.3})
  for(let i=0;i<40;i++)petals.push({x:Math.random()*w,y:Math.random()*h,z:Math.random()*12+8,vx:Math.random()*0.55+0.25,vy:Math.random()*0.25+0.08,wb:Math.random()*Math.PI*2,ws:Math.random()*0.02+0.01,rt:Math.random()*Math.PI*2,rs:Math.random()*0.03-0.015,op:Math.random()*0.5+0.35,h:Math.random()*40+340})
  for(let i=0;i<70;i++)motes.push({x:Math.random()*w*0.3,y:Math.random()*h*0.3,r:Math.random()*4+1.2,op:Math.random()*0.55+0.3,vx:Math.random()*0.12-0.06,vy:-Math.random()*0.2-0.04})
  function drawPetal(px,py,z,rt,op,h){ctx.save();ctx.translate(px,py);ctx.rotate(rt);ctx.beginPath();ctx.moveTo(0,-z);ctx.bezierCurveTo(z*0.55,-z*0.7,z*0.55,z*0.35,0,z*0.85);ctx.bezierCurveTo(-z*0.55,z*0.35,-z*0.55,-z*0.7,0,-z);ctx.fillStyle=`hsla(${h},75%,72%,${op})`;ctx.fill();ctx.restore()}
  function rotateEffect(){const html=document.querySelector('html');if(!html||!html.classList.contains('light-theme')){effTimer=setTimeout(rotateEffect,5000);return};effIdx=(effIdx+1)%3;effTT=0;effTimer=setTimeout(rotateEffect,15000+Math.random()*15000)}
  function draw(){ctx.clearRect(0,0,w,h);const lt=document.querySelector('html')?.classList.contains('light-theme')
    if(!lt){const n=Date.now()*0.001;for(const s of stars){const a=s.b+Math.sin(n*s.s*60+s.p)*0.25;ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fillStyle=`rgba(255,255,255,${Math.max(0.06,a)})`;ctx.fill()}for(let i=meteors.length-1;i>=0;i--){const m=meteors[i];m.x-=m.v;m.y+=m.v*0.5;m.life-=m.d;if(m.life<=0){meteors.splice(i,1);continue};const g=ctx.createLinearGradient(m.x,m.y,m.x+m.l,m.y-m.l*0.5);g.addColorStop(0,`rgba(255,255,255,${m.life*0.7})`);g.addColorStop(1,'rgba(255,255,255,0)');ctx.beginPath();ctx.moveTo(m.x,m.y);ctx.lineTo(m.x+m.l,m.y-m.l*0.5);ctx.strokeStyle=g;ctx.lineWidth=1.3;ctx.stroke()}if(Math.random()<0.004)sm()}
    else{if(effTimer===null)rotateEffect();effTT+=0.014;const f=Math.min(effTT,1)
      if(drops.length<80)for(let i=0;i<3;i++)drops.push({x:Math.random()*w,y:-25,l:Math.random()*22+12,spd:Math.random()*6+4,op:Math.random()*0.5+0.3})
      if(petals.length<30)for(let i=0;i<3;i++)petals.push({x:Math.random()*w,y:-25,z:Math.random()*12+8,vx:Math.random()*0.55+0.25,vy:Math.random()*0.25+0.08,wb:Math.random()*Math.PI*2,ws:Math.random()*0.02+0.01,rt:Math.random()*Math.PI*2,rs:Math.random()*0.03-0.015,op:Math.random()*0.5+0.35,h:Math.random()*40+340})
      if(motes.length<40)for(let i=0;i<3;i++)motes.push({x:Math.random()*w*0.3,y:Math.random()*h*0.3,r:Math.random()*4+1.2,op:Math.random()*0.55+0.3,vx:Math.random()*0.12-0.06,vy:-Math.random()*0.2-0.04})
      if(effIdx===0){for(let i=drops.length-1;i>=0;i--){const d=drops[i];d.y+=d.spd;if(d.y>h+35){drops.splice(i,1);continue};ctx.beginPath();ctx.moveTo(d.x,d.y);ctx.lineTo(d.x-d.spd*0.3,d.y+d.l);ctx.strokeStyle=`rgba(140,180,235,${d.op*f})`;ctx.lineWidth=1.2;ctx.stroke()}}
      else if(effIdx===1){for(let i=petals.length-1;i>=0;i--){const p=petals[i];p.x+=p.vx+Math.sin(Date.now()*0.0015+p.wb)*0.2;p.y+=p.vy;p.rt+=p.rs;p.wb+=p.ws;if(p.y>h+45){petals.splice(i,1);continue};if(p.x<-50)p.x=w+40;if(p.x>w+50)p.x=-40;drawPetal(p.x,p.y,p.z,p.rt,p.op*f,p.h)}}
      else{sunAngle+=0.0004;for(let i=0;i<8;i++){const a=sunAngle+i*0.785+Math.sin(Date.now()*0.0004+i)*0.06;const dx=Math.cos(a),dy=Math.sin(a);const farX=dx*w*0.95,farY=dy*h*0.85;const topW=8*f,botW=200*f;const g=ctx.createLinearGradient(0,0,farX,farY);g.addColorStop(0,'rgba(255,248,195,0.9)');g.addColorStop(0.15,'rgba(255,235,160,0.65)');g.addColorStop(0.5,'rgba(255,215,110,0.18)');g.addColorStop(1,'rgba(255,180,60,0)');ctx.beginPath();ctx.moveTo(dx*topW,dy*topW);ctx.lineTo(farX-dy*botW,farY+dx*botW);ctx.lineTo(farX+dy*botW,farY-dx*botW);ctx.lineTo(-dx*topW,-dy*topW);ctx.fillStyle=g;ctx.fill()}for(let i=motes.length-1;i>=0;i--){const m=motes[i];m.x+=m.vx;m.y+=m.vy;m.op-=0.0005;if(m.y<-40||m.op<=0){motes.splice(i,1);continue};const glow=ctx.createRadialGradient(m.x,m.y,0,m.x,m.y,m.r*4.5);glow.addColorStop(0,'rgba(255,248,190,0.85)');glow.addColorStop(0.2,'rgba(255,230,140,0.55)');glow.addColorStop(0.55,'rgba(255,205,90,0.15)');glow.addColorStop(1,'rgba(255,170,50,0)');ctx.beginPath();ctx.arc(m.x,m.y,m.r,0,Math.PI*2);ctx.fillStyle=glow;ctx.fill()}}}
    anim=requestAnimationFrame(draw)
  }for(let i=0;i<3;i++)sm();draw()
}

async function initKnowledge() { try { await axios.post(`${API_BASE}/knowledge/init?force=true`, {}, { headers: authHeaders() }); ElMessage.success('知识库已重建') } catch { ElMessage.error('重建失败') } }
function clearAllSessions() { ElMessageBox.confirm('确定要清除所有本地会话历史吗？','确认清除',{type:'warning'}).then(()=>{const keys=[];for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k&&(k.startsWith('db_agent_')||k.startsWith('chart_')))keys.push(k)};keys.forEach(k=>localStorage.removeItem(k));ElMessage.success('已清除')}).catch(()=>{}) }
</script>

<style scoped>
.page{display:flex;flex-direction:column;height:100vh;background:var(--bg-primary);position:relative}
.bg-canvas{position:absolute;inset:0;z-index:0;pointer-events:none;width:100%;height:100%}
.page-topbar{position:relative;z-index:1;display:flex;align-items:center;height:40px;padding:0 14px;background:var(--bg-secondary);border-bottom:1px solid var(--border);flex-shrink:0}
.page-title{font-size:13px;font-weight:600;color:var(--text-primary)}
.page-body{position:relative;z-index:1;flex:1;overflow-y:auto;padding:20px}
.settings-container{max-width:640px;margin:0 auto}
.setting-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border)}
.setting-label{font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:2px}
.setting-desc{font-size:11px;color:var(--text-muted)}
</style>