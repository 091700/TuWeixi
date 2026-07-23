package com.example.studentmanage.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.studentmanage.dao.UserDao;  // 添加这行
import com.example.studentmanage.entity.User;

@Service  // 标记为Service层组件
public class UserService {
    @Autowired
    private UserDao userDao;

    // 1. 用户登录（校验用户名、密码、角色）
    public User login(String username, String password) {
        User user = userDao.findByUsername(username);
        if (user != null) {
            // 打印日志辅助排查（实际项目中可删除）
            System.out.println("查询到用户：" + user.getUsername() + "，角色：" + user.getRole() + "，密码：" + user.getPassword());
            // 严格的字符串比对（避免null导致的问题）
            if (password != null && password.equals(user.getPassword())) {
                return user;
            }
        }
        return null;  // 登录失败
    }

    // 2. 新增教师（仅管理员可调用，校验用户名唯一性）
    public boolean addTeacher(User user) {
        User existUser = userDao.findByUsername(user.getUsername());
        if (existUser != null) {
            return false;  // 用户名已存在
        }
        return userDao.addTeacher(user) > 0;  // 新增成功返回true
    }

    // 3. 删除教师（仅管理员可调用）
    public boolean deleteTeacher(Integer userId) {
        return userDao.deleteTeacher(userId) > 0;
    }

    // 4. 修改教师（仅管理员可调用，校验用户名唯一性）
    public boolean updateTeacher(User user) {
        User existUser = userDao.findByUsername(user.getUsername());
        // 若用户名已存在且不是当前修改的教师，则冲突
        if (existUser != null && !existUser.getUserId().equals(user.getUserId())) {
            return false;
        }
        return userDao.updateTeacher(user) > 0;
    }

    // 5. 查询所有教师（仅管理员可调用）
    public List<User> getAllTeachers() {
        return userDao.findAllTeachers();
    }
}