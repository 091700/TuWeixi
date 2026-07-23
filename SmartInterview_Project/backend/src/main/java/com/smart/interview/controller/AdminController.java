package com.smart.interview.controller;
import com.smart.interview.mapper.InterviewTurnRecordMapper;
import com.smart.interview.entity.InterviewTurnRecord;
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.smart.interview.entity.InterviewSession;
import com.smart.interview.entity.SysUser;
import com.smart.interview.mapper.InterviewSessionMapper;
import com.smart.interview.mapper.SysUserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.format.DateTimeFormatter;
import java.util.List;

@RestController
@RequestMapping("/api/admin")
@CrossOrigin(origins = "*")
public class AdminController {

    @Autowired
    private SysUserMapper sysUserMapper;

    @Autowired
    private InterviewSessionMapper sessionMapper;
    
    @Autowired
    private InterviewTurnRecordMapper turnRecordMapper;

    @GetMapping("/dashboard/stats")
    public String getGlobalStats() {
        // 1. 统计总考生人数 (排除掉 admin 账号)
        long totalStudents = sysUserMapper.selectCount(
                new LambdaQueryWrapper<SysUser>().eq(SysUser::getRole, "student")
        );

        // 2. 统计已完成的面试总场次
        long totalSessions = sessionMapper.selectCount(
                new LambdaQueryWrapper<InterviewSession>().eq(InterviewSession::getStatus, 1)
        );

        // 3. 计算全平台考生的平均分
        List<InterviewSession> allFinishedSessions = sessionMapper.selectList(
                new LambdaQueryWrapper<InterviewSession>().eq(InterviewSession::getStatus, 1)
        );
        double totalScore = 0;
        for (InterviewSession s : allFinishedSessions) {
            if (s.getComprehensiveScore() != null) {
                totalScore += s.getComprehensiveScore().doubleValue();
            }
        }
        int avgScore = allFinishedSessions.isEmpty() ? 0 : (int) (totalScore / allFinishedSessions.size());

        // 4. 获取最近 10 场面试的实时战报
        List<InterviewSession> recentSessions = sessionMapper.selectList(
                new LambdaQueryWrapper<InterviewSession>()
                        .eq(InterviewSession::getStatus, 1)
                        .orderByDesc(InterviewSession::getEndTime)
                        .last("LIMIT 10")
        );

        JSONArray recentList = new JSONArray();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM-dd HH:mm");
        for (InterviewSession s : recentSessions) {
            SysUser user = sysUserMapper.selectById(s.getUserId());
            JSONObject item = new JSONObject();
            item.set("sessionId", s.getId());
            item.set("username", user != null ? user.getUsername() : "未知用户");
            item.set("role", "software_engineering".equals(s.getJobRole()) ? "软件工程" : "网络安全");
            item.set("score", s.getComprehensiveScore());
            item.set("endTime", s.getEndTime() != null ? s.getEndTime().format(formatter) : "");
            recentList.add(item);
        }

        JSONObject data = new JSONObject();
        data.set("totalStudents", totalStudents);
        data.set("totalSessions", totalSessions);
        data.set("avgScore", avgScore);
        data.set("recentSessions", recentList);

        return JSONUtil.createObj().set("status", "success").set("data", data).toString();
    }

    @GetMapping("/session/{sessionId}/details")
    public String getSessionDetails(@PathVariable Long sessionId) {
        // 按照轮次升序，把这场面试所有的问答记录全查出来
        List<InterviewTurnRecord> turns = turnRecordMapper.selectList(
                new LambdaQueryWrapper<InterviewTurnRecord>()
                        .eq(InterviewTurnRecord::getSessionId, sessionId)
                        .orderByAsc(InterviewTurnRecord::getTurnNumber)
        );
        return JSONUtil.createObj().set("status", "success").set("data", turns).toString();
    }
}