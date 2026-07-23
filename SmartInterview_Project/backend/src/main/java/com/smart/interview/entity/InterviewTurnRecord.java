package com.smart.interview.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;

@Data
@TableName("interview_turn_record")
public class InterviewTurnRecord {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long sessionId;
    private Integer turnNumber;
    private String questionText;
    private String userAnswerText;
    private String audioUrl;
    private BigDecimal contentScore;
    private BigDecimal expressionScore;
    private BigDecimal nervousness; 
    private BigDecimal confidence; 
    private BigDecimal clarity;

    private String aiFeedback;
}