# TuWeixi

[![GitHub Stars](https://img.shields.io/github/stars/091700/TuWeixi?style=flat&color=blue)](https://github.com/091700/TuWeixi/stargazers)
[![Projects](https://img.shields.io/badge/Projects-12-blue?style=flat)](https://github.com/091700/TuWeixi)
[![Focus](https://img.shields.io/badge/Focus-AI%20Agent%20%7C%20Full--Stack%20%7C%20Game-blueviolet?style=flat)]()

12 个自研项目，覆盖 AI Agent、全栈 Web、桌面工具与游戏。每个仓库都有独立 README，记录实现思路、关键取舍和踩过的坑。

---

## 📂 项目矩阵

### 🤖 AI 与全栈

| 项目 | 技术栈 | 简介 |
|------|--------|------|
| **🗄️ sql_agent** | `Python` `FastAPI` `Vue 3` `DeepSeek R1` `ChromaDB` | 从零实现的 LLM Agent 全栈项目。核心是一套可解释的 Agent Loop：五维终止条件、LLM 自评、失败后 Self-Healing 重试；多 Agent 协作把任务拆成 DAG，用 Kahn 拓扑排序分层，`asyncio.gather` 并行执行。加入 PER 优先经验回放，按 TD-error 采样历史经验并注入 System Prompt。SQL 侧做了三层沙箱、RBAC 与高危操作审批。1460 行自研代码，没有套 LangChain 之类的框架黑盒。 |
| **🎙️ SmartInterview_Project** | `Java Spring Boot` `Python` `Whisper GPU` `Vue 3` `ChromaDB` | AI 模拟面试平台。WebSocket 承载实时对话（353 行 InterviewWebSocketServer），Faster-Whisper 在 GPU 上做语音转写，librosa 提取紧张度、自信度、清晰度三项声学指标。知识库用 ChromaDB + BAAI/bge-small-zh-v1.5 做 RAG 检索，DeepSeek 负责内容评分和追问生成。 |
| **🧊 SmartPantry** | `Java Spring Boot` `Python` `PyTorch` `Qwen` `Vue 3` | 智能冰箱管理系统。PyTorch 全连接网络预测食材保鲜期，5 维风味向量做余弦相似度，给"黑暗料理"打分。Qwen 2.5-1.5B 零样本提取食材特征（553 行 app.py），配 19 种人工整理的风味特征基础食材库。 |
| **📚 intelligent-book-platform** | `Java Spring Boot` `Elasticsearch 8` `YOLOv5` `Thymeleaf` | 智能图书交易平台。Elasticsearch 做多字段模糊搜索并按 `_score` 排序，YOLOv5 实现以图搜书（Python 导出 ONNX，Java 子进程调用），Tesseract OCR 识别封面文字。账号体系用 Spring Security + BCrypt。 |

### 🎮 游戏

| 项目 | 技术栈 | 简介 |
|------|--------|------|
| **🍬 BestGameForever2** | `Cocos Creator 2.4.2` `JavaScript` `Canvas 2D` | 完整三消游戏。7×9 棋盘、8 个世界 × 99 关，第 7 关之后的地图由 LCG 伪随机生成，保证同一关每次打开都一致，并校验至少存在一组可消三连。单组四连生成炸弹，3×3 范围连锁引爆；清空全部格子的背景后触发 GoalGem 下落通关。连击按 `10 × (连击数 + 组数 - 1)` 计分，叠加时间奖励与三星结算。另有空闲 7 秒提示、无解自动洗牌、暂停面板、胜负结算和 BGM 循环。26 个脚本约 4100 行，MVC 分层 + 事件总线，动画全部用 `cc.tween` 实现。 |
| **🎮 niu-qu-game** | `Godot 4` `GDScript` | 2D 游戏工具框架，8 个可复用模块。碰撞区域工厂 428 行，覆盖 8 种碰撞体、6 个关卡传送点和 6 个 Boss 顺序解锁；另外提供可破坏物体系统、对象池、粒子管理器、相机抖动和伪动画补间。 |

### ⚙️ 桌面与工程

| 项目 | 技术栈 | 简介 |
|------|--------|------|
| **🖥️ electron-floating-helper** | `Electron 30` `Node.js` `DeepSeek Chat` | 桌面透明浮动助手「奶龙」。边缘吸附用 20px 阈值 + 150ms 防抖 + 45px 脱离距离，避免贴边时反复横跳。每秒轮询 CPU、内存、网络占用；聊天记录用 electron-store 落盘并定期清理。语音模块通过 cmd.exe 子进程管理，退出时 `taskkill /T /F` 强制回收。 |
| **📱 campustaskmanager** | `Java` `Android SDK` `高德地图 SDK` | Android 校园任务管理 App。接入高德地图完成路线规划和导航，任务支持增删改查、分类与状态流转。中英双语、亮暗双主题，共 8 个 Java 源文件与 6 个 XML 布局。 |
| **🏪 WarehouseSystem** | `Java` `Spring MVC` `JDBC` `Druid` `JSP` | 仓库管理系统。24 个 Java 源文件，10 个 Controller、7 个 DAO、5 个 Model 加 Filter/Util，覆盖商品、订单、出入库、客户/供应商和多仓库全流程。 |
| **📋 student-manage-system** | `Java Spring Boot` `Apache POI` `Thymeleaf` | 学生管理系统。14 个 Java 源文件，Controller/Service/DAO 分层清晰。用 Apache POI 批量导入导出 Excel，LoginInterceptor 统一做登录拦截。 |
| **🛒 e-commerce** | `PHP 8` `MySQL` `PDO` `Session` | PHP 电商系统。15 个 PHP 文件覆盖注册登录、商品管理、购物车、下单结算和后台 CRUD，数据层统一走 PDO 预处理。 |
| **⚡ NetAcceleratorWin** | `C#` `.NET Framework` `WinForms` | WinForms 恶搞小工具，启动页 + 视频播放两套窗体。用 Fody/Costura 把依赖合并进单个 exe，双击即运行，仅供娱乐。 |

---

## 🧠 技术栈

| 方向 | 实际使用过的技术 |
|------|------------------|
| **语言** | Java · Python · JavaScript · PHP · C# · GDScript · SQL |
| **后端** | Spring Boot · Spring MVC · FastAPI · Electron 主进程 |
| **前端** | Vue 3 · Thymeleaf · JSP · 原生 JS · Bootstrap |
| **AI / 数据** | DeepSeek · Faster-Whisper · YOLOv5 · Qwen · PyTorch · ChromaDB · librosa · Elasticsearch |
| **存储** | MySQL · MyBatis-Plus · JPA · JDBC · Druid |
| **工程** | WebSocket · Cocos Creator 2.4.2 · Godot 4 · Android SDK · 高德地图 SDK · Maven · Gradle · Git |

---

## 🌱 最近在做

- **BestGameForever2**：关卡地图与炸弹连锁已完成，下一步补关卡平衡和特殊宝石组合。
- **sql_agent**：继续打磨 Agent Loop 的终止策略与经验回放命中率。

---

各项目的源码、目录结构和实现细节，见仓库内对应的 README。
