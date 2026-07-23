# 🛒 E-Commerce Platform — PHP + MySQL 电商系统

基于 PHP + MySQL 的电商管理系统，支持完整的用户认证、产品管理、购物车、结算、后台管理。纯 LAMP 技术栈，扁平文件结构，无框架依赖。

---

## 功能

### 用户系统

- 注册 / 登录 / 登出（`register.php` / `login.php` / `logout.php`）
- 密码验证与 Session 状态维护
- 购物车数据持久化（Session + MySQL）

### 产品管理

- 产品列表展示 + 分页（`index.php`）
- 产品详情（`products.php`）
- 添加产品到购物车（`add_to_cart.php`）
- 管理员后台 CRUD（`admin.php`）

### 购物车

- 加购 / 数量调整 / 删除（`cart.php`）
- 实时总价计算
- 结算流程（`checkout.php`）
- 订单成功页面（`success.php`）

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `index.php` | 首页，产品瀑布流展示，登录态控制 |
| `login.php` | 用户登录，Session 认证 |
| `register.php` | 用户注册 |
| `logout.php` | 登出，清除 Session |
| `products.php` | 产品详情页 |
| `cart.php` | 购物车管理 |
| `add_to_cart.php` | 加购接口 |
| `checkout.php` | 订单结算提交 |
| `success.php` | 支付成功回执 |
| `admin.php` | 后台管理：产品增删改 |
| `database.php` | MySQL PDO 连接配置 |
| `functions.php` | 公共函数：产品 CRUD、购物车逻辑 |
| `verify_password.php` | 密码验证 |
| `style.css` | 全站样式 |
| `skm.jpg` | 产品示例图片 |

---

## 技术栈

PHP 8 · MySQL · PDO · Session · LAMP