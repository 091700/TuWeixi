# 🗄️ DB Agent — 基于 LLM 的数据库自治代理系统

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Vue3](https://img.shields.io/badge/Vue_3-Element_Plus-4FC08D?style=flat&logo=vuedotjs)](https://vuejs.org)
[![React](https://img.shields.io/badge/React_18-系统仪表盘-61DAFB?style=flat&logo=react)](https://react.dev)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek_Chat_/_R1-4D6BFE?style=flat)](https://deepseek.com)
[![ChromaDB](https://img.shields.io/badge/RAG-ChromaDB_+_Sentence--Transformers-121212?style=flat)](https://trychroma.com)
[![MySQL](https://img.shields.io/badge/DB-MySQL_8.0-4479A1?style=flat&logo=mysql)](https://mysql.com)

1,460 行纯自研代码 · 12 个算法模块 · P0-P2 三级全落地 · 零框架黑盒

---

## 技术架构

```
前端: Vue 3 (Composition API + Element Plus) + React 18 (系统监控仪表盘)
后端: FastAPI (SSE 流式 + 30 个 REST 端点)
Agent 层: Orchestrator → TokenBudget → AdaptiveLoop → Tools
安全: 三层 SQL 沙箱 + RBAC + JWT + 审计日志 + 连接池
记忆: Working Memory → PER 经验回放 → ChromaDB RAG
数据库: MySQL 8.0 + agent_auth 认证库
```

---

## 核心算法

### Agent Loop

采用**混合终止策略**：五维规则层 + LLM 语义层联合判断。

- Token Budget 经济模型（正常 → 预警 → 临界 → 超限，分步降级）
- 五维自适应终止（指纹冗余检测 / 连续失败 / 信息增益停滞 / 数据充分 / 轮次上限）
- LLM Self-Evaluator 语义级自评：输出 `{can_answer, confidence, missing}` 决策 JSON
- 规则兜底（Token 耗尽、最大轮次、重复错误）+ JSON 解析容错 + 关键词回退

**失败自愈**：5 策略自愈矩阵，包括 Levenshtein 编辑距离 + 元数据约束双重验证的智能列名修正。

### Multi-Agent

基于 DAG 的完整任务分解→调度→聚合闭环。

- Orchestrator 将用户问题分解为子任务 DAG
- Kahn 拓扑排序分层，同层 asyncio.gather 并行执行
- SharedWorkingMemory Sub-Agent 间共享上下文
- AgentMailbox Actor Model 异步消息传递

### Agent Memory

三层记忆架构：

1. **Working Memory**（`AgentWorkingState`）：plan / explored_tables / findings / last_query_sql
2. **Episodic Memory**（`PrioritizedEpisodicMemory`）：基于 TD-error 的优先经验回放，heapq 采样，独立 System Prompt 注入
3. **RAG 知识库**（ChromaDB + Sentence-Transformers）：13 条预置知识 + 自动沉淀 + 语义检索

### CoT 推理可视化

DeepSeek R1 的 `reasoning_content` 思维链通过 SSE `type:reasoning` 事件推送前端，支持展开 / 收起推理链，展示工具调用步骤实时卡片。

---

## 安全体系

### 三层 SQL 沙箱

```
请求 → JWT 认证 → RBAC 角色检查
  Layer 1: 类型检查（仅 SELECT / EXPLAIN / DESCRIBE / SHOW）
  Layer 2: 关键字黑名单（DROP / ALTER / INSERT / CREATE / TRUNCATE ...）
  Layer 3: 注入检测（堆叠查询 / UNION / 盲注 / 文件写入 / 编码绕过，11 条规则）
  只读账号 + 自动 LIMIT + 查询超时
```

| 组件 | 功能 |
|------|------|
| JWT + BCrypt | HS256 签名，8h 过期 |
| RBAC | admin / reader 双角色依赖注入 |
| 审计日志 | 全操作追溯 + CSV 导出 |
| Guardrails | 防幻觉：回答表名 ∈ explored_tables |
| Human-in-the-loop | DROP / TRUNCATE / ALTER 审批队列 |
| 连接池 | DBUtils PooledDB（8 连接 + 自动 ping） |
| 自动备份 | DROP / ALTER 前 mysqldump + 一键恢复 |

---

## 功能

- 自然语言→SQL：自动查元数据生成查询
- 表结构巡检：缺失主键 / 无索引大表 / 命名规范
- SQL 慢查询诊断：EXPLAIN + 智能优化建议
- 测试数据生成：Faker 推断列类型，生成仿真 INSERT
- SQL 编辑器：格式化 + 执行 + EXPLAIN
- 用户管理：创建 / 禁用 / 删改用户和角色

---

## 截屏

| 展示内容 | 路径 |
|---------|------|
| 登录界面 | `screenshots/login.png` |
| 对话主界面 | `screenshots/chat.png` |
| CoT 推理链 | `screenshots/cot.png` |
| 工具调用卡片 | `screenshots/tools.png` |
| 管理后台 | `screenshots/admin.png` |
| 表巡检 | `screenshots/inspect.png` |
| **React 仪表盘** | `screenshots/react.png` |
| 设置页 · 监控入口 | `screenshots/settings.png` |

---

## 项目结构

```
backend/
  agent/                        Agent 算法模块（12 个）
    loop_engine.py              核心算法：TokenBudget / AdaptiveLoop / SelfHealing
    scheduler.py                主循环：SSE 流式对话 / 模块集成
    session_manager.py          会话管理 / 智能裁剪 / TTL
    self_evaluator.py           LLM 自评终止判断
    episodic_memory.py          PER 优先经验回放
    tool_dependency.py          Kahn 拓扑排序 / 并行批次
    orchestrator.py             Multi-Agent 编排 / DAG / SharedMemory
    agent_registry.py           Agent 注册 + 意图路由
    guardrails.py               防幻觉 / 审批队列
    cost_tracker.py             Token 成本追踪
    telemetry.py                OpenTelemetry Tracing
  api/routes.py                 30 个 REST 端点
  auth/                         JWT + RBAC + 用户管理
  security/                     安全沙箱 / 连接池 / 备份
  tools/                        8 个独立工具
  eval/                         静态 + 端到端评估
  rag/                          ChromaDB 知识库
  main.py                       应用入口
  config.py                     配置
  requirements.txt              依赖
frontend/
  src/pages/                    Vue 3 页面（Login / Chat / Settings 等）
  src/react-dashboard/          React 18 系统监控仪表盘（统计卡片/折线图/环形仪表/查询表）
  src/store/auth.js             认证状态管理
  src/config.js                 配置
  index.html / dashboard.html   多入口构建（Vue + React 共存）
  vite.config.js                构建配置（vue + react 插件）
```

---

## 快速开始

```bash
# 后端
cd backend
pip install -r requirements.txt
cp .env.example .env    # 填入 DeepSeek API Key + MySQL 信息
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend
npm install
npm run dev    # http://localhost:5173
```

默认账户：admin / admin123 | 需要 MySQL 8.0+ 和 DeepSeek API Key

---

## 评估

- 20 个测试用例静态评估
- `evaluate_e2e()` 端到端真实 Agent 运行
- Token 成本实时追踪

## 技术栈

Python 3.11+ · FastAPI · Vue 3 · DeepSeek V3 / R1 · ChromaDB · MySQL 8.0 |
OpenAI SDK · Sentence-Transformers · JWT · BCrypt