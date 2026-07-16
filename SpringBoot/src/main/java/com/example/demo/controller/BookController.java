package com.example.demo.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
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
    public Result<?> save(@RequestBody Book book){
        if (book.getTotal() == null || book.getTotal() <= 0) {
            book.setTotal(1);
        }
        book.setAvailable(book.getTotal());
        book.setBorrownum(0);
        BookMapper.insert(book);
        return Result.success();
    }

    @PutMapping
    public Result<?> update(@RequestBody Book book){
        if (book.getTotal() != null) {
            Book existing = BookMapper.selectById(book.getId());
            if (existing != null && existing.getTotal() != null && existing.getAvailable() != null) {
                int currentlyBorrowed = existing.getTotal() - existing.getAvailable();
                if (book.getTotal() < currentlyBorrowed) {
                    return Result.error("400", "馆藏总数不能小于当前已借出数量(" + currentlyBorrowed + "册)");
                }
                book.setAvailable(book.getTotal() - currentlyBorrowed);
            }
        }
        BookMapper.updateById(book);
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
        Page<Book> BookPage = BookMapper.selectPage(new Page<>(pageNum,pageSize), wrappers);
        return Result.success(BookPage);
    }
}
