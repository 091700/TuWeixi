export const API_BASE = 'http://127.0.0.1:8000/api'
export const HEALTH_INTERVAL = 120000 // 2分钟健康检查间隔
export const STORAGE_KEYS = {
  sessions: 'db_agent_sessions',
  favorites: 'db_agent_saved_sessions',
  snapshot: (id) => `db_agent_snapshot_${id}`,
  pendingRestore: 'db_agent_pending_restore',
}