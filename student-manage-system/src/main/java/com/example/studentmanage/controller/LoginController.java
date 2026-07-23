package com.example.studentmanage.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.studentmanage.entity.User;
import com.example.studentmanage.service.UserService;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;

@RestController
public class LoginController {
    @Autowired
    private UserService userService;

    @PostMapping("/login")
public Object login(@RequestParam String username,
                    @RequestParam String password,
                    HttpServletRequest request) {
    try {
        if (username == null || username.trim().isEmpty()) {
            return Map.of("error", "用户名不能为空");
        }
        if (password == null || password.trim().isEmpty()) {
            return Map.of("error", "密码不能为空");
        }

        User user = userService.login(username.trim(), password.trim());
        if (user != null) {
            request.getSession(true).setAttribute("loginUser", user);
            // 返回完整用户信息
            Map<String, Object> result = new HashMap<>();
            result.put("userId", user.getUserId());
            result.put("username", user.getUsername());
            result.put("role", user.getRole());
            result.put("classId", user.getClassId() == null ? "" : user.getClassId());
            return result;
        }
        return Map.of("error", "用户名或密码错误");
    } catch (Exception e) {
        e.printStackTrace();
        return Map.of("error", "服务器异常：" + e.getMessage());
    }
}
    @PostMapping("/logout")
    public String logout(HttpServletRequest request) {
        HttpSession session = request.getSession();
        session.invalidate();
        return "success";
    }
}