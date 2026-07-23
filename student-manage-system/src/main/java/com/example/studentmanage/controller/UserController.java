package com.example.studentmanage.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.studentmanage.entity.User;
import com.example.studentmanage.service.UserService;

@RestController
public class UserController {

    @Autowired
    private UserService userService;

    // 1. 管理员获取所有教师列表
    @GetMapping("/admin/getAllTeachers")
    public List<User> getAllTeachers() {
        return userService.getAllTeachers();
    }

    // 2. 删除教师（仅管理员）
    @PostMapping("/admin/deleteTeacher")
    public String deleteTeacher(@RequestParam("userId") Integer userId) {
        if (userId == null) {
            return "教师ID不能为空";
        }
        boolean success = userService.deleteTeacher(userId);
        return success ? "删除成功" : "删除失败";
    }

    // 3. 修改教师信息（仅管理员）
    @PostMapping("/admin/updateTeacher")
    public String updateTeacher(@RequestBody User user) {
        if (user.getUserId() == null) {
            return "教师ID不能为空";
        }
        boolean success = userService.updateTeacher(user);
        return success ? "修改成功" : "用户名已存在或修改失败";
    }
    @PostMapping("/admin/addTeacher")
public String addTeacher(@RequestBody User user) {
    // 校验用户名和密码非空
    if (user.getUsername() == null || user.getUsername().isEmpty() || 
        user.getPassword() == null || user.getPassword().isEmpty()) {
        return "用户名和密码不能为空";
    }
    boolean success = userService.addTeacher(user);
    return success ? "新增教师成功" : "用户名已存在，新增失败";
}

}