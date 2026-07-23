package com.smart.interview.service;

import cn.hutool.core.io.FileUtil;
import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpResponse;
import cn.hutool.http.HttpUtil;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * AI集成服务
 * 负责与Python引擎、DeepSeek大模型交互，处理音频分析、内容打分、题目获取和报告生成
 */
@Slf4j
@Service
public class AiIntegrationService {

    @Value("${ai.python-engine.base-url}")
    private String pythonEngineUrl; // Python引擎基础地址

    @Value("${ai.deepseek.api-key}")
    private String deepseekApiKey; // DeepSeek API密钥

    @Value("${ai.deepseek.url}")
    private String deepseekUrl; // DeepSeek API地址

    /**
     * 异步调用Python端提取声学特征并打分
     * @param audioFile 待分析的音频文件
     * @return 包含分析结果的CompletableFuture，异常时返回错误信息
     */
    public CompletableFuture<JSONObject> analyzeAudioAsync(File audioFile) {
        return CompletableFuture.supplyAsync(() -> {
            log.info("开始请求 Python 音频分析接口, 文件: {}", audioFile.getName());
            try (HttpResponse response = HttpRequest.post(pythonEngineUrl + "/audio")
                    .form("audio_file", audioFile)
                    .timeout(20000) // 20秒超时兜底，防止Python假死
                    .execute()) {
                
                if (response.isOk()) {
                    return JSONUtil.parseObj(response.body()).getJSONObject("data");
                } else {
                    log.error("Python 音频分析接口报错: {}", response.body());
                    return new JSONObject().set("error", "音频分析失败");
                }
            } catch (Exception e) {
                log.error("请求 Python 音频模型严重异常", e);
                return new JSONObject().set("error", e.getMessage());
            } finally {
                // 清理Java端临时文件
                FileUtil.del(audioFile);
            }
        });
    }
    
    /**
     * 获取随机面试题目
     * @param jobRole 目标岗位
     * @param difficulty 难度等级
     * @return 随机题目，获取失败时返回默认题目
     */
    public String getRandomQuestion(String jobRole, String difficulty) {
        try {
            String url = pythonEngineUrl.replace("/analyze", "/question/random") 
                     + "?job_role=" + jobRole + "&difficulty=" + difficulty;
            String result = HttpUtil.get(url, 5000);
            return JSONUtil.parseObj(result).getStr("data");
        } catch (Exception e) {
            log.error("获取题目失败", e);
            return "请简单介绍一下你的专业背景。"; 
        }
    }

    /**
     * 异步调用Python RAG检索 + DeepSeek大模型打分与智能追问
     * @param currentQuestion 当前面试题
     * @param userAnswer 考生回答
     * @param jobRole 目标岗位
     * @param lastScore 上一题得分
     * @param difficulty 难度等级
     * @return 包含打分、点评和追问的CompletableFuture
     */
   public CompletableFuture<JSONObject> analyzeContentAsync(String currentQuestion, String userAnswer, String jobRole, int lastScore, String difficulty) {
        return CompletableFuture.supplyAsync(() -> {
            log.info("开始进行 RAG 检索与大模型内容分析...");
            try {
                // 1. 请求Python RAG接口获取标准答案
                String ragResultBody = HttpUtil.post(pythonEngineUrl + "/content", 
                        Map.of("question", currentQuestion, "user_answer", userAnswer, "job_role", jobRole));
                JSONObject ragData = JSONUtil.parseObj(ragResultBody).getJSONObject("data");
                String instruction = ragData.getStr("instruction");
                String reference = ragData.getStr("rag_reference");
                
                // 根据上一题得分设置面试官风格
                String pressurePrompt = "";
                if (lastScore > 0 && lastScore < 60) {
                    pressurePrompt = "【⚠️ 极度严厉模式】：该面试者上一题回答得很差，请你现在扮演极度严苛、不留情面的技术总监！点评要一针见血甚至带有轻微的质疑。追问必须深挖底层原理，给他极强的压迫感！";
                } else if (lastScore >= 85) {
                    pressurePrompt = "【🚀 拔高挑战模式】：该面试者水平不错。请给予简短肯定后，立刻抛出一个极具挑战性的高并发场景题或底层源码问题，探底他的技术极限！";
                } else {
                    pressurePrompt = "【平稳模式】：请保持专业、客观的面试官态度进行点评和追问。";
                }

                // 2. 组装Prompt，要求生成打分、点评和追问
                String diffText = "简单".equals(difficulty) ? "初级入门" : "资深/专家级";
                String prompt = "..." + "当前面试难度设定为：" + diffText + "...";
                String diffPrompt = "medium".equals(difficulty) ? "普通难度" : 
                                "easy".equals(difficulty) ? "简单入门难度" : "极客地狱难度";
                JSONObject deepseekPayload = new JSONObject();
                deepseekPayload.set("model", "deepseek-chat");
                String systemPrompt = instruction + " 参考标准知识点: " + reference + "。" +
                        "请扮演专业的面试官。你需要做三件事：1.给当前回答打分(0-100)；2.给出一句精简的点评；3.提出一个【深度追问】。" +
                        "【打分标准】：如果面试者回答出了核心技术点或逻辑大致正确，请大方给予 85 分以上的高分！如果回答优秀可以回答90分以上高分，用户只要回答大致正确就应该多高分。而且由于用户是语音转文字，用户难免语音识别有问题，所以在用户出现错别字的时候，请忽视错别字错误。" +
                        "请严格且仅返回纯 JSON 格式，不要包含任何 Markdown 标记，例如：{\"score\": 88, \"feedback\": \"回答准确。\", \"next_question\": \"那你觉得如何优化？\"}";
                
                deepseekPayload.set("messages", new Object[]{
                        Map.of("role", "system", "content", systemPrompt),
                        Map.of("role", "user", "content", "面试者的回答是：" + userAnswer)
                });
                deepseekPayload.set("response_format", Map.of("type", "json_object")); // 强制返回JSON

                HttpResponse dsResponse = HttpRequest.post(deepseekUrl)
                        .header("Authorization", "Bearer " + deepseekApiKey)
                        .body(deepseekPayload.toString())
                        .timeout(30000)
                        .execute();

                if (dsResponse.isOk()) {
                    String dsContent = JSONUtil.parseObj(dsResponse.body())
                            .getJSONArray("choices").getJSONObject(0)
                            .getJSONObject("message").getStr("content");
                            dsContent = dsContent.replace("```json", "").replace("```", "").trim();
                    JSONObject result = JSONUtil.parseObj(dsContent);
                    
                    // 若未生成追问，补充随机题目
                    if (!result.containsKey("next_question")) {
                        result.set("next_question", getRandomQuestion(jobRole, difficulty)); 
                    }
                    return result;
                } else {
                    log.error("DeepSeek API 报错: {}", dsResponse.body());
                    return new JSONObject().set("score", 60).set("feedback", "AI 思考超时，请继续下一题。").set("next_question", getRandomQuestion(jobRole, difficulty));
                }
            } catch (Exception e) {
                log.error("内容分析流水线异常", e);
                return new JSONObject().set("score", 60).set("feedback", "系统评判异常。").set("next_question", getRandomQuestion(jobRole, difficulty));
            }
        });
    }

