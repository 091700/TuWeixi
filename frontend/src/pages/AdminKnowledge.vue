<template>
  <div class="page">
    <header class="page-topbar">
      <div class="flex items-center gap-3">
        <button class="btn btn-ghost btn-sm" @click="$router.push('/')">← 返回</button>
        <span class="page-title">知识库管理</span>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-primary btn-sm" @click="showAdd=true">+ 添加知识</button>
        <button class="btn btn-sm" @click="loadKnowledge">刷新</button>
      </div>
    </header>
    <div class="page-body">
      <div class="card">
        <el-table :data="items" size="small" max-height="calc(100vh - 160px)" style="width:100%">
          <el-table-column prop="id" label="ID" width="180" show-overflow-tooltip />
          <el-table-column label="标题" min-width="160"><template #default="{row}">{{ (row.metadata||{}).title||'未命名' }}</template></el-table-column>
          <el-table-column label="分类" width="120"><template #default="{row}">{{ (row.metadata||{}).category||'通用' }}</template></el-table-column>
          <el-table-column label="内容" min-width="300" show-overflow-tooltip><template #default="{row}">{{ (row.document||'').slice(0,120) }}...</template></el-table-column>
          <el-table-column label="操作" width="80"><template #default="{row}"><el-button size="small" type="danger" text @click="doDelete(row.id)">删除</el-button></template></el-table-column>
        </el-table>
        <div v-if="!items.length" style="padding:40px;text-align:center;color:var(--text-muted);font-size:13px">暂无知识条目</div>
      </div>
    </div>
    <el-dialog v-model="showAdd" title="添加知识" width="560px">
      <div class="field"><label>内容</label><textarea v-model="newItem.content" class="input" rows="6" placeholder="知识内容" style="resize:vertical"></textarea></div>
      <div class="field" style="margin-top:10px"><label>标题</label><input v-model="newItem.title" class="input" placeholder="标题" /></div>
      <div class="field" style="margin-top:10px"><label>分类</label><input v-model="newItem.category" class="input" placeholder="分类" /></div>
      <el-button type="primary" @click="doAdd" :disabled="!newItem.content" class="w-full" style="margin-top:14px">添加</el-button>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import { useRouter } from 'vue-router'; import axios from 'axios'; import { ElMessage, ElMessageBox } from 'element-plus'; import { useAuth } from '../store/auth.js'; import { API_BASE } from '../config.js'
const router = useRouter(); const auth = useAuth(); function authHeaders() { return auth.getAuthHeaders() }
const items = ref([]); const showAdd = ref(false); const newItem = ref({ content:'', title:'', category:'通用' })
async function loadKnowledge() { try { const r = await axios.get(`${API_BASE}/knowledge/list`, { headers: authHeaders() }); items.value = r.data.items || [] } catch {} }
async function doAdd() { try { await axios.post(`${API_BASE}/knowledge/add`, { content:newItem.value.content, metadata:{ title:newItem.value.title||'未命名', category:newItem.value.category||'通用' } }, { headers: authHeaders() }); showAdd.value=false; loadKnowledge(); ElMessage.success('已添加') } catch(e){ ElMessage.error('添加失败') } }
async function doDelete(id) { try { await ElMessageBox.confirm('删除该知识条目？','确认',{type:'warning'}); await axios.delete(`${API_BASE}/knowledge/${id}`, { headers: authHeaders() }); loadKnowledge(); ElMessage.success('已删除') } catch {} }
onMounted(loadKnowledge)
</script>
<style scoped>.page{display:flex;flex-direction:column;height:100vh;background:var(--bg-primary)}.page-topbar{display:flex;align-items:center;justify-content:space-between;height:40px;padding:0 14px;background:var(--bg-secondary);border-bottom:1px solid var(--border);flex-shrink:0}.page-title{font-size:13px;font-weight:600;color:var(--text-primary)}.page-body{flex:1;overflow-y:auto;padding:14px}.field{display:flex;flex-direction:column;gap:4px}.field label{font-size:11px;font-weight:600;color:var(--text-secondary)}.w-full{width:100%}</style>