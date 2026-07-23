<template>
  <div class="page">
    <header class="page-topbar">
      <div class="flex items-center gap-3">
        <button class="btn btn-ghost btn-sm" @click="$router.push('/')">← 返回</button>
        <span class="page-title">用户管理</span>
      </div>
      <button class="btn btn-primary btn-sm" @click="showCreate=true">+ 新建用户</button>
    </header>
    <div class="page-body">
      <div class="card">
        <el-table :data="users" size="small" max-height="calc(100vh - 160px)" style="width:100%">
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="display_name" label="显示名" width="140" />
          <el-table-column prop="role" label="角色" width="80" />
          <el-table-column prop="is_active" label="状态" width="80"><template #default="{row}"><span :style="{color:row.is_active?'var(--success)':'var(--error)'}">{{ row.is_active?'正常':'禁用' }}</span></template></el-table-column>
          <el-table-column prop="last_login" label="最后登录" width="160" />
          <el-table-column label="操作" min-width="200"><template #default="{row}"><el-button size="small" text @click="toggleStatus(row.username,!row.is_active)">{{ row.is_active?'禁用':'启用' }}</el-button><el-button size="small" text @click="promptRole(row.username)">改角色</el-button><el-button size="small" text @click="promptPassword(row.username)">重置密码</el-button></template></el-table-column>
        </el-table>
      </div>
    </div>
    <el-dialog v-model="showCreate" title="新建用户" width="400px">
      <div class="field"><label>用户名</label><input v-model="newUser.username" class="input" placeholder="用户名" /></div>
      <div class="field" style="margin-top:10px"><label>密码</label><input v-model="newUser.password" type="password" class="input" placeholder="至少6位" /></div>
      <div class="field" style="margin-top:10px"><label>角色</label><el-select v-model="newUser.role" size="small" class="w-full"><el-option label="admin" value="admin" /><el-option label="reader" value="reader" /></el-select></div>
      <div class="field" style="margin-top:10px"><label>显示名</label><input v-model="newUser.display" class="input" placeholder="可选" /></div>
      <el-button type="primary" @click="doCreate" :disabled="!newUser.username||!newUser.password" class="w-full" style="margin-top:14px">创建</el-button>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import { useRouter } from 'vue-router'; import axios from 'axios'; import { ElMessage, ElMessageBox } from 'element-plus'; import { useAuth } from '../store/auth.js'; import { API_BASE } from '../config.js'
const router = useRouter(); const auth = useAuth(); function authHeaders() { return auth.getAuthHeaders() }
const users = ref([]); const showCreate = ref(false); const newUser = ref({ username:'', password:'', role:'reader', display:'' })
async function loadUsers(){ try { const r = await axios.get(`${API_BASE}/admin/users`, { headers: authHeaders() }); users.value = r.data.users || [] } catch {} }
async function toggleStatus(username, is_active){ try { await axios.post(`${API_BASE}/admin/users/status`, { username, is_active }, { headers: authHeaders() }); loadUsers(); ElMessage.success(is_active?'已启用':'已禁用') } catch(e){ ElMessage.error(e.response?.data?.detail||'操作失败') } }
async function promptRole(username){ try { const { value } = await ElMessageBox.prompt('新角色 (admin/reader)', '修改角色', { inputValue:'reader' }); if(value&&(value==='admin'||value==='reader')){ await axios.post(`${API_BASE}/admin/users/role`, { username, role:value }, { headers: authHeaders() }); loadUsers(); ElMessage.success('已更新') } } catch {} }
async function promptPassword(username){ try { const { value } = await ElMessageBox.prompt('新密码 (至少6位)', '重置密码'); if(value&&value.length>=6){ await axios.post(`${API_BASE}/admin/users/password`, { username, new_password:value }, { headers: authHeaders() }); ElMessage.success('已重置') } } catch {} }
async function doCreate(){ try { await axios.post(`${API_BASE}/admin/users/create`, { username:newUser.value.username, password:newUser.value.password, role:newUser.value.role, display_name:newUser.value.display }, { headers: authHeaders() }); loadUsers(); showCreate.value=false; ElMessage.success('已创建') } catch(e){ ElMessage.error(e.response?.data?.detail||'创建失败') } }
onMounted(loadUsers)
</script>
<style scoped>.page{display:flex;flex-direction:column;height:100vh;background:var(--bg-primary)}.page-topbar{display:flex;align-items:center;justify-content:space-between;height:40px;padding:0 14px;background:var(--bg-secondary);border-bottom:1px solid var(--border);flex-shrink:0}.page-title{font-size:13px;font-weight:600;color:var(--text-primary)}.page-body{flex:1;overflow-y:auto;padding:14px}.field{display:flex;flex-direction:column;gap:4px}.field label{font-size:11px;font-weight:600;color:var(--text-secondary)}.w-full{width:100%}</style>