    /**
     * 异步生成综合面试评估报告
     * @param jobRole 目标岗位
     * @param turns 面试回合记录列表
     * @return 包含评估报告的CompletableFuture
     */
    public CompletableFuture<String> generateInterviewReportAsync(String jobRole, java.util.List<com.smart.interview.entity.InterviewTurnRecord> turns) {
        return CompletableFuture.supplyAsync(() -> {
            if (turns == null || turns.isEmpty()) return "暂无面试数据，无法生成报告。";
            try {
                // 1. 拼接完整对话历史
                StringBuilder history = new StringBuilder();
                for (int i = 0; i < turns.size(); i++) {
                    history.append("问题").append(i + 1).append(": ").append(turns.get(i).getQuestionText()).append("\n");
                    history.append("回答: ").append(turns.get(i).getUserAnswerText()).append("\n\n");
                }

                // 2. 编写强指令Prompt，要求Markdown格式
                String prompt = "你是一位资深 " + jobRole + " 面试官。请根据以下完整的面试记录，给出客观、专业的结构化评估报告。\n" 
                    + history.toString() +
                    "\n【核心任务】：要求必须严格包含以下四个标题，并且严格使用 Markdown 格式排版。\n" +
                    "### 🌟 核心亮点\n" +
                    "### ⚠️ 存在不足\n" +
                    "### 🎯 改进计划\n" +
                    "### 📚 专属学习加油包\n" +
                    "【输出约束】：在『专属学习加油包』部分，你必须根据该面试者的具体薄弱环节，精准推荐 3-4 个学习资源。推荐的书籍、官方文档或开源项目名称必须严格使用书名号包围（例如：《深入理解Java虚拟机》）；推荐复习的核心技术概念必须严格使用方括号包围（例如：[Redis 缓存穿透]）。\n" +
                    "语言要专业中肯，直击要害，拒绝假大空。";

                JSONObject payload = new JSONObject();
                payload.set("model", "deepseek-chat");
                payload.set("messages", new Object[]{
                        Map.of("role", "system", "content", "你负责出具严格的面试评估总结报告。"),
                        Map.of("role", "user", "content", prompt)
                });

                // 3. 发起请求，报告生成超时设为60秒
                HttpResponse response = HttpRequest.post(deepseekUrl)
                        .header("Authorization", "Bearer " + deepseekApiKey)
                        .body(payload.toString())
                        .timeout(60000)
                        .execute();

                if (response.isOk()) {
                    return JSONUtil.parseObj(response.body())
                            .getJSONArray("choices").getJSONObject(0)
                            .getJSONObject("message").getStr("content");
                } else {
                    log.error("大模型生成报告失败: {}", response.body());
                    return "大模型生成报告异常，请稍后再试。";
                }
            } catch (Exception e) {
                log.error("报告生成流水线报错", e);
                return "系统异常，报告生成失败。";
            }
        });
    }
}