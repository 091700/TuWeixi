# 🧊 SmartPantry — 智能冰箱管理系统（Java + Python AI + Vue 3）

基于 Java Spring Boot + Python AI 引擎 + Vue 3 的全栈智能冰箱系统。支持食材管理、AI 新鲜度预测、黑暗料理评分、本地 LLM 零样本食材特征提取（Qwen 2.5-1.5B）。后端 MyBatis-Plus + MySQL，AI 引擎 FastAPI + PyTorch。

---

## 技术架构

```
Vue 3 前端 → Java Spring Boot 后端 → MySQL (smart_pantry)
                                 → Python AI 引擎 (FastAPI + PyTorch)
                                     → Qwen 2.5-1.5B-Instruct 本地 LLM
                                     → 5维风味向量张量计算
```

---

## 核心功能

### 食材入库（Java → AI 联动）

`POST /api/pantry/add` 接收前端传入的食材名称，自动类型判断：
- **旧食材**（`Integer`）：查 `ingredient_dict` 库，直接复用已有记录
- **新食材**（`String`）：调用 AI Engine → `extractIngredientFeatures()` → LLM 零样本分析类别和保鲜期 → 自动写库，实现**认知自我扩充**

入库后调用 AI-1 `predictFreshness()` 预测变质日期，存入 `user_pantry` 表。

### AI 新鲜度预测（PyTorch 全连接网络）

```python
class ShelfLifePredictor(nn.Module):
    # 输入: [cat_id, base_shelf_life, storage_type, temp, initial_status] → 5维张量
    # 输出: 可存放天数 (float)
    nn.Linear(5, 64) → ReLU → nn.Linear(64, 32) → ReLU → nn.Linear(32, 1)
```

`/api/ai/predict_freshness` 接收 5 维特征，通过 64→32→1 三层全连接 + ReLU 激活预测剩余保鲜天数。

### 黑暗料理评分（5维风味向量余弦相似度）

`/api/ai/predict_harmony` 对食材组合的 5 维风味向量 [甜, 咸, 酸, 辣, 异味] 做两两余弦相似度计算 → 归一化为 0-100 分。基础库包含 19 种食材的硬编码风味特征（西红柿 `[4,1,5,0,0]`、鲱鱼罐头 `[0,9,2,0,10]` 等）。

评分文案：
- >80：绝妙搭配
- 55-80：中规中矩
- 35-55：勉强能吃
- 0：严重生化武器警告

### 本地 LLM 零样本特征提取（Qwen 2.5-1.5B）

`/api/ai/extract_features` 接收食材名称，调用本地通义千问 1.5B 模型进行零样本分析：
- `temperature=0.01` 确保输出稳定性
- `max_new_tokens=100` 控制生成长度
- JSON 正则提取 + 错误兜底
- 自动从 MySQL `ingredient_dict` 表获取数据库食材 → 遍历检测缺失特征 → 调用 LLM 补全 → 写入 `flavor_cache.json`

### 食材管理（Vue 3 + Spring Boot CRUD）

| API | 功能 |
|-----|------|
| `GET /api/pantry/my-fridge` | 按变质日期排序查看冰箱食材 |
| `DELETE /api/pantry/consume/{id}` | 食用标记（status=1） |
| `DELETE /api/pantry/discard/{id}` | 丢弃标记（status=2） |
| `GET /api/pantry/dict` | 食材字典库 |

---

## 项目结构

```
SmartPantry/
├── smart-pantry-backend/          Java Spring Boot
│   ├── src/main/java/com/pantry/
│   │   ├── SmartPantryApplication.java          入口
│   │   ├── controller/PantryController.java     161 行，REST API
│   │   ├── service/AiIntegrationService.java    93 行，AI 引擎调用
│   │   ├── entity/                              数据实体
│   │   ├── mapper/                               MyBatis-Plus 映射
│   │   └── resources/application.yml            配置
│   ├── pom.xml                                  Spring Boot 3 + MyBatis-Plus
│   └── mvnw                                     Maven Wrapper
├── smart-pantry-frontend/          Vue 3 前端
│   ├── src/                                     Vue 3 源码
│   ├── package.json / vite.config.js            构建配置
│   └── index.html
└── SmartPantry_Project/ai_engine/   Python AI 引擎
    ├── app.py                                   553 行，FastAPI + PyTorch + Qwen LLM
    ├── flavor_cache.json                         风味知识库持久化
    ├── requirements.txt                          依赖
    └── venv/                                     Python 虚拟环境
```

---

## 快速开始

```bash
# 1. AI 引擎
cd SmartPantry_Project/ai_engine
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5000

# 2. Java 后端
cd smart-pantry-backend
./mvnw spring-boot:run

# 3. Vue 前端
cd smart-pantry-frontend
npm install
npm run dev
```

需要 MySQL 数据库 `smart_pantry` + `ingredient_dict` 和 `user_pantry` 表。

## 技术栈

Java 17 · Spring Boot 3 · MyBatis-Plus · Maven · Python 3.11 · FastAPI · PyTorch · Qwen 2.5-1.5B-Instruct · Vue 3 · Vite · MySQL · pymysql
