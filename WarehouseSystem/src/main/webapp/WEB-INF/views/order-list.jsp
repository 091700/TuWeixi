<%@ page contentType="text/html;charset=UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<c:set var="ctx" value="${pageContext.request.contextPath}"/>
<!DOCTYPE html>
<html>
<head>
<title>订单管理</title>
<style>
    :root {
        --primary: #1a2b3c;
        --secondary: #2c8fd1;
        --accent: #27ae60;
        --warning: #e67e22;
        --danger: #e74c3c;
        --light: #f8f9fa;
        --dark: #121a24;
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
        transition: all 0.3s ease;
    }
    
    body {
        background-color: #f5f7fa;
        color: var(--text);
        line-height: 1.6;
    }
    
    .container {
        max-width: 1300px;
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
        margin-bottom: 25px;
        border: 1px solid var(--border);
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        border-bottom: 1px solid var(--border);
    }
    
    .order-card {
        background: var(--card-bg);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: var(--shadow);
        margin-bottom: 20px;
        border: 1px solid var(--border);
        transition: transform 0.3s ease;
    }
    
    .order-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
    
    .order-header {
        display: flex;
        justify-content: space-between;
        padding: 20px;
        border-bottom: 1px solid var(--border);
    }
    
    .order-info h3 {
        margin-bottom: 10px;
        font-size: 1.3rem;
        color: var(--primary);
    }
    
    .order-info p {
        margin: 5px 0;
        color: #64748b;
    }
    
    .order-status {
        text-align: right;
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 15px;
        border-radius: 20px;
        font-weight: 500;
        margin-bottom: 10px;
    }
    
    .status-PENDING {
        background-color: #ffedd5;
        color: #f97316;
    }
    
    .status-CONFIRMED {
        background-color: #dcfce7;
        color: #22c55e;
    }
    
    .status-COMPLETED {
        background-color: #dbeafe;
        color: #3b82f6;
    }
    
    .status-CANCELLED {
        background-color: #fee2e2;
        color: #ef4444;
    }
    
    .order-body {
        padding: 20px;
    }
    
    .item-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .item-table th {
        background: #f8fafc;
        padding: 12px 15px;
        text-align: left;
        font-weight: 600;
        color: var(--primary);
        border-bottom: 1px solid var(--border);
    }
    
    .item-table td {
        padding: 12px 15px;
        border-bottom: 1px solid var(--border);
    }
    
    .order-footer {
        padding: 15px 20px;
        text-align: right;
        border-top: 1px solid var(--border);
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--accent);
    }
    
    .no-orders {
        text-align: center;
        padding: 50px 20px;
    }
    
    .no-orders h3 {
        font-size: 1.5rem;
        margin-bottom: 15px;
        color: var(--primary);
    }
    
    .no-orders p {
        color: #64748b;
        margin-bottom: 25px;
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
    
    .modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .modal-content {
        background: white;
        border-radius: 10px;
        width: 600px;
        max-width: 95%;
        box-shadow: var(--shadow);
        animation: modalAppear 0.3s ease-out;
    }
    
    @keyframes modalAppear {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .modal-header {
        padding: 20px;
        border-bottom: 1px solid var(--border);
    }
    
    .modal-body {
        padding: 20px;
        max-height: 60vh;
        overflow-y: auto;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-group label {
        display: block;
        margin-bottom: 8px;
        font-weight: 500;
        color: var(--primary);
    }
    
    .form-control {
        width: 100%;
        padding: 12px 15px;
        border: 1px solid var(--border);
        border-radius: 6px;
        font-size: 1rem;
    }
    
    .form-control:focus {
        outline: none;
        border-color: var(--secondary);
        box-shadow: 0 0 0 3px rgba(44, 143, 209, 0.1);
    }
    
    .order-item {
        display: flex;
        gap: 15px;
        margin-bottom: 15px;
    }
    
    .order-item select, .order-item input {
        flex: 1;
    }
    
    .btn-add-item {
        background: var(--accent);
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 6px;
        cursor: pointer;
        margin-bottom: 20px;
    }
    
    .btn-remove {
        background: var(--danger);
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 6px;
        cursor: pointer;
    }
    
    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 15px;
        padding: 20px;
        border-top: 1px solid var(--border);
    }
    
    .btn-light {
        background: #f1f5f9;
        color: var(--text);
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
            <a href="${ctx}/goods">商品管理</a>
            <a href="${ctx}/warehouses">仓库管理</a>
            <a href="${ctx}/orders" class="active">订单管理</a>
            <a href="http://localhost:8080/warehouse/">首页</a>
        </nav>
    </div>
</header>

<div class="container">
    <div class="card">
        <div class="card-header">
            <h2>订单列表</h2>
            <button class="btn btn-primary" onclick="showOrderForm()">新建订单</button>
        </div>
    </div>

    <c:choose>
    <c:when test="${not empty orders && orders.size() > 0}">
        <c:forEach items="${orders}" var="order">
            <div class="order-card">
                <div class="order-header">
                    <div class="order-info">
                        <h3>订单号: #${order.orderId}</h3>
                        <p><strong>客户:</strong> ${order.customerName}</p>
                        <p><strong>仓库:</strong> ${order.warehouseName}</p>
                        <p><strong>创建时间:</strong>
                        <fmt:formatDate value="${order.createdAt}" pattern="yyyy-MM-dd HH:mm"/>
                        </p>
                    </div>
                    
                    <div class="order-status">
                        <span class="status-badge status-${order.status}">${order.status}</span>
                        <c:if test="${order.status == 'PENDING'}">
                            <button class="btn btn-success" onclick="confirmOrder(${order.orderId})">确认订单</button>
                        </c:if>
                    </div>
                </div>
                
                <div class="order-body">
                    <table class="item-table">
                        <thead>
                            <tr>
                                <th>商品名称</th>
                                <th>单价</th>
                                <th>数量</th>
                                <th>小计</th>
                            </tr>
                        </thead>
                        <tbody>
                            <c:forEach items="${order.items}" var="item">
                                <tr>
                                    <td>${item.goodsName}</td>
                                    <td>¥<fmt:formatNumber value="${item.unitPrice}" pattern="#,##0.00"/></td>
                                    <td>${item.quantity}</td>
                                    <td>¥<fmt:formatNumber value="${item.unitPrice * item.quantity}" pattern="#,##0.00"/></td>
                                </tr>
                            </c:forEach>
                        </tbody>
                    </table>
                </div>
                
                <div class="order-footer">
                    总金额: ¥<fmt:formatNumber value="${order.totalAmount}" pattern="#,##0.00"/>
                </div>
            </div>
        </c:forEach>
    </c:when>
    <c:otherwise>
        <div class="card">
            <div class="no-orders">
                <h3>暂无订单记录</h3>
                <p>点击"新建订单"按钮创建您的第一笔订单</p>
                <button class="btn btn-primary" onclick="showOrderForm()">新建订单</button>
            </div>
        </div>
    </c:otherwise>
    </c:choose>
</div>

<div id="orderModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>创建新订单</h3>
        </div>
        
        <div class="modal-body">
            <div id="errorMessage" style="color: #e53e3e; padding: 10px; display: none;"></div>
            <form id="orderForm" action="${ctx}/orders" method="post">
                <div class="form-group">
                    <label for="customerId">选择客户:</label>
                    <select id="customerId" name="customerId" class="form-control" required>
                        <option value="">-- 请选择客户 --</option>
                        <c:forEach items="${customers}" var="customer">
                            <option value="${customer.id}">${customer.name}</option>
                        </c:forEach>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="warehouseId">选择仓库:</label>
                    <select id="warehouseId" name="warehouseId" class="form-control" required>
                        <option value="">-- 请选择仓库 --</option>
                        <c:forEach items="${warehouses}" var="warehouse">
                            <option value="${warehouse.id}">${warehouse.name}</option>
                        </c:forEach>
                    </select>
                </div>

                <h3 style="margin: 20px 0 15px;">订单商品</h3>
                <div id="itemsContainer">
                    <div class="order-item">
                        <select name="goodsId" class="form-control" required>
                            <option value="">-- 选择商品 --</option>
                            <c:forEach items="${goodsList}" var="goods">
                                <option value="${goods.goodsId}">
                                ${goods.name} (¥<fmt:formatNumber value="${goods.price}" pattern="#,##0.00"/>)
                                </option>
                            </c:forEach>
                        </select>
                        <input type="number" name="quantity" class="form-control" min="1" value="1" required placeholder="数量">
                        <button type="button" class="btn-remove" onclick="removeItem(this)">删除</button>
                    </div>
                </div>

                <button type="button" class="btn btn-success" onclick="addItem()">添加商品</button>
            </form>
        </div>
        
        <div class="form-actions">
            <button type="button" class="btn btn-light" onclick="closeModal()">取消</button>
            <button type="submit" form="orderForm" class="btn btn-primary">提交订单</button>
        </div>
    </div>
</div>

<script>
function showOrderForm() {
    document.getElementById('orderModal').style.display = 'flex';
    document.getElementById('errorMessage').style.display = 'none';
}
function closeModal() {
    document.getElementById('orderModal').style.display = 'none';
}
function addItem() {
    const container = document.getElementById('itemsContainer');
    const newItem = container.children[0].cloneNode(true);
    // 重置新项目的值
    newItem.querySelector('select').selectedIndex = 0;
    newItem.querySelector('input').value = 1;
    container.appendChild(newItem);
}
function removeItem(button) {
    const container = document.getElementById('itemsContainer');
    if (container.children.length > 1) {
        button.closest('.order-item').remove();
    } else {
        showError('订单必须包含至少一个商品');
    }
}
function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 3000);
}

function confirmOrder(orderId) {
    if (confirm('确定要确认订单 #' + orderId + ' 吗？')) {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '<%= request.getContextPath() %>/orders', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    location.reload();
                } else {
                    alert('确认订单失败：' + xhr.statusText);
                }
            }
        };
        const data = 'action=confirm&orderId=' + orderId;
        xhr.send(data);
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('orderModal');
    if (event.target === modal) {
        closeModal();
    }
}

document.getElementById('orderForm').addEventListener('submit', function(event) {
    const items = document.querySelectorAll('#itemsContainer .order-item');
    let isValid = true;
    items.forEach(item => {
        const select = item.querySelector('select');
        const input = item.querySelector('input');
        if (!select.value) {
            showError('请为所有商品项选择商品');
            isValid = false;
        }
        if (!input.value || parseInt(input.value) <= 0) {
            showError('商品数量必须大于0');
            isValid = false;
        }
    });
    if (!isValid) {
        event.preventDefault();
    }
});
</script>
</body>
</html>