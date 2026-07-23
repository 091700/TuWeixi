# 🖥️ Nailong Helper — Electron 浮动桌面助手

基于 Electron 的桌面透明浮动助手，支持全局快捷键、系统托盘、语音引擎、200+ WebM 动画、实时系统监控（CPU / RAM / 网络 / 电池）。纯 Node.js + Electron + Vanilla JS。

---

## 功能

### 浮动窗口

- 透明无边框窗口，始终置顶
- 调整大小 / 透明度 / 缩放（设置页面可调）
- 亮色 / 暗色主题切换
- `Ctrl+Alt+Q` 全局快捷键隐藏/显示

### 动画系统

- 200+ WebM 动画（`assets/` 目录）
- `nailongdaxiao.webm` — 大笑动画
- `nailonghuishou.webm` — 回收动画
- 随机播放 / 顺序播放可选

### 语音引擎

- 语音识别（Speech-to-Text）+ 合成（Text-to-Speech）
- `voice_engine/` 目录独立管理语音模型
- 长时间静音自动停止

### 系统监控

- CPU 使用率
- 内存占用
- 网络流量
- 电池状态
- 实时更新显示在悬浮窗

### 系统集成

- 系统托盘（右键菜单：显示/隐藏/退出）
- 开机自启动
- 打包安装程序（electron-builder + NSIS）

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `main.js` | Electron 主进程（370行），窗口管理 + 全局快捷键 + 托盘 + 语音引擎 |
| `preload.js` | 预加载脚本，暴露安全的 IPC 接口 |
| `renderer.js` | 渲染进程，动画播放 / 系统监控 / 设置同步 |
| `index.html` | 主浮动窗口 |
| `settings.html` + `settings.js` | 设置页面 |
| `style.css` | 全站样式 |
| `config.json` | 用户配置持久化 |
| `package.json` | 项目配置 + electron-builder 打包 |
| `assets/` | 图标 (`nailong.ico`, `nailong.png`) + WebM 动画 |

## 启动

```bash
npm install
npm start
```

## 打包

```bash
npm run build
```

输出到 `dist/` 目录，生成 Windows NSIS 安装包。

## 技术栈

Electron 30 · Node.js · electron-store · systeminformation · electron-builder · Vanilla JavaScript