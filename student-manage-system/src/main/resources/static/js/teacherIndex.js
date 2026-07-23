window.onload = function () {
    const loginUserStr = sessionStorage.getItem("loginUser");
    if (!loginUserStr) {
        window.location.href = "/pages/login.html";
        return;
    }
    const teacher = JSON.parse(loginUserStr);

    document.getElementById("username").textContent = `欢迎：${teacher.username}`;
    document.getElementById("teacherClass").textContent = teacher.classId || "未分配班级";

    if (!teacher.classId) {
        alert("您尚未分配班级，无法管理学生");
        document.getElementById("addStudentBtn").disabled = true;
    }

    loadMyClassStudents();

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

    document.getElementById("searchStudentBtn").addEventListener("click", loadMyClassStudents);
    document.getElementById("resetStudentBtn").addEventListener("click", function () {
        ["studentName", "studentMajor", "minScore", "maxScore"].forEach(id => {
            document.getElementById(id).value = "";
        });
        loadMyClassStudents();
    });

    document.getElementById("addStudentBtn").addEventListener("click", function () {
        document.getElementById("studentModalTitle").textContent = "新增本班学生";
        document.getElementById("studentForm").reset();
        document.getElementById("studentId").value = "";
        document.getElementById("className").value = teacher.classId || "";
        document.getElementById("studentModal").style.display = "flex";
    });

    document.querySelector(".close-modal").addEventListener("click", function () {
        document.getElementById("studentModal").style.display = "none";
    });

    document.getElementById("exportStudentBtn").addEventListener("click", function () {
        const name = document.getElementById("studentName").value;
        const major = document.getElementById("studentMajor").value;
        const minScore = document.getElementById("minScore").value;
        const maxScore = document.getElementById("maxScore").value;
        const classId = teacher.classId;
        let url = `/student/batchExport?className=${encodeURIComponent(classId)}`;
        if (name) url += `&name=${encodeURIComponent(name)}`;
        if (major) url += `&major=${encodeURIComponent(major)}`;
        if (minScore) url += `&minScore=${minScore}`;
        if (maxScore) url += `&maxScore=${maxScore}`;
        window.location.href = url;
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
            className: teacher.classId,
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
                    loadMyClassStudents();
                }
            })
            .catch(() => alert("操作异常，请稍后重试"));
    });

    function loadMyClassStudents() {
        const name = document.getElementById("studentName").value;
        const major = document.getElementById("studentMajor").value;
        const minScore = document.getElementById("minScore").value;
        const maxScore = document.getElementById("maxScore").value;
        const classId = teacher.classId;
        let url = `/student/get?className=${encodeURIComponent(classId)}`;
        if (name) url += `&name=${encodeURIComponent(name)}`;
        if (major) url += `&major=${encodeURIComponent(major)}`;
        if (minScore) url += `&minScore=${minScore}`;
        if (maxScore) url += `&maxScore=${maxScore}`;

        fetch(url, { credentials: "include" })
            .then(res => res.json())
            .then(students => {
                const tbody = document.getElementById("studentTableBody");
                tbody.innerHTML = "";
                if (students.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">暂无本班学生数据</td></tr>`;
                    return;
                }
                students.forEach(st => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>${st.studentNo}</td>
                        <td>${st.name}</td>
                        <td>${st.gender}</td>
                        <td>${st.age}</td>
                        <td>${st.major}</td>
                        <td>${st.className}</td>
                        <td>${st.score}</td>
                        <td><button class="edit-btn" onclick='editStudent(${JSON.stringify(st).replace(/"/g, "&quot;")})'>编辑</button></td>
                    `;
                    tbody.appendChild(tr);
                });
            })
            .catch(() => alert("加载学生数据失败，请稍后重试"));
    }

    window.editStudent = function (student) {
        document.getElementById("studentModalTitle").textContent = "编辑本班学生";
        document.getElementById("studentId").value = student.studentId;
        document.getElementById("studentNo").value = student.studentNo;
        document.getElementById("name").value = student.name;
        document.getElementById("gender").value = student.gender;
        document.getElementById("age").value = student.age;
        document.getElementById("major").value = student.major;
        document.getElementById("score").value = student.score;
        document.getElementById("className").value = student.className; // 学生所在班级
        document.getElementById("studentModal").style.display = "flex";
    };
};