<%@ page contentType="text/html;charset=UTF-8" %>
<c:set var="ctx" value="${pageContext.request.contextPath}"/>
<!DOCTYPE html>
<html>
<head>
    <title>404 - 页面未找到</title>
</head>
<body>
    <div class="error-container">
        <div class="error-code">404</div>
        <h1>页面未找到</h1>
        <p class="error-message">抱歉，您请求的页面不存在或已被移除</p>
        
        <div class="debug-info">
            <h3>调试信息：</h3>
            <p><strong>请求URI:</strong> ${pageContext.request.requestURI}</p>
            <p><strong>上下文路径:</strong> ${pageContext.request.contextPath}</p>
            <p><strong>请求方法:</strong> ${pageContext.request.method}</p>
            <p><strong>服务器信息:</strong> ${pageContext.servletContext.serverInfo}</p>
        </div>
        
        <a href="${ctx}/orders" class="btn-home">返回订单管理</a>
        <a href="${ctx}/" class="btn-home" style="background: #2ecc71; margin-left: 10px;">返回首页</a>
    </div>
</body>
</html>