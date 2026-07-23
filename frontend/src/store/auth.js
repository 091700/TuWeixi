import { reactive, computed } from 'vue'

const state = reactive({
  token: localStorage.getItem('db_agent_token') || '',
  username: localStorage.getItem('db_agent_username') || '',
  role: localStorage.getItem('db_agent_role') || '',
  displayName: localStorage.getItem('db_agent_display_name') || '',
})

export function useAuth() {
  const isLoggedIn = computed(() => !!state.token)
  const isAdmin = computed(() => state.role === 'admin')

  function setAuth(token, username, role, displayName) {
    state.token = token
    state.username = username
    state.role = role
    state.displayName = displayName
    localStorage.setItem('db_agent_token', token)
    localStorage.setItem('db_agent_username', username)
    localStorage.setItem('db_agent_role', role)
    localStorage.setItem('db_agent_display_name', displayName)
  }

  function logout() {
    state.token = ''
    state.username = ''
    state.role = ''
    state.displayName = ''
    localStorage.removeItem('db_agent_token')
    localStorage.removeItem('db_agent_username')
    localStorage.removeItem('db_agent_role')
    localStorage.removeItem('db_agent_display_name')
  }

  function getAuthHeaders() {
    if (!state.token) return {}
    return { Authorization: `Bearer ${state.token}` }
  }

  return { state, isLoggedIn, isAdmin, setAuth, logout, getAuthHeaders }
}