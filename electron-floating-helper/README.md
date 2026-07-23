# 🖥️ Nailong Helper — Electron 桌面奶龙助手

基于 Electron 30 的桌面浮动助手。透明无边框窗口，支持边缘吸附停靠（左/右边缘 20px 阈值检测 + 150ms 防抖自动弹回 + 45px 拖拽脱离距离）、实时系统监控（CPU / 内存 / 网络，`systeminformation` 每秒轮询）、DeepSeek 聊天（本地 `chat-history` store 持久化 + 7天/30天/1年历史清理）、奶龙弹珠屏保（`NailongBall` 物理模拟 + requestAnimationFrame 循环）、语音引擎（cmd.exe 子进程 management + `taskkill /T /F` 进程树清理），支持全局快捷键、亮/暗主题、自定义缩放。

---

## 核心系统

### 边缘吸附引擎（main.js L74-156）

基于防抖拖拽的完全重构边缘吸附：

- `dock()`：距离边缘 < 20px 触发，窗口缩为 60×60 圆球，`setAlwaysOnTop(true)`
- `restore()`：拖拽拉出 > 45px 恢复原尺寸，自动避让边缘（15px buffer），600ms 冷却防误触
- 150ms 防抖定时器：用户拖拽未松手时不动 bounds，松手后自动弹回

### 系统监控（main.js L182-208）

`systeminformation` 每秒采集：
- `si.currentLoad()` → CPU 使用率
- `si.mem()` → 内存占用百分比
- `si.networkStats()` → 实时上下行网速（KB/s）
- 通过 IPC `system-info` 事件推送渲染进程

### DeepSeek 聊天（main.js L254-332）

`electron-store` 本地持久化聊天记录 + 会话管理：
- System Prompt 限定角色为“可爱幽默的奶龙”，回复控制在 100 字内
- `get-chat-history`：加载历史记录到前端 UI
- `clear-chat-history`：按范围清除（全部 / 7天 / 30天 / 1年），无 timestamp 的旧数据统一清理
- API：`api.deepseek.com/chat/completions`，`temperature: 0.7`

### 语音引擎（main.js L22-51）

`spawn('cmd.exe', ['/c', start_voice.bat])` 启动语音识别/合成：
- 展开面板按需启动，收缩后 14 秒延迟自动关闭
- `will-quit` 时 `taskkill /T /F` 强制清理子进程树

### 弹珠屏保（renderer.js L127-166）

`NailongBall` 类，WebM 动画视频节点 + 物理模拟：
- 30-50px 随机尺寸，`(Math.random() - 0.5) * 14` 随机初速度
- 与窗口碰撞反弹 + 速度衰减（`vx *= 1.05` 加速扩散）
- `requestAnimationFrame` 驱动渲染循环，离屏自动销毁

### 弹幕系统（renderer.js L100-111）

7 条预设弹幕（"我是奶龙""涂维兮yyds" 等），鼠标进入 / 闲置 20s 触发，2.5s 后自动移除。

---

## 文件说明

| 文件 | 行数 | 说明 |
|------|------|------|
| `main.js` | 370 | 主进程：窗口/吸附/监控/聊天/语音/快捷键 |
| `renderer.js` | 219 | 渲染进程：动画/弹幕/弹珠/聊天 UI |
| `preload.js` | - | 预加载：IPC 接口暴露 |
| `index.html` | - | 主浮动窗口 |
| `settings.html` + `settings.js` | - | 设置页：缩放/透明度/主题/快捷键 |
| `style.css` | - | 全站样式 |
| `config.json` | - | 持久化配置 |
| `assets/` | - | 图标 + WebM 动画 + 语音模型 |

---

## 启动

```bash
npm install
npm start
```

## 打包

```bash
npm run build
```

输出 Windows NSIS 安装包至 `dist/`。

## 技术栈

Electron 30 · electron-store · systeminformation · DeepSeek API · Vanilla JS · electron-builder
