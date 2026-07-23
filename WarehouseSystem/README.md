# 📦 WarehouseSystem — Java 仓库管理系统

[![Java](https://img.shields.io/badge/Java-17-ED8B00?style=flat&logo=openjdk)](https://java.com)
[![Spring](https://img.shields.io/badge/Spring_MVC-5-6DB33F?style=flat&logo=spring)](https://spring.io)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql)](https://mysql.com)

基于 Java Spring MVC + JDBC 的仓库管理系统，24 个 Java 源码文件，覆盖商品管理、订单管理、入库/出库、客户/供应商管理、多仓库管理。原生 Servlet + DAO 架构，JSP 前端，MySQL 数据库。

---

## 系统架构

```
前端 (JSP/HTML/CSS/JS)
  │
  ├── Controller 层（10 个）
  │   GoodsController │ OrderController │ WarehouseController
  │   StockInController │ StockOutController │ CustomerController
  │   FukuanController │ XiadanController │ StartController
  │
  ├── DAO 层（7 个）
  │   GoodsDAO │ OrderDAO │ WarehouseDAO │ StockDAO
  │   CustomerDAO │ SupplierDAO │ UserDAO
  │
  ├── Model 层（5 个）
  │   Goods │ Order │ Customer │ Supplier │ Warehouse
  │
  └── Config/Filter/Util
      DBConfig (Druid) │ EncodingFilter │ ErrorHandler
```

## 核心功能

| 模块 | Controller | DAO | 功能 |
|------|-----------|-----|------|
| **商品管理** | `GoodsController` | `GoodsDAO`（4747B） | 商品 CRUD + 搜索 + 库存状态 |
| **订单管理** | `OrderController`（4392B） | `OrderDAO`（8214B） | 下单/取消/查询/状态流转 |
| **入库管理** | `StockInController`（2608B） | `StockDAO` | 入库记录 + 库存更新 |
| **出库管理** | `StockOutController`（2138B） | `StockDAO` | 出库记录 + 库存扣减 |
| **仓库管理** | `WarehouseController`（3496B） | `WarehouseDAO`（3448B） | 多仓库 CRUD + 容量管理 |
| **客户管理** | `CustomerController`（1588B） | `CustomerDAO`（1951B） | 客户信息管理 |
| **供应商管理** | — | `SupplierDAO`（1045B） | 供应商信息管理 |
| **付款管理** | `FukuanController`（582B） | — | 付款记录 |
| **下单** | `XiadanController`（1273B） | `OrderDAO` | 快速下单 |

## 技术栈

Java 17 · Spring MVC · JDBC · Druid · MySQL · JSP · JSTL · Maven