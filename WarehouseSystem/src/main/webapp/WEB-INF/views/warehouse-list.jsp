<%@ page contentType="text/html;charset=UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>仓库管理</title>
    <style>
        :root {
            --primary: #1a2b3c;
            --secondary: #2c8fd1;
            --accent: #27ae60;
            --danger: #e74c3c;
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
        
        .card-body {
            padding: 20px;
        }
        
        .table-container {
            overflow-x: auto;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            min-width: 600px;
        }
        
        .data-table th {
            background: #f8fafc;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: var(--primary);
            border-bottom: 1px solid var(--border);
        }
        
        .data-table td {
            padding: 15px;
            border-bottom: 1px solid var(--border);
        }
        
        .data-table tr:last-child td {
            border-bottom: none;
        }
        
        .data-table tr:hover {
            background-color: #f8fafc;
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
        
        .btn-danger {
            background: var(--danger);
            color: white;
        }
        
        .btn-light {
            background: #f1f5f9;
            color: var(--text);
        }
        
        .btn-sm {
            padding: 6px 12px;
            font-size: 0.85rem;
        }
        
        .action-buttons {
            display: flex;
            gap: 8px;
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
            width: 450px;
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
        
        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 15px;
            padding: 20px;
            border-top: 1px solid var(--border);
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
            <a href="${pageContext.request.contextPath}/goods">商品管理</a>
            <a href="${pageContext.request.contextPath}/warehouses" class="active">仓库管理</a>
            <a href="${pageContext.request.contextPath}/orders">订单管理</a>
            <a href="http://localhost:8080/warehouse/">首页</a>
        </nav>
    </div>
</header>

<div class="container">
    <div class="card">
        <div class="card-header">
            <h2>仓库列表</h2>
            <button class="btn btn-primary" onclick="showModal('add')">新增仓库</button>
        </div>
        
        <div class="card-body">
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>仓库名称</th>
                            <th>地址</th>
                            <th>面积(m²)</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <c:forEach items="${warehouses}" var="warehouse">
                            <tr>
                                <td>${warehouse.name}</td>
                                <td>${warehouse.address}</td>
                                <td>${warehouse.area}</td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="btn btn-light btn-sm" onclick="showModal('edit', ${warehouse.id})">编辑</button>
                                        <button class="btn btn-danger btn-sm" onclick="deleteWarehouse(${warehouse.id})">删除</button>
                                    </div>
                                </td>
                            </tr>
                        </c:forEach>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<div id="warehouseModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 id="modalTitle">新增仓库</h3>
        </div>
        <form action="${pageContext.request.contextPath}/warehouses" method="post">
            <div class="modal-body">
                <input type="hidden" name="action" value="add">
                <input type="hidden" name="id" value="0">
                
                <div class="form-group">
                    <label>名称:</label>
                    <input type="text" name="name" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label>地址:</label>
                    <input type="text" name="address" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label>面积:</label>
                    <input type="number" step="0.01" name="area" class="form-control" required>
                </div>
            </div>
            
            <div class="form-actions">
                <button type="button" class="btn btn-light" onclick="closeModal()">取消</button>
                <button type="submit" class="btn btn-primary">保存</button>
            </div>
        </form>
    </div>
</div>

<script>
    function showModal(action, id = 0) {
        const modal = document.getElementById('warehouseModal');
        const form = modal.querySelector('form');
        
        if (action === 'add') {
            form.reset();
            form.elements.action.value = 'add';
            form.elements.id.value = '0';
            document.getElementById('modalTitle').textContent = '新增仓库';
        } else {
            fetch(`${pageContext.request.contextPath}/warehouses?action=get&id=${id}`)
                .then(response => response.json())
                .then(data => {
                    form.elements.name.value = data.name;
                    form.elements.address.value = data.address;
                    form.elements.area.value = data.area;
                    form.elements.action.value = 'update';
                    form.elements.id.value = data.id;
                    document.getElementById('modalTitle').textContent = '编辑仓库';
                });
        }
        modal.style.display = 'flex';
    }

    function closeModal() {
        document.getElementById('warehouseModal').style.display = 'none';
    }

    function deleteWarehouse(id) {
        if(confirm('确定删除这个仓库吗？')) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '${pageContext.request.contextPath}/warehouses';
            
            const action = document.createElement('input');
            action.type = 'hidden';
            action.name = 'action';
            action.value = 'delete';
            
            const idInput = document.createElement('input');
            idInput.type = 'hidden';
            idInput.name = 'id';
            idInput.value = id;
            
            form.appendChild(action);
            form.appendChild(idInput);
            document.body.appendChild(form);
            form.submit();
        }
    }

    window.onclick = function(event) {
        const modal = document.getElementById('warehouseModal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    }
</script>
</body>
</html>