# TuWeixi

[![GitHub Stars](https://img.shields.io/github/stars/091700/TuWeixi?style=flat&color=blue)](https://github.com/091700/TuWeixi/stargazers)
[![Projects](https://img.shields.io/badge/Projects-12-blue?style=flat)](https://github.com/091700/TuWeixi)

个人项目合集，共 12 个仓库，每个仓库内附独立 README。

---

## 📂 项目矩阵

### 🔥 主力项目

| 项目 | 技术栈 | 简介 |
|------|--------|------|
| **🗄️ sql_agent** | `Python` `FastAPI` `Vue 3` `DeepSeek R1` `ChromaDB` | 从零实现的 LLM Agent 全栈项目。Agent Loop（五维终止 + LLM 自评 + Self-Healing）、Multi-Agent 编排（DAG 任务图 → Kahn 拓扑排序 → asyncio.gather 并行）、PER 优先经验回放（TD-error + heapq 采样 + System Prompt 注入）、CoT 思维链可视化。三层 SQL 沙箱 + RBAC + Guardrails + 高危审批。1460 行纯自研代码，零框架黑盒。 |
| **🎙️ SmartInterview_Project** | `Java Spring Boot` `Python` `Whisper GPU` `Vue 3` `ChromaDB` | AI 模拟面试平台。WebSocket 实时交互（353 行 InterviewWebSocketServer）、Faster-Whisper GPU 语音识别 + librosa 声学三指标评分（紧张度/自信度/清晰度）、RAG 知识库（ChromaDB + BAAI/bge-small-zh-v1.5）、DeepSeek 内容评分与追问生成。 |
| **🧊 SmartPantry** | `Java Spring Boot` `Python` `PyTorch` `Qwen` `Vue 3` | 智能冰箱管理系统。PyTorch 全连接网络预测食材保鲜期、5 维风味向量余弦相似度计算黑暗料理评分、Qwen 2.5-1.5B 零样本食材特征提取（553 行 app.py）、19 种硬编码风味特征的基础食材库。 |
| **📚 intelligent-book-platform** | `Java Spring Boot` `Elasticsearch 8` `YOLOv5` `Thymeleaf` | 智能图书交易平台。Elasticsearch 全文搜索（多字段模糊匹配 + `_score` 排序）、YOLOv5 以图搜书（Python ONNX 导出 + Java 子进程调用）、Tesseract OCR 封面文字识别、Spring Security + BCrypt。 |

### 🎮 游戏

| 项目 | 技术栈 | 简介 |
|------|--------|------|
| **🍬 BestGameForever2** | `Cocos Creator 2.4.2` `JavaScript` `Canvas 2D` | 完整三消游戏。7×9 棋盘、8 个世界 × 99 关（关卡地图程序生成，LCG 伪随机保证同关一致）、炸弹 3×3 连锁引爆、GoalGem 胜利条件、连击计分 + 时间奖励 + 三星结算、无解自动洗牌与空闲提示、暂停/胜负场景、BGM 循环。26 个脚本约 4100 行，MVC 分层 + 事件总线，全部动画用 `cc.tween` 实现。 |
| **🎮 niu-qu-game** | `Godot 4` `GDScript` | 2D 游戏工具框架。8 个核心模块：碰撞区域工厂（428 行，8 种碰撞体 + 6 关卡传送，6 个 Boss 顺序解锁）、可破坏物体系统、对象池、粒子管理器、相机抖动、伪动画补间。 |

### ⚙️ 桌面与工程

| 项目 | 技术栈 | 简介 |
|------|--------|------|
| **🖥️ electron-floating-helper** | `Electron 30` `Node.js` `DeepSeek Chat` | 桌面透明浮动助手「奶龙」。边缘吸附（20px 阈值 + 150ms 防抖 + 45px 脱离距离）、系统监控（CPU/内存/网络每秒轮询）、DeepSeek 本地聊天（electron-store 持久化）、语音引擎（cmd.exe 子进程管理 + taskkill 强制清理）。 |
| **📱 campustaskmanager** | `Java` `Android SDK` `高德地图 SDK` | Android 校园任务管理 App。高德地图路线规划与导航、任务 CRUD 与分类/状态管理、中英双语、亮暗双主题。 |
| **🏪 WarehouseSystem** | `Java` `Spring MVC` `JDBC` `Druid` `JSP` | 仓库管理系统。24 个 Java 源文件（10 Controller + 7 DAO + 5 Model），覆盖商品、订单、出入库、客户/供应商、多仓库全流程。 |
| ** student-manage-system** | `Java Spring Boot` `Apache POI` `Thymeleaf` | 学生管理系统。14 个 Java 源文件，Apache POI 批量导入导出 Excel，LoginInterceptor 登录拦截。 |
| **🛒 e-commerce** | `PHP 8` `MySQL` `PDO` `Session` | PHP 电商系统。15 个 PHP 文件覆盖注册登录、产品管理、购物车、结算、后台 CRUD。 |
| **⚡ NetAcceleratorWin** | `C#` `.NET Framework` `WinForms` | WinForms 恶搞小工具。启动页 + 视频播放，Fody/Costura 合并打包成单文件，仅供娱乐。 |

---

源码与详细说明见各仓库内的 README：[github.com/091700/TuWeixi](https://github.com/091700/TuWeixi)
