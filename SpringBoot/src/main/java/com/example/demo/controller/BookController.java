package com.example.demo.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.StringUtils;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.demo.commom.Result;
import com.example.demo.entity.Book;
import com.example.demo.mapper.BookMapper;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

@RestController
@RequestMapping("/book")
public class BookController {
    @Resource
    BookMapper BookMapper;

    @PostMapping
    public Result<?> save(@RequestBody Book Book){
        if(Book.getTotalCount() == null){
            Book.setTotalCount(1);
        }
        if(Book.getAvailableCount() == null){
            Book.setAvailableCount(Book.getTotalCount());
        }
        if(Book.getBorrownum() == null){
            Book.setBorrownum(0);
        }
        Book.setStatus("1");
        BookMapper.insert(Book);
        return Result.success();
    }
    @PutMapping
    public  Result<?> update(@RequestBody Book Book){
        Book dbBook = BookMapper.selectById(Book.getId());
        if(dbBook != null && Book.getTotalCount() != null && !Book.getTotalCount().equals(dbBook.getTotalCount())){
            // 馆藏总数不得小于当前已借出数量
            int borrowedCount = dbBook.getTotalCount() - dbBook.getAvailableCount();
            if(Book.getTotalCount() < borrowedCount){
                return Result.error("-1", "馆藏总数不得小于当前已借出数量");
            }
        }
        // 如果修改了availableCount，校验不小于0
        if(Book.getAvailableCount() != null){
            if(Book.getAvailableCount() < 0){
                return Result.error("-1", "可借数量不足");
            }
            if(Book.getAvailableCount() == 0){
                Book.setStatus("0");
            } else {
                Book.setStatus("1");
            }
        }
        BookMapper.updateById(Book);
        return Result.success();
    }

    //    批量删除
    @PostMapping("/deleteBatch")
    public  Result<?> deleteBatch(@RequestBody List<Integer> ids){
        BookMapper.deleteBatchIds(ids);
        return Result.success();
    }
    @DeleteMapping("/{id}")
    public Result<?> delete(@PathVariable Long id){
        BookMapper.deleteById(id);
        return Result.success();
    }
    @GetMapping
    public Result<?> findPage(@RequestParam(defaultValue = "1") Integer pageNum,
                              @RequestParam(defaultValue = "10") Integer pageSize,
                              @RequestParam(defaultValue = "") String search1,
                              @RequestParam(defaultValue = "") String search2,
                              @RequestParam(defaultValue = "") String search3){
        LambdaQueryWrapper<Book> wrappers = Wrappers.<Book>lambdaQuery();
        if(StringUtils.isNotBlank(search1)){
            wrappers.like(Book::getIsbn,search1);
        }
        if(StringUtils.isNotBlank(search2)){
            wrappers.like(Book::getName,search2);
        }
        if(StringUtils.isNotBlank(search3)){
            wrappers.like(Book::getAuthor,search3);
        }
        Page<Book> BookPage =BookMapper.selectPage(new Page<>(pageNum,pageSize), wrappers);
        return Result.success(BookPage);
    }
}
