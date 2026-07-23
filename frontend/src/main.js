import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import axios from 'axios'
import './style.css'
import App from './App.vue'
import Login from './pages/Login.vue'
import AuditLog from './pages/AuditLog.vue'
import Chat from './pages/Chat.vue'
import Favorites from './pages/Favorites.vue'
import Settings from './pages/Settings.vue'
import AdminUsers from './pages/AdminUsers.vue'
import AdminBackups from './pages/AdminBackups.vue'
import AdminKnowledge from './pages/AdminKnowledge.vue'
import { useAuth } from './store/auth.js'

// 路由配置
const routes = [
  { path: '/login', component: Login, meta: { noAuth: true } },
  { path: '/audit', component: AuditLog, meta: { requiresAuth: true } },
  { path: '/favorites', component: Favorites, meta: { requiresAuth: true } },
  { path: '/settings', component: Settings, meta: { requiresAuth: true } },
  { path: '/admin/users', component: AdminUsers, meta: { requiresAuth: true } },
  { path: '/admin/backups', component: AdminBackups, meta: { requiresAuth: true } },
  { path: '/admin/knowledge', component: AdminKnowledge, meta: { requiresAuth: true } },
  { path: '/', component: Chat, meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const auth = useAuth()

  if (to.meta.noAuth) {
    // 已登录用户访问登录页，跳转到首页
    if (auth.isLoggedIn.value) {
      return next('/')
    }
    return next()
  }

  if (to.meta.requiresAuth && !auth.isLoggedIn.value) {
    return next('/login')
  }

  next()
})

// axios 请求拦截器：自动附加 JWT 认证头
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('db_agent_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// axios 响应拦截器：统一处理 401 未授权
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('db_agent_token')
      localStorage.removeItem('db_agent_username')
      localStorage.removeItem('db_agent_role')
      localStorage.removeItem('db_agent_display_name')
      window.location.hash = '#/login'
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')