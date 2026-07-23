package com.example.studentmanage.entity;

public class User {
    private Integer userId;      // 对应数据库user_id
    private String username;     // 用户名
    private String password;     // 密码
    private String role;         // 角色（admin/teacher）
    private String classId;      // 关联班级ID（教师用）

    // 必须包含所有字段的getter和setter，否则映射失败
    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getClassId() {
        return classId;
    }

    public void setClassId(String classId) {
        this.classId = classId;
    }
}