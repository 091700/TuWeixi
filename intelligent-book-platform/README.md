# 📚 Intelligent Book Trading Platform — Spring Boot 整合 Elasticsearch + YOLO 视觉搜索

[![Java](https://img.shields.io/badge/Java-17-ED8B00?style=flat&logo=openjdk)](https://java.com)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-3-6DB33F?style=flat&logo=springboot)](https://spring.io)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8-005571?style=flat&logo=elasticsearch)](https://elastic.co)
[![YOLO](https://img.shields.io/badge/YOLOv5-Object_Detection-00FFFF?style=flat)](https://github.com/ultralytics/yolov5)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql)](https://mysql.com)

基于 Spring Boot 3 的智能图书交易平台。集成 Elasticsearch 全文搜索、YOLOv5 以图搜书视觉搜索、Tesseract OCR 图片文字识别、Spring Security 安全认证、JPA 数据持久化。30 个 Java 源码文件，覆盖前端模板、REST API、搜索引擎、计算机视觉、安全配置等完整 Web 开发管线。

---

## 系统架构

```
┌──────────────────────────────────────────────────────────────────────┐
│  Thymeleaf 前端模板                                                  │
│  index.html │ search.html │ book-detail.html │ cart.html │ login    │
├──────────────────────────────────────────────────────────────────────┤
│  Spring Boot 3 后端 — Controller 层                                   │
│  BookController │ SearchController │ VisualSearchController          │
│  OrderController │ AuthController │ Authentication                   │
├──────────────────────────────────────────────────────────────────────┤
│  Service 层                                                          │
│  BookService │ SearchService │ OrderService │ UserService            │
│  YOLOService │ OCRService                                            │
├──────────────────┬────────────────────┬──────────────────────────────┤
│  Repository 层   │ 搜索引擎            │ 视觉引擎                    │
│  BookRepository  │ Elasticsearch      │ YOLOv5 (Python 子进程)       │
│  UserRepository  │ BookSearchRepository│ Tesseract OCR               │
│  OrderRepository │                    │                              │
├──────────────────┴────────────────────┴──────────────────────────────┤
│  MySQL 8.0 │ Elasticsearch 8 │ Python 3.11 (YOLO) │ Tesseract OCR    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 核心功能

### 1. Elasticsearch 全文搜索（SearchService.java）

| 能力 | 实现 |
|------|------|
| 搜索引擎 | Elasticsearch 8.x, REST High-Level Client |
| 索引映射 | `BookSearchRepository` Spring Data Elasticsearch |
| 搜索字段 | 书名、作者、描述、分类、ISBN |
| 搜索类型 | 关键词搜索 / 模糊匹配 / 布尔查询 |
| 结果排序 | 按相关度评分 `_score` 降序 |

### 2. YOLOv5 以图搜书（YOLOService.java + export_yolo_model.py）

**Python 模型导出**（`export_yolo_model.py`）：
- 加载 YOLOv5 PyTorch 模型（`.pt` 权重）
- `torch.onnx.export()` 导出 ONNX 格式

**Java 调用管线**：
- 前端上传图片 → `VisualSearchController`
- 调用 Python 子进程执行 YOLOv5 推理
- 解析输出结果 → 提取检测到的对象标签
- 根据标签查询 Elasticsearch 匹配图书

### 3. OCR 图片文字识别（OCRService.java）

- 集成 Tesseract OCR 引擎
- 上传图书封面图片 → OCR 提取文字
- 识别结果用于 Elasticsearch 搜索关键词
- 覆盖书名、作者、出版社文字识别

### 4. 图书交易系统

| API | 功能 |
|-----|------|
| `GET /books` | 图书列表 & 分页浏览 |
| `GET /books/{id}` | 图书详情 |
| `POST /books` | 发布图书（卖家） |
| `PUT /books/{id}` | 更新图书信息 |
| `DELETE /books/{id}` | 下架图书 |
| `POST /orders` | 创建订单 |
| `GET /orders` | 我的订单 |
| `POST /auth/register` | 用户注册 |
| `POST /auth/login` | 用户登录 |

### 5. 安全体系（SecurityConfig.java）

- Spring Security 表单登录 + HTTP Basic
- 用户角色：普通用户 / 管理员
- CSRF 防护
- Session 会话管理
- 密码 BCrypt 加密

### 6. 配置模块

| 配置 | 说明 |
|------|------|
| `ElasticsearchConfig.java` | ES 客户端连接配置 |
| `SecurityConfig.java` | Spring Security 安全策略 |
| `JpaConfig.java` | JPA + MySQL 数据源配置 |
| `YOLOConfig.java` | YOLO 模型路径 & Python 环境配置 |
| `WebConfig.java` | CORS & 静态资源映射 |

---

## 项目结构

```
intelligent-book-platform/
├── pom.xml                                    Spring Boot 3 + Elasticsearch + JPA
├── src/main/java/com/example/intelligentbookplatform/
│   ├── IntelligentBookTradingPlatformApplication.java    入口
│   ├── config/
│   │   ├── ElasticsearchConfig.java          ES REST 客户端
│   │   ├── SecurityConfig.java               Spring Security
│   │   ├── JpaConfig.java                    JPA + MySQL
│   │   ├── WebConfig.java                    CORS & 资源
│   │   └── YOLOConfig.java                   YOLO 配置
│   ├── controller/
│   │   ├── BookController.java               图书 CRUD
│   │   ├── SearchController.java             搜索 API
│   │   ├── VisualSearchController.java       视觉搜索
│   │   ├── OrderController.java              订单管理
│   │   ├── AuthController.java               登录注册
│   │   └── HomeController.java               首页
│   ├── service/
│   │   ├── BookService.java                  图书业务
│   │   ├── SearchService.java                Elasticsearch 搜索
│   │   ├── OrderService.java                 订单业务
│   │   ├── UserService.java                  用户业务
│   │   ├── YOLOService.java                  YOLOv5 视觉检测
│   │   └── OCRService.java                   Tesseract OCR
│   ├── repository/
│   │   ├── BookRepository.java               JPA 图书
│   │   ├── UserRepository.java               JPA 用户
│   │   ├── OrderRepository.java              JPA 订单
│   │   └── elasticsearch/BookSearchRepository.java  ES 搜索
│   ├── model/
│   │   ├── Book.java                         图书实体
│   │   ├── User.java                         用户实体
│   │   ├── Order.java                        订单实体
│   │   └── OrderItem.java                    订单项实体
│   └── dto/
│       ├── SearchResult.java                 搜索结果 DTO
│       └── VisualSearchRequest.java          视觉搜索请求
├── src/main/resources/application.properties  配置
├── export_yolo_model.py                       YOLOv5 模型导出 (Python)
└── uploads/                                   图片上传目录 (9 张测试图)
```

---

## 快速开始

```bash
# 1. MySQL
mysql -u root -p -e "CREATE DATABASE intelligent_book_platform"

# 2. Elasticsearch
# 下载 https://elastic.co/downloads/elasticsearch → bin/elasticsearch

# 3. 导出 YOLOv5 模型（需要 Python 3.11 + PyTorch）
pip install ultralytics
python export_yolo_model.py    # 生成 onnx 模型

# 4. 启动 Spring Boot
./mvnw spring-boot:run          # http://localhost:8080
```

**环境要求**：MySQL 8.0、Elasticsearch 8.x（默认 localhost:9200）、Java 17、可选 YOLOv5 + Python 3.11

---

## 技术栈

| 层 | 技术 |
|----|------|
| 框架 | Java 17 · Spring Boot 3 · Spring MVC · Spring Data JPA |
| 安全 | Spring Security · BCrypt · Session |
| 搜索引擎 | Elasticsearch 8.x · REST High-Level Client |
| 计算机视觉 | YOLOv5 (ONNX / Python 子进程) · Tesseract OCR |
| 数据库 | MySQL 8.0 · JPA · Hibernate |
| 前端 | Thymeleaf · HTML5 · CSS3 · Bootstrap |
| 构建 | Maven · pom.xml（含 spring-boot-starter-data-elasticsearch） |