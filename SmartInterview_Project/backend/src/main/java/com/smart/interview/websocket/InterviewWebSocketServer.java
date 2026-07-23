package com.smart.interview.websocket;

import cn.hutool.core.io.FileUtil;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.smart.interview.entity.InterviewSession;
import com.smart.interview.entity.InterviewTurnRecord;
import com.smart.interview.mapper.InterviewSessionMapper;
import com.smart.interview.mapper.InterviewTurnRecordMapper;
import com.smart.interview.service.AiIntegrationService;
import jakarta.websocket.*;
import jakarta.websocket.server.PathParam;
import jakarta.websocket.server.ServerEndpoint;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.io.File;
import java.math.BigDecimal;
import java.nio.ByteBuffer;
import java.time.LocalDateTime;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 面试WebSocket服务端
 * 处理实时面试交互：连接建立、文本/音频消息接收、AI分析、数据存储和连接关闭
 */
@Slf4j
@Component
@ServerEndpoint("/ws/interview/{userId}/{jobRole}/{difficulty}")
public class InterviewWebSocketServer {

    // 静态注入Spring Bean（WebSocket多例特性所需）
    private static AiIntegrationService aiIntegrationService;
    private static InterviewTurnRecordMapper interviewTurnRecordMapper;
    private static InterviewSessionMapper interviewSessionMapper;

    @Autowired
    public void setAiIntegrationService(AiIntegrationService aiIntegrationService) {
        InterviewWebSocketServer.aiIntegrationService = aiIntegrationService;
    }
    
    @Autowired
    public void setStaticBeans(AiIntegrationService aiIntegrationService, 
                              InterviewTurnRecordMapper interviewTurnRecordMapper,
                              InterviewSessionMapper interviewSessionMapper) {
        InterviewWebSocketServer.aiIntegrationService = aiIntegrationService;
        InterviewWebSocketServer.interviewTurnRecordMapper = interviewTurnRecordMapper;
        InterviewWebSocketServer.interviewSessionMapper = interviewSessionMapper;
    }

    @Autowired
    public void setInterviewTurnRecordMapper(InterviewTurnRecordMapper interviewTurnRecordMapper) {
        InterviewWebSocketServer.interviewTurnRecordMapper = interviewTurnRecordMapper;
    }

    // WebSocket会话池
    private static final ConcurrentHashMap<String, Session> sessionPool = new ConcurrentHashMap<>();

    /**
     * WebSocket连接建立时触发
     * 初始化面试会话，获取或创建面试记录，发送第一个问题
     */
    @OnOpen
    public void onOpen(Session session, 
        @PathParam("userId") String userId, 
        @PathParam("jobRole") String jobRole,
        @PathParam("difficulty") String difficulty) {
        log.info("用户 {} 尝试连接专业: {}", userId, jobRole);
        session.getUserProperties().put("difficulty", difficulty);
        
        long realSessionId;
        // 查询是否存在未完成的面试会话
        LambdaQueryWrapper<InterviewSession> query = new LambdaQueryWrapper<InterviewSession>()
                .eq(InterviewSession::getUserId, userId)
                .eq(InterviewSession::getJobRole, jobRole)
                .eq(InterviewSession::getStatus, 0) 
                .orderByDesc(InterviewSession::getStartTime)
                .last("LIMIT 1"); 
        
        InterviewSession existingSession = interviewSessionMapper.selectOne(query);

        if (existingSession != null) {
            // 复用已有会话
            realSessionId = existingSession.getId();
            log.info("复用已有 Session ID: {}", realSessionId);
            long turnCount = interviewTurnRecordMapper.selectCount(new LambdaQueryWrapper<InterviewTurnRecord>().eq(InterviewTurnRecord::getSessionId, realSessionId));
            session.getUserProperties().put("turnNumber", (int)turnCount);
        } else {
            // 创建新会话
            InterviewSession newSession = new InterviewSession();
            newSession.setUserId(Long.parseLong(userId));
            newSession.setJobRole(jobRole);
            newSession.setStartTime(LocalDateTime.now());
            newSession.setStatus(0);
            interviewSessionMapper.insert(newSession); 
            realSessionId = newSession.getId(); 
            log.info("创建新 Session ID: {}", realSessionId);
            session.getUserProperties().put("turnNumber", 0);
        }
        session.getUserProperties().put("realSessionId", realSessionId);

        // 获取并发送第一个面试题
        String firstQuestion = aiIntegrationService.getRandomQuestion(jobRole, difficulty);
        session.getUserProperties().put("currentQuestion", firstQuestion); 
        sendMessage(session, new JSONObject().set("type", "question").set("content", firstQuestion));
    }
    
