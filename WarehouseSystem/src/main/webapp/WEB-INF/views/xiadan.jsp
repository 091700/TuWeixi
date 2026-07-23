<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<!DOCTYPE html>
<html>
<head>
    <title>下单页面</title>
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
            color: var(--text);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1000px;
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
        
        nav {
            display: flex;
            gap: 15px;
        }
        
        nav a {
            color: var(--text);
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 6px;
            font-weight: 500;
        }
        
        nav a:hover, nav a.active {
            background-color: var(--secondary);
            color: white;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: var(--shadow);
            margin-bottom: 30px;
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
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--text);
        }
        
        .form-control {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 1rem;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--secondary);
            box-shadow: 0 0 0 3px rgba(44, 143, 209, 0.1);
        }
        
        .btn {
            padding: 10px 20px;
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
        
        .btn-success {
            background: var(--accent);
            color: white;
        }
        
        .form-row {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .form-col {
            flex: 1;
        }
        
        .form-actions {
            margin-top: 15px;
        }
    </style>
</head>
<body>
<header>
    <div class="header-content">
        <div class="logo">
            <h1>仓储管理系统</h1>
        </div>
        <nav>
<a href="http://localhost:8080/warehouse/" class="active">首页</a>
</nav>
    </div>
</header>

<div class="container">
    <div class="card">
        <div class="card-header">
            <h2>创建订单</h2>
        </div>
        
        <div class="card-body">
            <form action="${pageContext.request.contextPath}/orders" method="post">
                <input type="hidden" name="action" value="create">
                
                <div class="form-row">
                    <div class="form-col">
                        <div class="form-group">
                            <label for="customerId">客户:</label>
                            <select name="customerId" id="customerId" class="form-control">
                                <c:forEach items="${customers}" var="customer">
                                    <option value="${customer.id}">${customer.name}</option>
                                </c:forEach>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-col">
                        <div class="form-group">
                            <label for="warehouseId">仓库:</label>
                            <select name="warehouseId" id="warehouseId" class="form-control">
                                <c:forEach items="${warehouses}" var="warehouse">
                                    <option value="${warehouse.id}">${warehouse.name}</option>
                                </c:forEach>
                            </select>
                        </div>
                    </div>
                </div>

                <h3 style="margin-bottom: 15px;">选择商品</h3>
                
                <div class="form-row">
                    <div class="form-col">
                        <div class="form-group">
                            <label for="goodsId">商品:</label>
                            <select name="goodsId" id="goodsId" class="form-control">
                                <c:forEach items="${goodsList}" var="goods">
                                    <option value="${goods.goodsId}">${goods.name} - 单价: ${goods.price}</option>
                                </c:forEach>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-col">
                        <div class="form-group">
                            <label for="quantity">数量:</label>
                            <input type="number" name="quantity" id="quantity" class="form-control" value="1" min="1">
                        </div>
                    </div>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">提交订单</button>
                    <button id="payButton" class="btn btn-primary">前往付款</button>
                </div>
            </form>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header">
            <h2>注册新客户</h2>
        </div>
        
        <div class="card-body">
            <form action="${pageContext.request.contextPath}/customers" method="post">
                <input type="hidden" name="action" value="create">
                
                <div class="form-row">
                    <div class="form-col">
                        <div class="form-group">
                            <label for="newCustomerName">客户名称:</label>
                            <input type="text" name="name" id="newCustomerName" class="form-control">
                        </div>
                    </div>
                    
                    <div class="form-col">
                        <div class="form-group">
                            <label for="newCustomerContactPerson">联系人:</label>
                            <input type="text" name="contactPerson" id="newCustomerContactPerson" class="form-control">
                        </div>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-col">
                        <div class="form-group">
                            <label for="newCustomerAddress">客户地址:</label>
                            <input type="text" name="address" id="newCustomerAddress" class="form-control">
                        </div>
                    </div>
                    
                    <div class="form-col">
                        <div class="form-group">
                            <label for="newCustomerContactPhone">联系电话:</label>
                            <input type="text" name="contactPhone" id="newCustomerContactPhone" class="form-control">
                        </div>
                    </div>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-success">注册新客户</button>
                </div>
            </form>
        </div>
    </div>
</div>
<script>
        document.getElementById('payButton').addEventListener('click', function() {
            event.preventDefault();
            window.location.href = '/warehouse/fukuan';
        });
    </script>
</body>
</html>