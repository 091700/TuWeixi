package com.smart.interview.controller;

import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.smart.interview.entity.InterviewSession;
import com.smart.interview.entity.InterviewTurnRecord;
import com.smart.interview.mapper.InterviewSessionMapper;
import com.smart.interview.mapper.InterviewTurnRecordMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.format.DateTimeFormatter;
import java.util.Collections;
import java.util.List;

/**
 * 仪表盘控制器
 * 处理用户面试历史数据查询，用于前端展示趋势图、能力雷达图和面试记录
 */
@RestController
@RequestMapping("/api/dashboard")
@CrossOrigin(origins = "*") // 允许跨域请求
public class DashboardController {

    @Autowired
    private InterviewSessionMapper sessionMapper; // 面试场次数据访问层
    
    @Autowired
    private InterviewTurnRecordMapper recordMapper; // 面试回合记录数据访问层

    /**
     * 获取指定用户的面试历史数据
     * @param userId 用户ID
     * @return 包含趋势日期、趋势分数、维度分数和历史记录的JSON字符串
     */
    @GetMapping("/history/{userId}")
    public String getHistory(@PathVariable Long userId) {
        // 1. 查询该用户的所有面试场次（按开始时间升序排列，用于趋势图）
        List<InterviewSession> sessions = sessionMapper.selectList(
                new LambdaQueryWrapper<InterviewSession>()
                        .eq(InterviewSession::getUserId, userId)
                        .orderByAsc(InterviewSession::getStartTime)
        );

        // 初始化数据集合
        JSONArray trendDates = new JSONArray(); // 趋势图日期数组
        JSONArray trendScores = new JSONArray(); // 趋势图分数数组
        JSONArray historyList = new JSONArray(); // 面试历史记录列表
        
        // 5个能力维度的分数数组
        JSONArray techScores = new JSONArray(); // 技术深度
        JSONArray logicScores = new JSONArray(); // 逻辑能力
        JSONArray confScores = new JSONArray(); // 自信度
        JSONArray clarityScores = new JSONArray(); // 表达清晰度
        JSONArray relaxScores = new JSONArray(); // 放松度

        // 日期格式化器：月-日 时:分
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM-dd HH:mm");

        for (InterviewSession session : sessions) {
            // 2. 查询该场次的所有面试回合记录
            List<InterviewTurnRecord> turns = recordMapper.selectList(
                    new LambdaQueryWrapper<InterviewTurnRecord>()
                            .eq(InterviewTurnRecord::getSessionId, session.getId())
            );

            // 过滤掉没有问答记录的废弃场次
            if (turns.isEmpty()) continue;

            // 3. 计算该场次的内容分和表达分的平均分
            double totalContent = 0; // 内容总分
            double totalExpression = 0; // 表达总分
            for (InterviewTurnRecord turn : turns) {
                totalContent += turn.getContentScore() != null ? turn.getContentScore().doubleValue() : 0;
                totalExpression += turn.getExpressionScore() != null ? turn.getExpressionScore().doubleValue() : 0;
            }
            
            int turnCount = turns.size();
            double avgContent = totalContent / turnCount; // 平均内容分
            double avgExpression = totalExpression / turnCount; // 平均表达分

            // 将平均分映射到5个能力维度
            int tech = (int) avgContent;
            int logic = avgContent > 0 ? (int) Math.min(100, avgContent + 5) : 0;
            int conf = (int) avgExpression; 
            int clarity = (int) Math.min(100, avgExpression + 5); 
            int relax = (int) Math.min(100, avgExpression + 2); 

            // 计算综合总分
            int totalScore = (tech + logic + conf + clarity + relax) / 5;

            // 格式化日期并添加到趋势数据
            String dateStr = session.getStartTime().format(formatter);
            trendDates.add(dateStr);
            trendScores.add(totalScore);
            
            // 添加各维度分数到对应数组
            techScores.add(tech);
            logicScores.add(logic);
            confScores.add(conf);
            clarityScores.add(clarity);
            relaxScores.add(relax);

            // 构建单条面试历史记录
            JSONObject historyItem = new JSONObject();
            historyItem.set("date", dateStr);
            historyItem.set("role", "software_engineering".equals(session.getJobRole()) ? "软件工程" : "网络安全");
            historyItem.set("score", totalScore);
            historyItem.set("turnCount", turnCount);
            historyItem.set("report", session.getImprovementPlan());
            historyItem.set("sessionId", session.getId());
            historyList.add(historyItem);
        }

        // 反转历史记录，让最新的记录排在最前面
        Collections.reverse(historyList);

        // 4. 组装最终返回的JSON数据
        JSONObject result = new JSONObject();
        result.set("trendDates", trendDates);
        result.set("trendScores", trendScores);
        result.set("dimensions", new JSONObject()
                .set("tech", techScores)
                .set("logic", logicScores)
                .set("conf", confScores)
                .set("clarity", clarityScores)
                .set("relax", relaxScores)
        );
        result.set("historyList", historyList);

        // 返回成功响应
        return JSONUtil.createObj().set("status", "success").set("data", result).toString();
    }
}