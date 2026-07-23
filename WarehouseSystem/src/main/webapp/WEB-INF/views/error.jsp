<%@ page isErrorPage="true" %>
<%
    if (exception != null) {
        exception.printStackTrace(new java.io.PrintWriter(out));
    }
%>
<%@ page contentType="text/html;charset=UTF-8" isErrorPage="true" %>
<!DOCTYPE html>
<html>
<head>
    <title>错误页面</title>
</head>
<body>
<div class="container">
    <div class="card error-card">
        <h1>⚠️ 操作出错</h1>
        <p class="error-message">
            ${not empty requestScope['jakarta.servlet.error.message'] 
            ? requestScope['jakarta.servlet.error.message'] 
            : '未知错误'}
        </p>
        <a href="${pageContext.request.contextPath}/goods" class="btn-primary">返回首页</a>
    </div>
</div>
</body>
</html>