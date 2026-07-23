<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<!DOCTYPE html>
<html>
<head>
    <title>支付页面</title>
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
        
        .btn-light {
            background: #f1f5f9;
            color: var(--text);
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
            display: flex;
            justify-content: flex-end;
            gap: 15px;
        }
        
        .payment-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 30px 0;
        }
        
        .qr-code-box {
            text-align: center;
            padding: 20px;
            border: 1px solid var(--border);
            border-radius: 10px;
            background-color: white;
            box-shadow: var(--shadow);
        }
        
        .qr-code-box img {
            max-width: 300px;
            margin-bottom: 15px;
            border-radius: 8px;
        }
        
        .payment-info {
            margin-top: 20px;
            text-align: center;
        }
        
        .payment-info p {
            margin-bottom: 10px;
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
            <a href="javascript:history.back()" class="btn btn-light">返回上一页</a>
            <a href="${pageContext.request.contextPath}/" class="btn btn-light">返回首页</a>
        </nav>
    </div>
</header>

<div class="container">
    <div class="card">
        <div class="card-header">
            <h2>支付订单</h2>
        </div>
        
        <div class="card-body">
            <div class="payment-container">
                <div class="qr-code-box">
                    <h3>扫码支付</h3>
                    <img src="skm.jpg" alt="收款码" style="width: 290px; height: 290px; object-fit: contain; border: 1px solid #eee;">
                    <p>请使用微信或支付宝扫描二维码完成支付</p>
                </div>
            </div>
            
            <div class="payment-info">
                <p>支付方式: 扫码支付</p>
            </div>
            
        </div>
    </div>
</div>
</body>
</html>