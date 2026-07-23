# 📱 CampusTaskManager — Android 校园任务管理 App

[![Java](https://img.shields.io/badge/Java-Android-ED8B00?style=flat&logo=openjdk)](https://java.com)
[![Gradle](https://img.shields.io/badge/Gradle-8-02303A?style=flat&logo=gradle)](https://gradle.org)
[![AMap](https://img.shields.io/badge/AMap-SDK_v10-1E90FF?style=flat)](https://lbs.amap.com)

基于 Android + Java + Gradle 的校园任务管理 App。集成高德地图 SDK（路线规划 + 导航）、任务 CRUD 全流程（增删改查 + 分类 + 状态）、多语言（中/英）、亮色/暗色双主题。8 个 Java 源文件 + 6 个 XML 布局 + 5 层 mipmap 图标适配。

---

## 核心功能

| 模块 | 文件 | 说明 |
|------|------|------|
| **主页** | `MainActivity.java`（7.7KB） | 任务列表展示 + 筛选 + 状态管理 |
| **任务详情** | `TaskDetailActivity.java`（4.5KB） | 任务完整信息查看 + 操作 |
| **任务编辑** | `TaskEditActivity.java`（11.7KB） | 新建/编辑任务表单（标题/描述/分类/截止/优先级） |
| **地图导航** | `MapNavigationActivity.java`（2.6KB） | 高德地图 API 路线规划 + 导航 |
| **数据模型** | `Task.java`（2.4KB） | 任务实体（id/title/description/category/status/priority...） |
| **持久化** | `SharedPrefsHelper.java`（1.9KB） | SharedPreferences 本地数据持久化 |
| **启动** | `SplashActivity.java` | 闪屏页，初始化 + 权限检查 |
| **Application** | `MyApplication.java` | 全局 Application，AMap SDK 初始化 |

## UI 特性

- **分类标签**：彩色标签（绿/黄/红）标识任务优先级
- **卡片式列表**：`item_task.xml` 自定义 CardView 布局
- **多语言**：中文简体 + 英文（`values/` + `values-en/` 双 strings）
- **双主题**：亮色主题 + 暗色主题（`values-night/themes.xml`）
- **权限处理**：高德地图定位 + 存储权限

## 技术栈

Java · Android SDK · Gradle · 高德地图 SDK v10 · SharedPreferences · XML · 多语言国际化