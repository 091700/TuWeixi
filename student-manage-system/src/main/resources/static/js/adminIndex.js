window.onload = function () {
    const loginUser = sessionStorage.getItem("loginUser");
    if (!loginUser) {
        window.location.href = "/pages/login.html";
        return;
    }
    const user = JSON.parse(loginUser);
    document.getElementById("username").textContent = `欢迎：${user.username}`;

    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            tabBtns.forEach(b => b.classList.remove("active"));
            this.classList.add("active");
            const tabId = this.getAttribute("data-tab");
            tabContents.forEach(content => content.classList.remove("active"));
            document.getElementById(tabId).classList.add("active");
            if (tabId === "teacher-tab") loadTeacherList();
        });
    });

    document.getElementById("logoutBtn").addEventListener("click", function () {
        fetch("/logout", { method: "POST", credentials: "include" })
            .then(res => res.text())
            .then(data => {
                if (data === "success") {
                    sessionStorage.removeItem("loginUser");
                    window.location.href = "/pages/login.html";
                }
            })
            .catch(() => alert("退出失败，请稍后重试"));
    });

    loadStudentList();

    document.getElementById("searchStudentBtn").addEventListener("click", loadStudentList);
    document.getElementById("resetStudentBtn").addEventListener("click", function () {
        ["studentName", "studentMajor", "studentClass", "minScore", "maxScore"].forEach(id => {
            document.getElementById(id).value = "";
        });
        loadStudentList();
    });

    document.getElementById("addStudentBtn").addEventListener("click", function () {
        document.getElementById("studentModalTitle").textContent = "新增学生";
        document.getElementById("studentForm").reset();
        document.getElementById("studentId").value = "";
        document.getElementById("studentModal").style.display = "flex";
    });

    document.querySelectorAll(".close-modal").forEach(btn => {
        btn.addEventListener("click", function () {
            document.getElementById("studentModal").style.display = "none";
            document.getElementById("teacherModal").style.display = "none";
        });
    });

    document.getElementById("studentForm").addEventListener("submit", function (e) {
        e.preventDefault();
        const student = {
            studentId: document.getElementById("studentId").value || null,
            studentNo: document.getElementById("studentNo").value,
            name: document.getElementById("name").value,
            gender: document.getElementById("gender").value,
            age: parseInt(document.getElementById("age").value),
            major: document.getElementById("major").value,
            className: document.getElementById("className").value,
            score: parseFloat(document.getElementById("score").value)
        };
        const url = student.studentId ? "/student/update" : "/student/add";
        fetch(url, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(student)
        })
            .then(res => res.text())
            .then(data => {
                alert(data);
                if (data.includes("成功")) {
                    document.getElementById("studentModal").style.display = "none";
                    loadStudentList();
                }
            })
            .catch(error => {
                console.error("学生操作失败：", error);
                alert("操作失败，请稍后重试");
            });
    });

const fileInput = document.getElementById("importFile");
fileInput.addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    fetch("/admin/student/batchImport", {
        method: "POST",
        credentials: "include",
        body: formData
    })
    .then(resp => resp.text())
    .then(msg => {
        alert(msg);
        loadStudentList();
        fileInput.value = "";
    })
    .catch(err => {
        console.error("批量导入失败：", err);
        alert("导入请求异常，请稍后重试");
    });
});

document.getElementById("importStudentBtn").addEventListener("click", function () {
    fileInput.click();
});

document.getElementById("exportStudentBtn").addEventListener("click", function () {
    const params = [
        {id: "studentName", param: "name"},
        {id: "studentMajor", param: "major"},
        {id: "studentClass", param: "className"},
        {id: "minScore", param: "minScore"},
        {id: "maxScore", param: "maxScore"}
    ]
    .map(item => {
        const val = document.getElementById(item.id).value;
        return val ? `${item.param}=${encodeURIComponent(val)}` : "";
    })
    .filter(Boolean)
    .join("&");
    const url = `/student/batchExport?${params}`;
    window.location.href = url;
});

