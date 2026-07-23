<template>
  <div class="page">
    <header class="page-topbar">
      <div class="flex items-center gap-3">
        <button class="btn btn-ghost btn-sm" @click="$router.push('/')">← 返回</button>
        <span class="page-title">备份管理</span>
      </div>
      <button class="btn btn-sm" @click="load" :loading="loading">刷新</button>
    </header>
    <div class="page-body">
      <div class="card">
        <el-table :data="backups" size="small" max-height="calc(100vh - 160px)" style="width:100%" v-loading="loading">
          <el-table-column prop="filename" label="文件名" min-width="260" show-overflow-tooltip />
          <el-table-column prop="operation" label="操作" width="120" />
          <el-table-column prop="database" label="数据库" width="100" />
          <el-table-column prop="target" label="目标" width="100" />
          <el-table-column prop="username" label="用户" width="90" />
          <el-table-column label="大小" width="80"><template #default="{row}">{{ (row.size_bytes/1024).toFixed(1) }} KB</template></el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160" />
          <el-table-column label="操作" width="80" fixed="right"><template #default="{row}"><el-button size="small" type="danger" text @click="doRestore(row)">恢复</el-button></template></el-table-column>
        </el-table>
        <div v-if="!loading&&!backups.length" style="padding:40px;text-align:center;color:var(--text-muted);font-size:13px">暂无备份文件</div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import { useRouter } from 'vue-router'; import axios from 'axios'; import { ElMessage, ElMessageBox } from 'element-plus'; import { useAuth } from '../store/auth.js'; import { API_BASE } from '../config.js'
const router = useRouter(); const auth = useAuth(); function authHeaders() { return auth.getAuthHeaders() }
const backups = ref([]); const loading = ref(false)
async function load() { loading.value = true; try { const r = await axios.get(`${API_BASE}/admin/backups`, { headers: authHeaders() }); backups.value = r.data.backups || [] } catch {}; loading.value = false }
async function doRestore(row) { try { await ElMessageBox.confirm(`从 ${row.filename} 恢复？`, '确认', { type: 'warning' }); const db = prompt('目标数据库 (默认: 原始):', row.database); const r = await axios.post(`${API_BASE}/admin/backups/restore`, { filename: row.filename, target_database: db || undefined }, { headers: authHeaders() }); ElMessage.success(r.data.message||'已恢复') } catch {} }
onMounted(load)
</script>
<style scoped>.page{display:flex;flex-direction:column;height:100vh;background:var(--bg-primary)}.page-topbar{display:flex;align-items:center;justify-content:space-between;height:40px;padding:0 14px;background:var(--bg-secondary);border-bottom:1px solid var(--border);flex-shrink:0}.page-title{font-size:13px;font-weight:600;color:var(--text-primary)}.page-body{flex:1;overflow-y:auto;padding:14px}</style>