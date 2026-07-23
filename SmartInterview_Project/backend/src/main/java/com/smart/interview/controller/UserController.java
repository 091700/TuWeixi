package com.smart.interview.controller;

import cn.hutool.core.util.StrUtil;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.smart.interview.entity.SysUser;
import com.smart.interview.mapper.SysUserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 用户控制器
 * 处理用户注册、登录请求，支持跨域访问
 */
@RestController
@RequestMapping("/api/user")
@CrossOrigin(origins = "*")
public class UserController {

    @Autowired
    private SysUserMapper sysUserMapper; // 用户数据访问层

    // BCrypt 密码加密器
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    /**
     * 用户注册接口
     * @param params 包含username、password、role（可选，默认student）的请求参数
     * @return 注册结果JSON字符串
     */
    @PostMapping("/register")
    public String register(@RequestBody Map<String, String> params) {
        String username = params.get("username");
        String password = params.get("password");
        String role = params.getOrDefault("role", "student");

        // 校验用户名和密码是否为空
        if (StrUtil.hasBlank(username, password)) {
            return JSONUtil.createObj().set("status", "error").set("msg", "用户名或密码不能为空").toString();
        }

        // 1. 检查用户名是否已存在
        if (sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username)) != null) {
            return JSONUtil.createObj().set("status", "error").set("msg", "用户名已存在").toString();
        }

        // 2. 密码加密并保存用户信息
        SysUser user = new SysUser();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        user.setRole(role);
        sysUserMapper.insert(user);

        return JSONUtil.createObj().set("status", "success").set("msg", "注册成功").toString();
    }

    /**
     * 用户登录接口
     * @param params 包含username、password的请求参数
     * @return 登录结果JSON字符串，成功时返回userId、username、role
     */
    @PostMapping("/login")
    public String login(@RequestBody Map<String, String> params) {
        String username = params.get("username");
        String password = params.get("password");

        // 根据用户名查询用户
        SysUser user = sysUserMapper.selectOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
        
        // 3. 校验用户是否存在及密码是否匹配
        if (user == null || !passwordEncoder.matches(password, user.getPassword())) {
            return JSONUtil.createObj().set("status", "error").set("msg", "用户名或密码错误").toString();
        }

        // 4. 返回用户基本信息给前端
        return JSONUtil.createObj().set("status", "success")
                .set("data", JSONUtil.createObj()
                        .set("userId", user.getId())
                        .set("username", user.getUsername())
                        .set("role", user.getRole() != null ? user.getRole() : "student")
                )
                .toString();
    }
}