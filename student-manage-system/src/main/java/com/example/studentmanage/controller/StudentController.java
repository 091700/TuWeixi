package com.example.studentmanage.controller;

import java.util.List;

import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.SessionAttribute;
import org.springframework.web.multipart.MultipartFile;

import com.example.studentmanage.entity.Student;
import com.example.studentmanage.entity.User;  // 添加这行
import com.example.studentmanage.service.StudentService;  // 添加这行

@RestController
public class StudentController {
    @Autowired
    private StudentService studentService;

    // 1. 新增学生（管理员/教师均可，教师仅能新增本班）
    @PostMapping("/student/add")
    public String addStudent(@RequestBody Student student, @SessionAttribute("loginUser") User user ) {
        if ("teacher".equals(user.getRole())) {
            // 校验教师是否分配班级
            if (user.getClassId() == null || user.getClassId().isEmpty()) {
                return "教师未分配班级，无法新增学生";
            }
            student.setClassName(user.getClassId());
        }
        return studentService.addStudent(student);
    }

    // 2. 修改学生（管理员/教师均可，教师仅能修改本班）
    @PostMapping("/student/update")
    public String updateStudent(@RequestBody Student student, @SessionAttribute("loginUser") User user) {
        if ("teacher".equals(user.getRole())) {
            if (user.getClassId() == null || user.getClassId().isEmpty()) {
                return "教师未分配班级，无法修改学生";
            }
            student.setClassName(user.getClassId());
        }
        return studentService.updateStudent(student);
    }

    // 3. 删除学生（仅管理员）
    @PostMapping("/admin/student/delete")
    public String deleteStudent(@RequestParam("studentId") Integer studentId) {
        boolean success = studentService.deleteStudent(studentId);
        return success ? "删除成功" : "删除成功";
    }

    // 4. 按条件查询学生（权限由Service控制）
    @GetMapping("/student/get")
public List<Student> getStudents(
        @RequestParam(required = false) String major,
        @RequestParam(required = false) String className,
        @RequestParam(required = false) String name,
        @RequestParam(required = false) Double minScore,
        @RequestParam(required = false) Double maxScore,
        @SessionAttribute("loginUser") User user) {

    // 教师只能查询自己班级的学生
    if ("teacher".equals(user.getRole())) {
        className = user.getClassId(); // 强制过滤本班
    }

    return studentService.getStudents(
            user.getRole(),
            user.getClassId(),
            major,
            className,
            name,
            minScore,
            maxScore
    );
}
    // 5. 批量导入学生（仅管理员）
    @PostMapping("/admin/student/batchImport")
    public String batchImport(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return "请选择导入文件";
        }
        return studentService.batchImport(file);
    }

    // 6. 批量导出学生（管理员/教师均可，教师仅导出本班）
    @GetMapping("/student/batchExport")
    public void batchExport(
            @RequestParam(required = false) String major,
            @RequestParam(required = false) String className,
            @RequestParam(required = false) String name,
            @RequestParam(required = false) Double minScore,
            @RequestParam(required = false) Double maxScore,
            @SessionAttribute("loginUser") User user, 
            HttpServletResponse response) {
        List<Student> students = studentService.getStudents(
                user.getRole(),
                user.getClassId(),
                major,
                className,
                name,
                minScore,
                maxScore
        );
        studentService.batchExport(response, students);
    }
}