package com.example.demo.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.demo.entity.Book;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;


public interface BookMapper extends BaseMapper<Book> {
    @Select("select * from book where isbn = #{isbn} limit 1 for update")
    Book selectByIsbnForUpdate(@Param("isbn") String isbn);
}
