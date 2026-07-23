<%@ page contentType="text/html;charset=UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <title>涂维兮之神的仓库管理系统</title>
    <style>
        :root {
            --primary: #1a2b3c;
            --secondary: #2c8fd1;
            --accent: #27ae60;
            --card-bg: #ffffff;
            --border: #e0e6ed;
            --text: #2c3e50;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #f5f7fa, #e4e7eb);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .login-container {
            width: 100%;
            max-width: 450px;
        }
        
        .login-card {
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }
        
        .login-header {
            text-align: center;
            padding: 30px 20px;
            background: linear-gradient(to right, var(--primary), #2c3e50);
            color: white;
        }
        
        .login-header h1 {
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        
        .login-body {
            padding: 30px;
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
        
        .role-select {
            display: flex;
            gap: 15px;
            margin: 25px 0;
        }
        
        .role-option {
            flex: 1;
            text-align: center;
            padding: 15px;
            border: 2px solid var(--border);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .role-option.selected {
            border-color: var(--secondary);
            background-color: rgba(44, 143, 209, 0.1);
        }
        
        .btn-login {
            width: 100%;
            padding: 14px;
            background: var(--secondary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-login:hover {
            background: #1c7fc8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(44, 143, 209, 0.2);
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <h1>仓储管理系统</h1>
                <p>请选择您的身份登录</p>
            </div>
            
            <div class="login-body">
                <c:if test="${not empty error}">
                    <div class="error-message">${error}</div>
                </c:if>
                <form action="${pageContext.request.contextPath}/login" method="post">
                    <div class="form-group">
                        <label for="username">账号:</label>
                        <input type="text" id="username" name="username" class="form-control" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">密码:</label>
                        <input type="password" id="password" name="password" class="form-control" required>
                    </div>
                    
                    <div class="role-select">
                        <div class="role-option selected" data-role="customer">
                            <div>客户</div>
                        </div>
                        <div class="role-option" data-role="admin">
                            <div>管理员</div>
                        </div>
                    </div>
                    
                    <input type="hidden" name="role" value="customer">
                    
                    <button type="submit" class="btn-login">登录系统</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        document.querySelectorAll('.role-option').forEach(option => {
            option.addEventListener('click', function() {
                document.querySelectorAll('.role-option').forEach(el => {
                    el.classList.remove('selected');
                });
                this.classList.add('selected');
                document.querySelector('input[name="role"]').value = this.dataset.role;
            });
        });
    </script>
</body>
</html>