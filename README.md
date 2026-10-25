<div align="center">
  <img src="assets/profile/hero.svg" width="100%" alt="TuWeixi — 12 projects">
  <br><br>
  <img src="https://img.shields.io/badge/PROJECTS-12-5B8CFF?style=flat-square" alt="Projects">
  <img src="https://img.shields.io/badge/LANGUAGES-7-9B6BFF?style=flat-square" alt="Languages">
  <img src="https://img.shields.io/badge/AI-4%20PROJECTS-FF6BD6?style=flat-square" alt="AI Projects">
  <img src="https://img.shields.io/github/stars/091700/TuWeixi?style=flat-square&color=FFC53D" alt="Stars">
  <br><br>
  <sub>12 个自研项目，覆盖 AI Agent、全栈 Web、桌面工具与游戏。<br>每个仓库都有独立 README，记录实现思路与关键取舍。</sub>
</div>

---

## 🤖 AI 与全栈

四个项目，覆盖 Agent、语音面试、食材预测和图书检索。

### 🗄️ sql_agent · LLM Agent 全栈

从零实现的 LLM Agent 全栈项目，后端 FastAPI、前端 Vue 3，共 1460 行自研代码。Agent Loop 用五维终止条件、LLM 自评和失败后的 Self-Healing 重试控制执行；多 Agent 协作先把任务拆成 DAG，用 Kahn 拓扑排序分层，再通过 `asyncio.gather` 并行。历史经验由 PER 优先回放按 TD-error 采样，注入 System Prompt。SQL 侧做了三层沙箱、RBAC 权限和高危操作审批，避免模型直接改动生产数据。

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"> <img src="https://img.shields.io/badge/Vue_3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white"> <img src="https://img.shields.io/badge/DeepSeek-4B6BFB?style=flat-square"> <img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=flat-square">

### 🎙️ SmartInterview · AI 模拟面试

AI 模拟面试平台，Java Spring Boot 提供接口，Python 负责语音与评分。面试对话走 WebSocket 实时推送，服务端核心 353 行；Faster-Whisper 在 GPU 上做语音转写，librosa 提取紧张度、自信度、清晰度三项声学指标。知识库用 ChromaDB 存向量，BAAI/bge-small-zh-v1.5 做检索，DeepSeek 负责内容评分和追问生成。

<img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white"> <img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white"> <img src="https://img.shields.io/badge/Whisper-7C3AED?style=flat-square"> <img src="https://img.shields.io/badge/Vue_3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white"> <img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=flat-square">

### 🧊 SmartPantry · 智能冰箱管理

智能冰箱管理系统。PyTorch 全连接网络根据食材类型和存放时间预测保鲜期，5 维风味向量做余弦相似度，计算黑暗料理的离谱程度。Qwen 2.5-1.5B 零样本提取食材特征，配合 19 种人工整理的基础食材风味库，前端用 Vue 3 展示库存和推荐。

<img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white"> <img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white"> <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white"> <img src="https://img.shields.io/badge/Qwen-615CED?style=flat-square"> <img src="https://img.shields.io/badge/Vue_3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white">

### 📚 Intelligent Book Platform · 智能图书交易

智能图书交易平台，Java Spring Boot + Thymeleaf。搜索用 Elasticsearch 做多字段模糊匹配，结果按 `_score` 排序；以图搜书由 YOLOv5 完成，模型导出 ONNX 后由 Java 子进程调用；封面文字用 Tesseract OCR 识别。账号体系基于 Spring Security + BCrypt，商品与订单数据存 MySQL。

<img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white"> <img src="https://img.shields.io/badge/Elasticsearch-005571?style=flat-square&logo=elasticsearch&logoColor=white"> <img src="https://img.shields.io/badge/YOLOv5-00BFFF?style=flat-square"> <img src="https://img.shields.io/badge/Thymeleaf-005F0F?style=flat-square&logo=thymeleaf&logoColor=white"> <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white">

---

## 🎮 游戏

两个项目：一个完整三消，一个 2D 工具框架。

### 🍬 BestGameForever2 · 完整三消游戏

