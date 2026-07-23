package com.smart.interview.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.smart.interview.entity.InterviewTurnRecord;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface InterviewTurnRecordMapper extends BaseMapper<InterviewTurnRecord> {
    // 继承 BaseMapper 后，自动拥有针对 interview_turn_record 表的 CRUD 能力
}