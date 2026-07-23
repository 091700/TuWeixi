<template>
  <div class="page">
    <header class="page-topbar">
      <div class="flex items-center gap-3">
        <button class="btn btn-ghost btn-sm" @click="$router.push('/')">← 返回</button>
        <span class="page-title">收藏会话</span>
      </div>
    </header>
    <div class="page-body">
      <div class="card">
        <div v-if="favs.length" style="display:flex;flex-direction:column">
          <div v-for="f in favs" :key="f.id" class="fav-row" @click="openSession(f.id)">
            <div class="fav-info">
              <span class="fav-preview">{{ f.preview }}</span>
              <span class="fav-time">{{ formatTime(f.time) }}</span>
            </div>
            <button class="btn btn-sm btn-danger" @click.stop="removeFav(f.id)">移除</button>
          </div>
        </div>
        <div v-else style="padding:40px;text-align:center;color:var(--text-muted);font-size:13px">暂无收藏会话</div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import { useRouter } from 'vue-router'; import { STORAGE_KEYS } from '../config.js'
const router = useRouter(); const favs = ref([])
function loadFavs(){try{const r=localStorage.getItem(STORAGE_KEYS.favorites);favs.value=r?JSON.parse(r):[]}catch{favs.value=[]}}
function removeFav(id){favs.value=favs.value.filter(f=>f.id!==id);localStorage.setItem(STORAGE_KEYS.favorites,JSON.stringify(favs.value))}
function openSession(id){localStorage.setItem(STORAGE_KEYS.pendingRestore,id);router.push('/')}
function formatTime(ts){if(!ts)return'';const d=new Date(ts);return `${d.getMonth()+1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2,'0')}`}
onMounted(loadFavs)
</script>
<style scoped>.page{display:flex;flex-direction:column;height:100vh;background:var(--bg-primary)}.page-topbar{display:flex;align-items:center;height:40px;padding:0 14px;background:var(--bg-secondary);border-bottom:1px solid var(--border);flex-shrink:0}.page-title{font-size:13px;font-weight:600;color:var(--text-primary)}.page-body{flex:1;overflow-y:auto;padding:14px}.fav-row{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .1s}.fav-row:hover{background:var(--bg-hover)}.fav-info{display:flex;flex-direction:column;gap:2px}.fav-preview{font-size:13px;color:var(--text-primary);font-weight:500}.fav-time{font-size:11px;color:var(--text-muted)}</style>