package com.example.studentmanage.service;

import java.util.List;

import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.example.studentmanage.dao.StudentDao;  // 添加这行
import com.example.studentmanage.entity.Student;  // 添加这行
import com.example.studentmanage.util.ExcelUtil;


@Service
public class StudentService {
    @Autowired
    private StudentDao studentDao;

    // 1. 新增学生（校验学号唯一 + 年龄15-30岁）
    public String addStudent(Student student) {
        // 参数非空校验
        if (student.getStudentNo() == null || student.getStudentNo().isEmpty()) {
            return "学号不能为空";
        }
        if (student.getName() == null || student.getName().isEmpty()) {
            return "姓名不能为空";
        }

        // 年龄校验
        if (student.getAge() == null || student.getAge() < 15 || student.getAge() > 30) {
            return "年龄必须在15-30岁之间";
        }

        // 学号唯一性校验
        if (!studentDao.checkStudentNoUnique(student.getStudentNo(), null)) {
            return "学号已存在，请重新输入";
        }

        // 新增操作
        boolean success = studentDao.addStudent(student) > 0;
        return success ? "新增成功" : "新增失败";
    }

    // 2. 删除学生（仅管理员可调用，由Controller控制权限）
    public boolean deleteStudent(Integer studentId) {
        if (studentId == null) {
            return false;
        }
        // 校验学生是否存在
        Student student = studentDao.findById(studentId);
        if (student == null) {
            return false;
        }
        return studentDao.deleteStudent(studentId) > 0;
    }

    // 3. 修改学生（校验学号唯一 + 年龄15-30岁）
    public String updateStudent(Student student) {
        // 参数校验
        if (student.getStudentId() == null) {
            return "学生ID不能为空";
        }
        if (student.getAge() != null && (student.getAge() < 15 || student.getAge() > 30)) {
            return "年龄必须在15-30岁之间";
        }

        // 校验学生是否存在
        Student existStudent = studentDao.findById(student.getStudentId());
        if (existStudent == null) {
            return "学生不存在";
        }

        // 学号唯一性校验（排除自身）
        if (student.getStudentNo() != null && !studentDao.checkStudentNoUnique(student.getStudentNo(), student.getStudentId())) {
            return "学号已存在，请重新输入";
        }

        // 修改操作
        boolean success = studentDao.updateStudent(student) > 0;
        return success ? "修改成功" : "修改失败";
    }

    // 4. 按条件查询学生（区分管理员/教师权限）
    public List<Student> getStudents(String role, String teacherClass, String major, String className, String name, Double minScore, Double maxScore) {
        // 教师仅能查自己班级的学生
        if ("teacher".equals(role)) {
            // 若教师未分配班级，返回空列表
            if (teacherClass == null || teacherClass.isEmpty()) {
                return List.of();
            }
            className = teacherClass; // 强制筛选教师班级
        }
        return studentDao.findStudents(major, className, name, minScore, maxScore);
    }

    // 5. 批量导入学生（Excel）
    public String batchImport(MultipartFile file) {
        System.out.println(">>> batchImport 被调用，文件名：" + file.getOriginalFilename());
        try {
            List<Student> students = ExcelUtil.importExcel(file, Student.class);
            if (students.isEmpty()) {
                return "导入文件无有效数据";
            }

            int successCount = 0;
            for (Student student : students) {
                // 逐个校验并新增
                if (student.getAge() != null && student.getAge() >= 15 && student.getAge() <= 30
                        && student.getStudentNo() != null && !student.getStudentNo().isEmpty()
                        && studentDao.checkStudentNoUnique(student.getStudentNo(), null)) {
                    studentDao.addStudent(student);
                    successCount++;
                }
            }
            return "导入成功：" + successCount + "条，失败：" + (students.size() - successCount) + "条（年龄或学号问题）";
        } catch (Exception e) {
            return "导入失败：" + e.getMessage();
        }
    }

    // 6. 批量导出学生（Excel）
    public void batchExport(HttpServletResponse response, List<Student> students) {
        try {
            if (students == null || students.isEmpty()) {
                response.getWriter().write("无数据可导出");
                return;
            }
            ExcelUtil.exportExcel(response, "学生信息表.xlsx", "学生数据", students, Student.class);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}