    /**
     * 处理文本消息（考生文字回答）
     */
    @OnMessage
    public void onTextMessage(Session session, String message) {
        log.info("收到 WebSocket 文本消息: {}", message);
        try {
            JSONObject json = JSONUtil.parseObj(message);
            String type = json.getStr("type");

            if ("text_answer".equals(type)) {
                String userText = json.getStr("content");
                Long dbSessionId = (Long) session.getUserProperties().get("realSessionId");
                String currentQuestion = (String) session.getUserProperties().getOrDefault("currentQuestion", "系统提问");
                InterviewSession currentSession = interviewSessionMapper.selectById(dbSessionId);

                log.info("用户选择纯文字输入: {}", userText);

                // 初始化面试回合记录
                InterviewTurnRecord record = new InterviewTurnRecord();
                record.setSessionId(dbSessionId);
                record.setQuestionText(currentQuestion);
                record.setUserAnswerText(userText);
                record.setExpressionScore(new BigDecimal(85)); 
                record.setAudioUrl("TEXT_ONLY"); 
                
                int lastScore = (int) session.getUserProperties().getOrDefault("lastScore", 100);
                String difficulty = (String) session.getUserProperties().getOrDefault("difficulty", "medium");
                
                // 异步调用AI进行内容分析
                aiIntegrationService.analyzeContentAsync(userText, currentSession.getJobRole(), currentQuestion, lastScore, difficulty)
                .thenAccept(analysisResult -> {
                        int contentScore = analysisResult.getInt("score", 70);
                        String feedback = analysisResult.getStr("feedback", "回答已记录。");
                        session.getUserProperties().put("lastScore", contentScore);
                        // 获取AI生成的追问
                        String nextQuestion = analysisResult.getStr("next_question", aiIntegrationService.getRandomQuestion(currentSession.getJobRole(), difficulty));

                        record.setContentScore(new BigDecimal(contentScore));
                        record.setAiFeedback(feedback);
                        
                        // 更新回合数
                        int currentTurn = (int) session.getUserProperties().getOrDefault("turnNumber", 0) + 1;
                        session.getUserProperties().put("turnNumber", currentTurn);
                        record.setTurnNumber(currentTurn);
                        interviewTurnRecordMapper.insert(record);
                        
                        // 更新当前问题为新的追问
                        session.getUserProperties().put("currentQuestion", nextQuestion);

                        // 构造反馈消息返回给前端
                        JSONObject reply = new JSONObject();
                        reply.set("type", "feedback");
                        reply.set("user_answer", userText);
                        reply.set("ai_reply", feedback + " 追问一下：" + nextQuestion);
                        reply.set("expression_scores", new JSONObject().set("nervousness", 15).set("confidence", 85).set("clarity", 95));
                        reply.set("content_score", contentScore);

                        sendMessage(session, reply);
                    }).exceptionally(ex -> {
                        log.error("大模型分析文字时崩溃", ex);
                        return null;
                    });
            }
        } catch (Exception e) {
            log.error("处理文本消息异常", e);
        }
    }

    /**
     * 处理二进制消息（考生音频回答）
     */
   @OnMessage
    public void onMessage(ByteBuffer audioData, Session session, @PathParam("jobRole") String jobRole) {
        try {
            byte[] bytes = new byte[audioData.remaining()];
            audioData.get(bytes);
            log.info("收到用户音频流，大小: {} bytes", bytes.length);
            String difficulty = (String) session.getUserProperties().getOrDefault("difficulty", "medium");
            
            // 保存临时音频文件
            File tempAudio = new File(System.getProperty("java.io.tmpdir") + File.separator + session.getId() + "_temp.webm");
            FileUtil.writeBytes(bytes, tempAudio);

            // 发送状态更新
            sendMessage(session, new JSONObject().set("type", "status").set("content", "面试官正在思考..."));

            Long dbSessionId = (Long) session.getUserProperties().get("realSessionId");
            String currentQuestion = (String) session.getUserProperties().getOrDefault("currentQuestion", "系统提问");
            
            // 第一步：异步分析音频
            aiIntegrationService.analyzeAudioAsync(tempAudio).thenAccept(audioResult -> {
                try {
                    String realText = audioResult.getStr("text", "抱歉没听清");
                    JSONObject expressionScores = audioResult.getJSONObject("scores");
                    String audioUrl = audioResult.getStr("audio_url"); 
                    
                    int lastScore = (int) session.getUserProperties().getOrDefault("lastScore", 100);
                    
                    // 第二步：异步分析内容
                    aiIntegrationService.analyzeContentAsync(currentQuestion, realText, jobRole, lastScore, difficulty)
                    .thenAccept(contentResult -> {
                        try {
                            int contentScore = contentResult.getInt("score", 70);
                            String feedback = contentResult.getStr("feedback", "回答已记录。");
                            session.getUserProperties().put("lastScore", contentScore);
                            String nextQuestion = contentResult.getStr("next_question", aiIntegrationService.getRandomQuestion(jobRole, difficulty));
                            session.getUserProperties().put("currentQuestion", nextQuestion);

                            // 构造并发送反馈消息
                            JSONObject reply = new JSONObject();
                            reply.set("type", "feedback");
                            reply.set("user_answer", realText);
                            reply.set("ai_reply", contentResult.getStr("feedback") + " 咱们看下一题：" + nextQuestion);
                            reply.set("expression_scores", expressionScores);
                            reply.set("content_score", contentResult.getInt("score"));
                            sendMessage(session, reply);
                            
                            // 保存面试回合记录
                            InterviewTurnRecord record = new InterviewTurnRecord();
                            record.setSessionId(dbSessionId);

                            int currentTurn = (int) session.getUserProperties().getOrDefault("turnNumber", 0) + 1;
                            session.getUserProperties().put("turnNumber", currentTurn);
                            record.setTurnNumber(currentTurn);
                            
                            record.setAudioUrl(audioUrl); 
                            record.setQuestionText(currentQuestion); 
                            record.setUserAnswerText(realText);
                            record.setContentScore(new BigDecimal(contentResult.getInt("score")));
                            
                            // 计算表达分
                            double conf = expressionScores.getDouble("confidence", 60.0);
                            double cla = expressionScores.getDouble("clarity", 60.0);
                            double nerv = expressionScores.getDouble("nervousness", 60.0);
                            double finalExpr = (conf + cla + (100 - nerv)) / 3.0;
                            record.setExpressionScore(new BigDecimal(finalExpr));

                            record.setNervousness(new BigDecimal(nerv));
                            record.setConfidence(new BigDecimal(conf));
                            record.setClarity(new BigDecimal(cla));
                            
                            record.setAiFeedback(contentResult.getStr("feedback"));
                            interviewTurnRecordMapper.insert(record);
                            log.info("真实问答记录成功入库！音频地址: {}", audioUrl);
                        } catch (Exception e) {
                            log.error("内容处理与发送报错", e);
                        }
                    }); 
                } catch (Exception e) {
                    log.error("音频回调处理报错", e);
                }
            }); 

        } catch (Exception e) { 
            log.error("处理音频消息整体报错", e);
        }
    }

