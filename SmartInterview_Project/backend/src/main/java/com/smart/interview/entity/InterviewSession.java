package com.smart.interview.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("interview_session")
public class InterviewSession {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String jobRole;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private BigDecimal comprehensiveScore;
    private String radarData;
    private String improvementPlan;
    private Integer status;
}