26 个脚本约 4100 行，按 MVC 分层并配了一套事件总线。棋盘 7×9、8 个世界 × 99 关，第 7 关之后的地图由 LCG 伪随机生成，保证同一关每次打开一致，并校验至少存在一组可消三连。单组四连会在组内生成炸弹，下次消除时炸掉周围 3×3，波及的炸弹继续引爆；清空全部格子的背景后，GoalGem 从最后消除的位置下落通关。计分由单颗分值、连锁奖励和时间奖励组成，结算按总分给一到三星。动画全部用 `cc.tween` 实现，另外做了空闲 7 秒提示、无解自动洗牌、暂停、胜负场景和 BGM 循环。

<img src="https://img.shields.io/badge/Cocos_Creator_2.4.2-55C2E1?style=flat-square&logo=cocos&logoColor=white"> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"> <img src="https://img.shields.io/badge/Canvas_2D-2C2255?style=flat-square">

### 🎮 niu-qu-game · 2D 游戏工具框架

Godot 4 的 2D 游戏工具框架，拆成 8 个可复用 GDScript 模块。碰撞区域工厂 428 行，覆盖 8 种碰撞体、6 个关卡传送点和 6 个 Boss 顺序解锁；可破坏物体系统负责受击与掉落，对象池复用高频节点，粒子管理器统一爆炸与特效。另有相机抖动和伪动画补间，用来在不引入额外插件的情况下补足手感。

<img src="https://img.shields.io/badge/Godot_4-478CBF?style=flat-square&logo=godotengine&logoColor=white"> <img src="https://img.shields.io/badge/GDScript-355570?style=flat-square">

---

## ⚙️ 桌面与工程

六个项目，覆盖 Electron、Android、Spring MVC 和 PHP。

### 🖥️ electron-floating-helper · 桌面浮窗助手

Electron 30 写的透明桌面浮窗「奶龙」。边缘吸附用 20px 阈值、150ms 防抖和 45px 脱离距离，避免贴边时反复横跳；系统监控每秒轮询 CPU、内存和网络占用。聊天接入 DeepSeek，对话记录用 electron-store 落盘并定期清理。语音模块通过 `cmd.exe` 子进程管理，退出时用 `taskkill /T /F` 连同子进程一起回收。

<img src="https://img.shields.io/badge/Electron_30-47848F?style=flat-square&logo=electron&logoColor=white"> <img src="https://img.shields.io/badge/Node.js-5FA04E?style=flat-square&logo=nodedotjs&logoColor=white"> <img src="https://img.shields.io/badge/DeepSeek-4B6BFB?style=flat-square">

### 📱 CampusTaskManager · Android 校园任务

Android 校园任务管理 App，Java + Android SDK。接入高德地图 SDK 完成路线规划和导航，任务支持增删改查、分类和状态流转，列表与详情页联动。中英双语和亮暗双主题都做了资源适配，共 8 个 Java 源文件和 6 个 XML 布局。

<img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white"> <img src="https://img.shields.io/badge/Android-34A853?style=flat-square&logo=android&logoColor=white"> <img src="https://img.shields.io/badge/AMap-0091FF?style=flat-square">

### 🏪 WarehouseSystem · 仓库管理

仓库管理系统，Java Spring MVC + JSP。24 个 Java 源文件，拆成 10 个 Controller、7 个 DAO、5 个 Model，覆盖商品、订单、出入库、客户/供应商和多仓库管理。数据层用 JDBC + Druid 连接池，页面由 JSP 渲染。

<img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white"> <img src="https://img.shields.io/badge/Spring_MVC-6DB33F?style=flat-square&logo=spring&logoColor=white"> <img src="https://img.shields.io/badge/JSP-FF6B00?style=flat-square"> <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white">

### 📋 Student Manager · 学生管理

学生管理系统，Spring Boot + Thymeleaf。14 个 Java 源文件，Controller / Service / DAO 分层，Apache POI 负责 Excel 批量导入导出，LoginInterceptor 统一处理登录拦截。页面由 Thymeleaf 渲染，表单校验和登录状态都在后端完成。

