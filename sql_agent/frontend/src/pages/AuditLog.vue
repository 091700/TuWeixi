<template>
  <div class="page">
    <header class="page-topbar">
      <div class="flex items-center gap-3">
        <button class="btn btn-ghost btn-sm" @click="$router.push('/')">← 返回</button>
        <span class="page-title">操作审计</span>
      </div>
    </header>
    <div class="page-body">
      <div class="card" style="margin-bottom:12px">
        <div class="card-body" style="padding:12px">
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <input v-model="filterAction" placeholder="操作筛选" class="input input-sm" style="width:140px" @input="search" />
            <input v-model="filterDate" type="date" class="input input-sm" style="width:150px" @change="search" />
            <button class="btn btn-sm" @click="search">搜索</button>
            <button class="btn btn-sm btn-ghost" @click="exportCsv">导出 CSV</button>
          </div>
        </div>
      </div>
      <div class="card">
        <el-table :data="logs" size="small" max-height="calc(100vh - 200px)" style="width:100%">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户" width="100" />
          <el-table-column prop="action" label="操作" width="120" />
          <el-table-column prop="target" label="目标" min-width="140" show-overflow-tooltip />
          <el-table-column prop="result" label="结果" width="80"><template #default="{row}"><span :style="{color:row.result==='SUCCESS'?'var(--success)':'var(--error)'}">{{ row.result==='SUCCESS'?'成功':'失败' }}</span></template></el-table-column>
          <el-table-column prop="created_at" label="时间" width="160" />
        </el-table>
        <div style="padding:10px;display:flex;justify-content:flex-end;border-top:1px solid var(--border)"><el-pagination v-model:current-page="page" :page-size="limit" :total="total" layout="prev,next" small @current-change="search" /></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuth } from '../store/auth.js'
import { API_BASE } from '../config.js'
const router = useRouter(); const auth = useAuth()
function authHeaders() { return auth.getAuthHeaders() }
const logs = ref([]); const total = ref(0); const page = ref(1); const limit = 50
const filterAction = ref(''); const filterDate = ref('')
async function search() { try { const params = { limit, offset: (page.value - 1) * limit }; if (filterAction.value) params.action = filterAction.value; if (filterDate.value) { params.start_date = filterDate.value; params.end_date = filterDate.value }; const r = await axios.get(`${API_BASE}/audit/logs`, { params, headers: authHeaders() }); logs.value = r.data.logs || []; total.value = r.data.total || 0 } catch {} }
async function exportCsv() { try { const r = await axios.get(`${API_BASE}/audit/export`, { params: { start_date: filterDate.value || undefined, end_date: filterDate.value || undefined, action: filterAction.value || undefined }, headers: authHeaders(), responseType: 'blob' }); const a = document.createElement('a'); a.href = URL.createObjectURL(r.data); a.download = 'audit.csv'; a.click() } catch {} }
onMounted(search)
</script>
<style scoped>.page{display:flex;flex-direction:column;height:100vh;background:var(--bg-primary)}.page-topbar{display:flex;align-items:center;height:40px;padding:0 14px;background:var(--bg-secondary);border-bottom:1px solid var(--border);flex-shrink:0}.page-title{font-size:13px;font-weight:600;color:var(--text-primary)}.page-body{flex:1;overflow-y:auto;padding:14px}</style>