function loadStudentList() {
    const params = [
        {id: "studentName", param: "name"},
        {id: "studentMajor", param: "major"},
        {id: "studentClass", param: "className"},
        {id: "minScore", param: "minScore"},
        {id: "maxScore", param: "maxScore"}
    ]
    .map(item => {
        const val = document.getElementById(item.id).value;
        return val ? `${item.param}=${encodeURIComponent(val)}` : "";
    })
    .filter(Boolean)
    .join("&");
    const url = `/student/get?${params}`;
    fetch(url, { credentials: "include" })
        .then(res => res.json())
        .then(students => {
            const tbody = document.getElementById("studentTableBody");
            tbody.innerHTML = "";
            students.forEach(st => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><input type="checkbox" class="student-check" value="${st.studentId}"></td>
                    <td>${st.studentNo}</td>
                    <td>${st.name}</td>
                    <td>${st.gender}</td>
                    <td>${st.age}</td>
                    <td>${st.major}</td>
                    <td>${st.className}</td>
                    <td>${st.score}</td>
                    <td>
                        <button class="edit-btn" onclick='editStudent(${JSON.stringify(st).replace(/"/g, "&quot;")})'>编辑</button>
                        <button class="delete-btn" onclick='deleteSingleStudent(${st.studentId})'>删除</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            document.getElementById("selectAllStudent").onchange = function () {
                document.querySelectorAll(".student-check").forEach(cb => cb.checked = this.checked);
            };
        })
        .catch(() => alert("加载学生数据失败，请稍后重试"));
}

    window.deleteSingleStudent = function (studentId) {
        if (!confirm("确定要删除该学生吗？删除后不可恢复！")) return;
        fetch(`/admin/student/delete?studentId=${studentId}`, {
            method: "POST",
            credentials: "include"
        })
            .then(res => res.text())
            .then(data => {
                if (data === "success") {
                    alert("删除成功！");
                    loadStudentList();
                } else {
                    alert("删除失败，请稍后重试");
                }
            })
            .catch(() => alert("删除请求异常，请稍后重试"));
    };

    document.getElementById("deleteStudentBtn").addEventListener("click", function () {
        const checked = Array.from(document.querySelectorAll(".student-check:checked"));
        if (checked.length === 0) return alert("请先选中要删除的学生！");
        if (!confirm(`确定要删除选中的${checked.length}名学生吗？`)) return;
        let count = 0;
        checked.forEach(cb =>
            fetch(`/admin/student/delete?studentId=${cb.value}`, {
                method: "POST",
                credentials: "include"
            })
                .then(res => res.text())
                .then(data => {
                    if (data === "success") count++;
                    if (count + (checked.length - count) === checked.length) {
                        alert(`批量删除完成：成功${count}条，失败${checked.length - count}条`);
                        loadStudentList();
                    }
                })
        );
    });

    window.editStudent = function (student) {
        document.getElementById("studentModalTitle").textContent = "编辑学生";
        Object.keys(student).forEach(key => {
            const input = document.getElementById(key === "className" ? "className" : key);
            if (input) input.value = student[key] ?? "";
        });
        document.getElementById("studentModal").style.display = "flex";
    };

    function loadTeacherList() {
        fetch("/admin/getAllTeachers", { credentials: "include" })
            .then(res => res.json())
            .then(teachers => {
                const tbody = document.getElementById("teacherTableBody");
                tbody.innerHTML = "";
                teachers.forEach(t => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>${t.userId}</td>
                        <td>${t.username}</td>
                        <td>${t.password}</td>
                        <td>${t.classId || ""}</td>
                        <td>
                            <button class="edit-btn" onclick='editTeacher(${t.userId}, "${t.username}", "${t.password}", "${t.classId || ""}")'>编辑</button>
                            <button class="delete-btn" onclick='deleteTeacher(${t.userId})'>删除</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            })
            .catch(() => alert("加载教师列表失败，请稍后重试"));
    }

    window.editTeacher = function (userId, username, password, classId) {
        document.getElementById("teacherModalTitle").textContent = "编辑教师";
        document.getElementById("teacherId").value = userId;
        document.getElementById("teacherUsername").value = username;
        document.getElementById("teacherPassword").value = password;
        document.getElementById("teacherClassId").value = classId;
        document.getElementById("teacherModal").style.display = "flex";
    };

    window.deleteTeacher = function (userId) {
        if (!confirm("确定要删除该教师账号吗？删除后不可恢复！")) return;
        fetch(`/admin/deleteTeacher?userId=${userId}`, {
            method: "POST",
            credentials: "include"
        })
            .then(res => res.text())
            .then(data => {
                if (data === "success") {
                    alert("删除教师账号成功！");
                    loadTeacherList();
                } else {
                    alert("删除失败，请稍后重试");
                }
            })
            .catch(() => alert("删除请求异常，请稍后重试"));
    };

    document.getElementById("addTeacherBtn").addEventListener("click", function () {
        document.getElementById("teacherModalTitle").textContent = "新增教师";
        document.getElementById("teacherForm").reset();
        document.getElementById("teacherId").value = "";
        document.getElementById("teacherModal").style.display = "flex";
    });

    document.getElementById("teacherForm").addEventListener("submit", function (e) {
        e.preventDefault();
        const teacher = {
            userId: document.getElementById("teacherId").value || null,
            username: document.getElementById("teacherUsername").value,
            password: document.getElementById("teacherPassword").value,
            classId: document.getElementById("teacherClassId").value
        };
        const url = teacher.userId ? "/admin/updateTeacher" : "/admin/addTeacher";
        fetch(url, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(teacher)
        })
            .then(res => res.text())
            .then(data => {
                if (data === "success") {
                    alert(teacher.userId ? "编辑教师成功！" : "新增教师成功！");
                    document.getElementById("teacherModal").style.display = "none";
                    loadTeacherList();
                } else {
                    alert(data || "操作失败，请稍后重试");
                }
            })
            .catch(() => alert("操作请求异常，请稍后重试"));
    });
    // 在 adminIndex.js 中添加表单提交事件监听
document.getElementById("teacherForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const teacher = {
        username: document.getElementById("teacherUsername").value,
        password: document.getElementById("teacherPassword").value,
        classId: document.getElementById("teacherClassId").value  // 关联班级ID
    };
    // 编辑时需要传入教师ID
    const teacherId = document.getElementById("teacherId").value;
    if (teacherId) {
        teacher.userId = parseInt(teacherId);
    }

    const url = teacherId ? "/admin/updateTeacher" : "/admin/addTeacher";
    fetch(url, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(teacher)
    })
    .then(res => res.text())
    .then(data => {
        alert(data);
        if (data.includes("成功")) {
            document.getElementById("teacherModal").style.display = "none";
            loadTeacherList(); // 重新加载教师列表
        }
    })
    .catch(() => alert("操作失败，请重试"));
});

};