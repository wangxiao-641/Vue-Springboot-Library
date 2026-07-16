package com.example.demo.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.demo.entity.User;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

public interface UserMapper extends BaseMapper<User> {
    @Select("select * from user where id = #{id} limit 1 for update")
    User selectByIdForUpdate(@Param("id") Integer id);

}
