<%@ page contentType="text/html;charset=UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>商品入库</title>
    <style>
        :root {
            --primary: #1a2b3c;
            --secondary: #2c8fd1;
            --accent: #27ae60;
            --card-bg: #ffffff;
            --border: #e0e6ed;
            --text: #2c3e50;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        }

        body {
            background-color: #f5f7fa;
            min-height: 100vh;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background-color: white;
            padding: 15px 0;
            box-shadow: var(--shadow);
            margin-bottom: 30px;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1300px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .logo h1 {
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--primary);
        }

        .btn {
            padding: 8px 15px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .btn-primary {
            background: var(--secondary);
            color: white;
        }

        .btn-light {
            background: #f1f5f9;
            color: var(--text);
        }

        .card {
            background: var(--card-bg);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: var(--shadow);
            margin-bottom: 25px;
            border: 1px solid var(--border);
        }

        .card-header {
            padding: 20px;
            border-bottom: 1px solid var(--border);
        }

        .card-body {
            padding: 20px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--text);
        }

        .form-control {
            width: 100%;
            padding: 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 1rem;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--secondary);
            box-shadow: 0 0 0 3px rgba(44, 143, 209, 0.1);
        }

        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 15px;
            margin-top: 20px;
        }
    </style>
</head>

<body>
<header>
    <div class="header-content">
        <div class="logo">
            <h1>商品入库</h1>
        </div>
        <a href="${pageContext.request.contextPath}/goods" class="btn btn-light">返回商品列表</a>
    </div>
</header>

<div class="container">
    <div class="card">
        <div class="card-header">
            <h2>商品入库操作</h2>
        </div>

        <div class="card-body">
        <form action="${pageContext.request.contextPath}/stock-in" method="post">
                <input type="hidden" name="goods_id" value="${param.goods_id}">

                <div class="form-group">
                    <label>选择商品:</label>
                    <select name="goods_id" class="form-control" required>
                        <c:forEach items="${goodsList}" var="goods">
                            <option value="${goods.goodsId}">${goods.name}</option>
                        </c:forEach>
                    </select>
                </div>

                <div class="form-group">
                    <label>选择仓库:</label>
                    <select name="warehouse_id" class="form-control" required>
                        <c:forEach items="${warehouses}" var="warehouse">
                            <option value="${warehouse.id}">${warehouse.name}</option>
                        </c:forEach>
                    </select>
                </div>

                <div class="form-group">
                    <label>选择供应商:</label>
                    <select name="supplier_id" class="form-control" required>
                        <c:forEach items="${suppliers}" var="supplier">
                            <option value="${supplier.id}">${supplier.name}</option>
                        </c:forEach>
                    </select>
                </div>

                <div class="form-group">
                    <label>入库数量:</label>
                    <input type="number" name="quantity" class="form-control" min="1" required placeholder="输入正整数值">
                </div>

                <div class="form-actions">
                    <button type="reset" class="btn btn-light">重置</button>
                    <button type="submit" class="btn btn-primary">确认入库</button>
                </div>
            </form>
        </div>
    </div>
</div>
</body>
</html>