    /**
     * WebSocket连接关闭时触发
     * 保存面试数据，计算总分，异步生成评估报告
     */
    @OnClose
    public void onClose(Session session) { 
        sessionPool.remove(session.getId()); 
        try {
            Long dbSessionId = (Long) session.getUserProperties().get("realSessionId");
            if (dbSessionId != null) {
                InterviewSession existingSession = interviewSessionMapper.selectById(dbSessionId);
                
                if (existingSession != null && existingSession.getStatus() == 0) {
                    existingSession.setStatus(1); // 标记为已完成
                    existingSession.setEndTime(LocalDateTime.now()); // 存入结束时间
                    
                    // 查询该场次所有回合记录
                    java.util.List<InterviewTurnRecord> turns = interviewTurnRecordMapper.selectList(
                            new LambdaQueryWrapper<InterviewTurnRecord>().eq(InterviewTurnRecord::getSessionId, dbSessionId)
                    );
                    
                    if (!turns.isEmpty()) {
                        // 计算平均分
                        double totalContent = 0;
                        double totalExpression = 0;
                        for (InterviewTurnRecord turn : turns) {
                            totalContent += turn.getContentScore() != null ? turn.getContentScore().doubleValue() : 0;
                            totalExpression += turn.getExpressionScore() != null ? turn.getExpressionScore().doubleValue() : 0;
                        }
                        int avgContent = (int) (totalContent / turns.size());
                        int avgExpression = (int) (totalExpression / turns.size());
                        
                        // 映射到5个维度
                        int tech = avgContent;
                        int logic = avgContent > 0 ? Math.min(100, avgContent + 5) : 0;
                        int conf = avgExpression; 
                        int clarity = Math.min(100, avgExpression + 5); 
                        int relax = Math.min(100, avgExpression + 2); 
                        
                        int totalScore = (tech + logic + conf + clarity + relax) / 5;
                        existingSession.setComprehensiveScore(new BigDecimal(totalScore));
                    } else {
                        existingSession.setComprehensiveScore(new BigDecimal(0));
                    }
                    
                    // 1. 先保存基础分数和状态
                    interviewSessionMapper.updateById(existingSession);
                    log.info("面试场次 {} 已结束，开始异步生成结构化报告", dbSessionId);

                    // 2. 异步生成评估报告并更新
                    if (!turns.isEmpty()) {
                        aiIntegrationService.generateInterviewReportAsync(existingSession.getJobRole(), turns)
                            .thenAccept(reportText -> {
                                existingSession.setImprovementPlan(reportText);
                                interviewSessionMapper.updateById(existingSession);
                                log.info("结构化报告已成功生成并落库");
                            });
                    }
                }
            }
        } catch (Exception e) {
            log.error("关闭 WebSocket 存盘时报错", e);
        }
    }
    
    /**
     * WebSocket错误处理
     */
    @OnError
    public void onError(Session session, Throwable error) {
        log.error("WebSocket 错误，sessionId: {}", session.getId(), error);
    }
    
    /**
     * 发送文本消息到客户端
     */
    private void sendMessage(Session session, JSONObject message) {
        try { 
            session.getBasicRemote().sendText(message.toString()); 
        } catch (Exception e) {
            log.error("发送消息失败", e);
        }
    }
}