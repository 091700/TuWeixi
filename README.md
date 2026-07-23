# 👨‍💻 TuWeixi  — Full-Stack Developer & AI Engineer

[![GitHub Stars](https://img.shields.io/github/stars/091700/TuWeixi?style=flat&color=blue)](https://github.com/091700/TuWeixi/stargazers)
[![Projects](https://img.shields.io/badge/Projects-12-blue?style=flat)](https://github.com/091700/TuWeixi)
[![Languages](https://img.shields.io/badge/Languages-Java_|_Python_|_JavaScript_|_PHP_|_C%23_|_GDScript-blueviolet?style=flat)]()
[![AI](https://img.shields.io/badge/AI-DeepSeek_|_Whisper_|_YOLO_|_Qwen_|_ChromaDB-brightgreen?style=flat)]()

> 浙江师范大学毕业 · 全栈项目工程师 · AI 应用落地的爱好者

---

## 📂 项目矩阵

### 🔥 旗舰项目

| 项目 | 技术栈 | 简介 |
|------|--------|------|
| **🗄️ sql_agent** | `Python` `FastAPI` `Vue 3` `DeepSeek R1` `ChromaDB` | 从零手写的 LLM Agent 全栈项目。Agent Loop（五维终止 + LLM 自评 + Self-Healing）、Multi-Agent Orchestrator（DAG 任务图 → Kahn 拓扑排序 → asyncio.gather 并行）、PER 优先经验回放（TD-error + heapq 采样 + System Prompt 注入）、CoT 思维链可视化。三层 SQL 沙箱 + RBAC + Guardrails + 高危审批。1460 行纯自研代码，零框架黑盒。 |
| **🎙️ SmartInterview_Project** | `Java Spring Boot` `Python` `Whisper GPU` `Vue 3` `ChromaDB` | AI 模拟面试平台。WebSocket 实时交互（353 行 InterviewWebSocketServer）、Faster-Whisper GPU ASR + librosa 声学三指标评分（紧张度/自信度/清晰度）、RAG 知识库（ChromaDB + BAAI/bge-small-zh-v1.5）、DeepSeek 内容评分 + 追问生成。 |
| **🧊 SmartPantry** | `Java Spring Boot` `Python` `PyTorch` `Qwen LLM` `Vue 3` | 智能冰箱管理系统。PyTorch 全连接网络预测食材保鲜期、5 维风味向量余弦相似度计算黑暗料理评分、Qwen 2.5-1.5B 零样本食材特征提取（553 行 app.py）、含 19 种硬编码风味特征的基础食材库。 |
| **📚 intelligent-book-platform** | `Java Spring Boot` `Elasticsearch 8` `YOLOv5` `Thymeleaf` | 智能图书交易平台。Elasticsearch 全文搜索（多字段模糊匹配 + `_score` 排序）、YOLOv5 以图搜书（Python ONNX 导出 + Java 子进程调用）、Tesseract OCR 图书封面文字识别、Spring Security + BCrypt。 |

### ⚙️ 工程类项目

| 项目 | 技术栈 | 简介 |
|------|--------|------|
| **🖥️ electron-floating-helper** | `Electron 30` `Node.js` `DeepSeek Chat` | 桌面透明浮动助手「奶龙」——边缘吸附引擎（20px 阈值 + 150ms 防抖 + 45px 脱离距离）、实时系统监控（CPU/内存/网络每秒轮询）、DeepSeek 本地聊天（electron-store 持久化 + 历史清理）、语音引擎（cmd.exe 子进程管理 + taskkill /T/F 强制清理）。 |
| **📱 campustaskmanager** | `Java` `Android SDK` `高德地图 SDK` `Gradle` | Android 校园任务管理 App。集成高德地图路线规划 + 导航、任务 CRUD + 分类/状态管理、中/英双语 + 亮/暗双主题、8 个 Java 源文件 + 6 个 XML 布局。 |
| **🏪 WarehouseSystem** | `Java` `Spring MVC` `JDBC` `Druid` `JSP` | 仓库管理系统。24 个 Java 源文件——10 个 Controller + 7 个 DAO + 5 个 Model + Filter/Util，覆盖商品管理、订单管理、入库/出库、客户/供应商管理、多仓库管理全流程。 |

### 🎨 轻量与 Web 类项目

| 项目 | 技术栈 | 简介 |
|------|--------|------|
| **🎮 niu-qu-game** | `Godot 4` `GDScript` | 2D 游戏工具框架。8 个 GDScript 核心模块——碰撞区域工厂（428 行，8 种碰撞体 + 6 关卡传送系统，6 个 Boss 顺序解锁）、可破坏物体系统 + 对象池 + 粒子管理器 + 相机抖动 + 伪动画补间。 |
| **🛒 e-commerce** | `PHP 8` `MySQL` `PDO` `Session` | PHP 电商系统。15 个 PHP 文件覆盖用户注册/登录、产品管理、购物车、结算、后台 CRUD。 |
| **📋 student-manage-system** | `Java Spring Boot` `Apache POI` `Thymeleaf` | 学生管理系统。14 个 Java 源文件——5 个 Controller/Service + 4 个 DAO/Entity + ExcelUtil（Apache POI 批量导入导出）+ LoginInterceptor 登录拦截。 |

---

## 🧠 技术雷达

| 维度 | 关键词 |
|------|--------|
| **语言** | Java · Python · JavaScript · PHP · C# · GDScript |
| **后端框架** | Spring Boot 3 · Spring MVC · FastAPI · Electron |
| **前端** | Vue 3 · Thymeleaf · JSP · Vanilla JS · Bootstrap |
| **AI/ML** | DeepSeek · Faster-Whisper · YOLOv5 · Qwen 2.5 · ChromaDB · LangChain · librosa · PyTorch |
| **搜索与数据** | Elasticsearch 8 · MySQL 8.0 · MyBatis-Plus · JPA · JDBC · Druid |
| **其他** | WebSocket · Godot 4 · Android SDK · 高德地图 · Gradle · Maven · Git |

---

> *"Code is poetry, but architecture is the soul."*

*访问 [github.com/091700/TuWeixi](https://github.com/091700/TuWeixi) 查看各项目源码与 README 详情。*
