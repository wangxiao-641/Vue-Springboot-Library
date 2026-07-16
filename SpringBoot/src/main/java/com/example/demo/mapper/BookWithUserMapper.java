package com.example.demo.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.demo.entity.BookWithUser;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface BookWithUserMapper extends BaseMapper<BookWithUser> {
    @Select("select * from bookwithuser where id = #{readerId} and isbn = #{isbn} limit 1 for update")
    BookWithUser selectByReaderIdAndIsbnForUpdate(@Param("readerId") Integer readerId, @Param("isbn") String isbn);

    @Select("select * from bookwithuser where borrow_id = #{borrowId} limit 1 for update")
    BookWithUser selectByBorrowIdForUpdate(@Param("borrowId") Long borrowId);

    @Select("select * from bookwithuser where id = #{readerId} order by borrow_id for update")
    List<BookWithUser> selectByReaderIdForUpdate(@Param("readerId") Integer readerId);

}
