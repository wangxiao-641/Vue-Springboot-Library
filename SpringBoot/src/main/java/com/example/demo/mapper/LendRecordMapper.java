package com.example.demo.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.demo.entity.LendRecord;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;


public interface LendRecordMapper extends BaseMapper<LendRecord> {
    @Select("select * from lend_record where reader_id = #{readerId} and isbn = #{isbn} and status = '0' order by lend_time desc limit 1 for update")
    LendRecord selectOpenRecordForUpdate(@Param("readerId") Integer readerId, @Param("isbn") String isbn);
}
