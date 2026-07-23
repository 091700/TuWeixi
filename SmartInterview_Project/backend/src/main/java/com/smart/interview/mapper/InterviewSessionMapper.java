package com.smart.interview.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.smart.interview.entity.InterviewSession;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface InterviewSessionMapper extends BaseMapper<InterviewSession> {
    // 继承 BaseMapper 后，自动拥有针对 interview_session 表的 CRUD 能力
}