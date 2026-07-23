// 登录表单提交事件
document.getElementById("loginForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const usernameInput = document.querySelector("input[name='username']");
    const passwordInput = document.querySelector("input[name='password']");
    const errorMsgEl = document.getElementById("errorMsg");
    const submitBtn = this.querySelector("button[type='submit']");

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    errorMsgEl.textContent = "";
    if (!username) {
        errorMsgEl.textContent = "请输入用户名";
        usernameInput.focus();
        return;
    }
    if (!password) {
        errorMsgEl.textContent = "请输入密码";
        passwordInput.focus();
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "登录中...";

    fetch("/login", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    })
    .then(response => {
        submitBtn.disabled = false;
        submitBtn.textContent = "登录";
        if (!response.ok) throw new Error("登录请求失败");
        return response.json();
    })
    .then(result => {
        if (result.error) {
            errorMsgEl.textContent = result.error;
            return;
        }
        // 确保存储完整的用户信息
        sessionStorage.setItem("loginUser", JSON.stringify(result));
        if (result.role === "admin") {
            window.location.href = "/pages/adminIndex.html";
        } else if (result.role === "teacher") {
            window.location.href = "/pages/teacherIndex.html";
        } else {
            errorMsgEl.textContent = "登录失败";
        }
    })
    .catch(error => {
        console.error("登录请求失败：", error);
        errorMsgEl.textContent = "网络错误，请检查连接";
    });
});