package com.example.studentmanage.dao;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.example.studentmanage.entity.Student;

@Repository
public class StudentDao {
    @Autowired
    private JdbcTemplate jdbcTemplate;

    // 1. 新增学生
    public int addStudent(Student student) {
        String sql = "INSERT INTO student (student_no, name, gender, age, major, class, score) " +
                     "VALUES (?, ?, ?, ?, ?, ?, ?)";
        return jdbcTemplate.update(sql, 
                student.getStudentNo(), student.getName(), student.getGender(), 
                student.getAge(), student.getMajor(), student.getClassName(), student.getScore());
    }

    // 2. 删除学生（仅管理员用）
    public int deleteStudent(Integer studentId) {
        String sql = "DELETE FROM student WHERE student_id = ?";
        return jdbcTemplate.update(sql, studentId);
    }

public int updateStudent(Student student) {
    String sql = "UPDATE student SET student_no = ?, name = ?, gender = ?, age = ?, major = ?, `class` = ?, score = ? " +
                 "WHERE student_id = ?";
    return jdbcTemplate.update(sql, 
            student.getStudentNo(), student.getName(), student.getGender(), 
            student.getAge(), student.getMajor(), student.getClassName(), 
            student.getScore(), student.getStudentId());
}

    // 4. 按ID查询学生
    public Student findById(Integer studentId) {
        String sql = "SELECT student_id AS studentId, student_no AS studentNo, name, gender, age, major, class AS className, score, create_time AS createTime " +
                     "FROM student WHERE student_id = ?";
        try {
            return jdbcTemplate.queryForObject(sql, new BeanPropertyRowMapper<>(Student.class), studentId);
        } catch (Exception e) {
            return null;
        }
    }

    // 5. 按条件查询学生（支持管理员跨班级、教师仅本班）
    public List<Student> findStudents(String major, String className, String name, Double minScore, Double maxScore) {
        // 动态拼接SQL
        StringBuilder sql = new StringBuilder("SELECT student_id AS studentId, student_no AS studentNo, name, gender, age, major, `class` AS className, score, create_time AS createTime FROM student WHERE 1=1");

        StringBuilder params = new StringBuilder();
        Object[] paramArr = new Object[0];

        // 专业筛选
        if (major != null && !major.isEmpty()) {
            sql.append(" AND major = ?");
            params.append(major).append(",");
        }
        // 班级筛选（教师仅能查自己班级）
        if (className != null && !className.isEmpty()) {
            sql.append(" AND `class` = ?");
            params.append(className).append(",");
        }
        // 姓名模糊搜索
        if (name != null && !name.isEmpty()) {
            sql.append(" AND name LIKE ?");
            params.append("%").append(name).append("%").append(",");
        }
        // 成绩区间筛选
        if (minScore != null) {
            sql.append(" AND score >= ?");
            params.append(minScore).append(",");
        }
        if (maxScore != null) {
            sql.append(" AND score <= ?");
            params.append(maxScore).append(",");
        }

        // 处理参数数组
        if (params.length() > 0) {
            String[] paramStrs = params.substring(0, params.length() - 1).split(",");
            paramArr = new Object[paramStrs.length];
            for (int i = 0; i < paramStrs.length; i++) {
                try {
                    // 尝试转换为数字（成绩、年龄）
                    paramArr[i] = Double.parseDouble(paramStrs[i]);
                } catch (Exception e) {
                    // 字符串类型（专业、班级、姓名）
                    paramArr[i] = paramStrs[i];
                }
            }
        }

        // 执行查询
        return jdbcTemplate.query(sql.toString(), paramArr, new BeanPropertyRowMapper<>(Student.class));
    }

    // 6. 校验学号唯一性
    public boolean checkStudentNoUnique(String studentNo, Integer studentId) {
        String sql;
        Object[] params;
        if (studentId == null) {
            // 新增：查询是否存在该学号
            sql = "SELECT COUNT(*) FROM student WHERE student_no = ?";
            params = new Object[]{studentNo};
        } else {
            // 修改：排除自身后查询是否存在该学号
            sql = "SELECT COUNT(*) FROM student WHERE student_no = ? AND student_id != ?";
            params = new Object[]{studentNo, studentId};
        }
        Integer count = jdbcTemplate.queryForObject(sql, Integer.class, params);
        return count == 0;  // true=唯一，false=重复
    }
}