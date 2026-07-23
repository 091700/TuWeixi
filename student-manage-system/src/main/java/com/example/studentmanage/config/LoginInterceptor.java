package com.example.studentmanage.config;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.springframework.web.servlet.HandlerInterceptor;

import com.example.studentmanage.entity.User;

public class LoginInterceptor implements HandlerInterceptor {

    public boolean preHandle(HttpServletRequest request,
                        HttpServletResponse response,
                        Object handler) throws Exception {

    HttpSession session = request.getSession(false);
    User loginUser = session != null ? (User) session.getAttribute("loginUser") : null;
    System.out.println(">>> URI: " + request.getRequestURI());
    System.out.println(">>> JSESSIONID: " + (session != null ? session.getId() : "无 Session"));
    System.out.println(">>> loginUser: " + (loginUser != null ? loginUser.getUsername() + "/" + loginUser.getRole() : "null"));

    if (loginUser == null) {
        // 异步请求返回 401
        if ("XMLHttpRequest".equals(request.getHeader("X-Requested-With"))) {
            response.setStatus(401);
            return false;
        }
        // 同步请求重定向
        response.sendRedirect("/pages/login.html");
        return false;
    }

    // 管理员权限校验
    if (request.getRequestURI().contains("/admin/") && !"admin".equals(loginUser.getRole())) {
        response.sendRedirect("/pages/403.html");
        return false;
    }
    return true;
}


    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, 
                    org.springframework.web.servlet.ModelAndView modelAndView) throws Exception {
        // 可选实现
    }

    // 整个请求完成后执行
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
    }
}