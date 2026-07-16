package com.example.demo.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.demo.entity.BookWithUser;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

public interface BookWithUserMapper extends BaseMapper<BookWithUser> {
    @Select("select * from bookwithuser where id = #{readerId} and isbn = #{isbn} limit 1 for update")
    BookWithUser selectByReaderIdAndIsbnForUpdate(@Param("readerId") Integer readerId, @Param("isbn") String isbn);

}
