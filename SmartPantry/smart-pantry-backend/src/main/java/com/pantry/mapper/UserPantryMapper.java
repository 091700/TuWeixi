package com.pantry.mapper;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.pantry.entity.UserPantry;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserPantryMapper extends BaseMapper<UserPantry> {
    @Insert("INSERT INTO user_pantry (user_id, ingredient_id, entry_date, storage_type, current_temp, initial_status, predicted_expire_date) " +
            "VALUES (#{userId}, #{ingredientId}, #{entryDate}, #{storageType}, #{currentTemp}, #{initialStatus}, #{predictedExpireDate})")
    int insert(UserPantry userPantry);
}