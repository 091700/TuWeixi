package com.example.studentmanage.dao;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.example.studentmanage.entity.User;

@Repository
public class UserDao {
    @Autowired
    private JdbcTemplate jdbcTemplate;

    public User findByUsername(String username) {
        String sql = "SELECT user_id AS userId, username, password, role, class_id AS classId FROM user WHERE username = ?";
        try {
            return jdbcTemplate.queryForObject(sql, new BeanPropertyRowMapper<>(User.class), username);
        } catch (Exception e) {
            return null;
        }
    }

    public int addTeacher(User user) {
        String sql = "INSERT INTO user (username, password, role, class_id) VALUES (?, ?, 'teacher', ?)";
        return jdbcTemplate.update(sql, user.getUsername(), user.getPassword(), user.getClassId());
    }

    // 3. 删除教师（管理员用）
    public int deleteTeacher(Integer userId) {
        String sql = "DELETE FROM user WHERE user_id = ? AND role = 'teacher'";
        return jdbcTemplate.update(sql, userId);
    }

    // 4. 修改教师信息（管理员用）
    public int updateTeacher(User user) {
        String sql = "UPDATE user SET username = ?, password = ?, class_id = ? WHERE user_id = ? AND role = 'teacher'";
        return jdbcTemplate.update(sql, user.getUsername(), user.getPassword(), user.getClassId(), user.getUserId());
    }

    // 5. 查询所有教师（管理员用）
    public List<User> findAllTeachers() {
        String sql = "SELECT user_id AS userId, username, password, role, class_id AS classId FROM user WHERE role = 'teacher'";
        return jdbcTemplate.query(sql, new BeanPropertyRowMapper<>(User.class));
    }
}