<img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white"> <img src="https://img.shields.io/badge/Thymeleaf-005F0F?style=flat-square&logo=thymeleaf&logoColor=white"> <img src="https://img.shields.io/badge/Apache_POI-D22128?style=flat-square&logo=apache&logoColor=white">

### 🛒 e-commerce · PHP 电商系统

PHP 8 电商系统，15 个 PHP 文件覆盖注册登录、商品管理、购物车和下单结算，后台提供商品 CRUD。数据层统一走 PDO 预处理，登录态用 Session 保存，页面由 PHP 直接渲染。

<img src="https://img.shields.io/badge/PHP_8-777BB4?style=flat-square&logo=php&logoColor=white"> <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white">

### ⚡ NetAcceleratorWin · WinForms 小工具

WinForms 恶搞小工具。启动页和视频播放做成两套窗体，用 Fody / Costura 把依赖合并进单个 exe，双击即可运行，不需要额外安装环境。项目只为娱乐，没有实际加速功能。

<img src="https://img.shields.io/badge/C%23-512BD4?style=flat-square&logo=dotnet&logoColor=white"> <img src="https://img.shields.io/badge/.NET_Framework-512BD4?style=flat-square&logo=dotnet&logoColor=white">

---

## 🛠️ 技术栈

| 方向 | 用过的技术 |
|------|------------|
| **语言** | <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white"> <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"> <img src="https://img.shields.io/badge/PHP-777BB4?style=flat-square&logo=php&logoColor=white"> <img src="https://img.shields.io/badge/C%23-512BD4?style=flat-square&logo=dotnet&logoColor=white"> <img src="https://img.shields.io/badge/GDScript-355570?style=flat-square"> |
| **后端** | <img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white"> <img src="https://img.shields.io/badge/Spring_MVC-6DB33F?style=flat-square&logo=spring&logoColor=white"> <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"> <img src="https://img.shields.io/badge/Electron-47848F?style=flat-square&logo=electron&logoColor=white"> |
| **前端** | <img src="https://img.shields.io/badge/Vue_3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white"> <img src="https://img.shields.io/badge/Thymeleaf-005F0F?style=flat-square&logo=thymeleaf&logoColor=white"> <img src="https://img.shields.io/badge/JSP-FF6B00?style=flat-square"> <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=flat-square&logo=bootstrap&logoColor=white"> |
| **AI / 数据** | <img src="https://img.shields.io/badge/DeepSeek-4B6BFB?style=flat-square"> <img src="https://img.shields.io/badge/Whisper-7C3AED?style=flat-square"> <img src="https://img.shields.io/badge/YOLOv5-00BFFF?style=flat-square"> <img src="https://img.shields.io/badge/Qwen-615CED?style=flat-square"> <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white"> <img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=flat-square"> |
| **存储** | <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white"> <img src="https://img.shields.io/badge/Elasticsearch-005571?style=flat-square&logo=elasticsearch&logoColor=white"> <img src="https://img.shields.io/badge/MyBatis--Plus-D77310?style=flat-square"> <img src="https://img.shields.io/badge/JPA-59666C?style=flat-square&logo=hibernate&logoColor=white"> <img src="https://img.shields.io/badge/Druid-1C9B5E?style=flat-square"> |
| **工程** | <img src="https://img.shields.io/badge/WebSocket-010101?style=flat-square&logo=socketdotio&logoColor=white"> <img src="https://img.shields.io/badge/Cocos_Creator-55C2E1?style=flat-square&logo=cocos&logoColor=white"> <img src="https://img.shields.io/badge/Godot_4-478CBF?style=flat-square&logo=godotengine&logoColor=white"> <img src="https://img.shields.io/badge/Android-34A853?style=flat-square&logo=android&logoColor=white"> <img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white"> <img src="https://img.shields.io/badge/Maven-C71A36?style=flat-square&logo=apachemaven&logoColor=white"> <img src="https://img.shields.io/badge/Gradle-02303A?style=flat-square&logo=gradle&logoColor=white"> |

---

<div align="center">
  <a href="https://github.com/091700/TuWeixi"><img src="https://img.shields.io/badge/GitHub-091700-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
  <br><br>
  <sub>项目源码、目录结构与实现细节，见各仓库内的 README。</sub>
</div>
