package com.example.demo.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.StringUtils;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.demo.commom.Result;
import com.example.demo.entity.Book;
import com.example.demo.entity.BookWithUser;
import com.example.demo.mapper.BookMapper;
import com.example.demo.mapper.BookWithUserMapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.interceptor.TransactionAspectSupport;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@RestController
@RequestMapping("/book")
public class BookController {
    @Resource
    BookMapper BookMapper;
    @Resource
    BookWithUserMapper bookWithUserMapper;
    @Resource
    ObjectMapper objectMapper;

    @PostMapping
    public Result<?> save(@RequestBody JsonNode body){
        if (body == null || body.isNull()) {
            return Result.error("-1", "图书信息不能为空");
        }
        JsonNode totalCountNode = body.get("totalCount");
        if (totalCountNode == null || !totalCountNode.isIntegralNumber() || !totalCountNode.canConvertToInt()) {
            return Result.error("-1", "馆藏总数必须为正整数");
        }
        final Book Book;
        try {
            Book = objectMapper.treeToValue(body, Book.class);
        } catch (Exception e) {
            return Result.error("-1", "图书信息格式错误");
        }
        if (Book == null) {
            return Result.error("-1", "图书信息不能为空");
        }
        if (StringUtils.isBlank(Book.getIsbn())) {
            return Result.error("-1", "图书编号不能为空");
        }
        Book.setIsbn(Book.getIsbn().trim());
        if (Book.getTotalCount() == null || Book.getTotalCount() <= 0) {
            return Result.error("-1", "馆藏总数必须为正整数");
        }
        if (body.get("availableCount") != null) {
            return Result.error("-1", "可借数量由系统初始化，不能由客户端提交");
        }
        Book.setBorrownum(0);
        Book.setAvailableCount(Book.getTotalCount());
        Book.setStatus("1");
        try {
            BookMapper.insert(Book);
            return Result.success();
        } catch (Exception e) {
            return Result.error("-1", "图书新增失败，请检查图书编号是否重复");
        }
    }
    @PutMapping
    @Transactional(rollbackFor = Exception.class)
    public  Result<?> update(@RequestBody JsonNode body){
        if (body == null || body.isNull()) {
            return Result.error("-1", "图书信息不能为空");
        }
        JsonNode totalCountNode = body.get("totalCount");
        if (totalCountNode != null && (!totalCountNode.isIntegralNumber() || !totalCountNode.canConvertToInt())) {
            return Result.error("-1", "馆藏总数必须为正整数");
        }
        final Book Book;
        try {
            Book = objectMapper.treeToValue(body, Book.class);
        } catch (Exception e) {
            return Result.error("-1", "图书信息格式错误");
        }
        if (Book == null || Book.getId() == null) {
            return Result.error("-1", "图书ID不能为空");
        }
        if (body.get("availableCount") != null) {
            return Result.error("-1", "可借数量由系统根据馆藏总数和已借出数计算，不能由客户端修改");
        }
        Book dbBook = BookMapper.selectByIdForUpdate(Book.getId());
        if (dbBook == null) {
            return Result.error("-1", "图书不存在");
        }
        if (body.get("isbn") != null && StringUtils.isBlank(Book.getIsbn())) {
            return Result.error("-1", "图书编号不能为空");
        }
        String newIsbn = body.get("isbn") == null ? dbBook.getIsbn() : Book.getIsbn().trim();
        if (!newIsbn.equals(dbBook.getIsbn())) {
            Integer activeBorrowCount = bookWithUserMapper.selectCount(
                    Wrappers.<BookWithUser>lambdaQuery().eq(BookWithUser::getIsbn, dbBook.getIsbn()));
            if (activeBorrowCount != null && activeBorrowCount > 0) {
                return Result.error("-1", "图书存在当前借阅，不能修改图书编号");
            }
        }
        Integer oldTotal = dbBook.getTotalCount();
        Integer oldAvailable = dbBook.getAvailableCount();
        if (oldTotal == null || oldAvailable == null || oldTotal <= 0 || oldAvailable < 0 || oldAvailable > oldTotal) {
            return Result.error("-1", "原库存数据异常，请先修复数据库库存数量");
        }
        Integer newTotal = Book.getTotalCount() == null ? oldTotal : Book.getTotalCount();
        if (newTotal <= 0) {
            return Result.error("-1", "馆藏总数必须为正整数");
        }
        int borrowedCount = oldTotal - oldAvailable;
        if (newTotal < borrowedCount) {
            return Result.error("-1", "馆藏总数不得小于当前已借出数量");
        }

        Book safeUpdate = new Book();
        safeUpdate.setId(Book.getId());
        safeUpdate.setIsbn(newIsbn);
        if (Book.getName() != null) safeUpdate.setName(Book.getName());
        if (Book.getPrice() != null) safeUpdate.setPrice(Book.getPrice());
        if (Book.getAuthor() != null) safeUpdate.setAuthor(Book.getAuthor());
        if (Book.getPublisher() != null) safeUpdate.setPublisher(Book.getPublisher());
        if (Book.getCreateTime() != null) safeUpdate.setCreateTime(Book.getCreateTime());
        safeUpdate.setBorrownum(dbBook.getBorrownum());
        safeUpdate.setTotalCount(newTotal);
        safeUpdate.setAvailableCount(newTotal - borrowedCount);
        safeUpdate.setStatus(safeUpdate.getAvailableCount() > 0 ? "1" : "0");

        try {
            if (BookMapper.updateById(safeUpdate) != 1) {
                return Result.error("-1", "图书不存在或未更新");
            }
            return Result.success();
        } catch (Exception e) {
            return Result.error("-1", "图书更新失败，请检查图书编号是否重复");
        }
    }

    //    批量删除
    @PostMapping("/deleteBatch")
    @Transactional(rollbackFor = Exception.class)
    public  Result<?> deleteBatch(@RequestBody List<Integer> ids){
        if (ids == null || ids.isEmpty()) {
            return Result.error("-1", "请选择要删除的图书");
        }
        if (ids.contains(null)) {
            return Result.error("-1", "图书ID不能为空");
        }
        Set<Integer> uniqueIds = new HashSet<>(ids);
        if (uniqueIds.size() != ids.size()) {
            return Result.error("-1", "批量删除不能包含重复图书ID");
        }
        List<Integer> sortedIds = new ArrayList<>(ids);
        Collections.sort(sortedIds);
        for (Integer id : sortedIds) {
            Book book = BookMapper.selectByIdForUpdate(id);
            if (book == null) {
                return Result.error("-1", "图书不存在");
            }
            if (hasActiveBorrow(book.getIsbn())) {
                return Result.error("-1", "图书存在当前借阅，不能删除");
            }
        }
        if (BookMapper.deleteBatchIds(sortedIds) != sortedIds.size()) {
            TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
            return Result.error("-1", "部分图书删除失败");
        }
        return Result.success();
    }
    @DeleteMapping("/{id}")
    @Transactional(rollbackFor = Exception.class)
    public Result<?> delete(@PathVariable Long id){
        if (id == null || id > Integer.MAX_VALUE) {
            return Result.error("-1", "图书不存在");
        }
        Book book = BookMapper.selectByIdForUpdate(id.intValue());
        if (book == null) {
            return Result.error("-1", "图书不存在");
        }
        if (hasActiveBorrow(book.getIsbn())) {
            return Result.error("-1", "图书存在当前借阅，不能删除");
        }
        if (BookMapper.deleteById(id) < 1) {
            return Result.error("-1", "图书删除失败");
        }
        return Result.success();
    }

    private boolean hasActiveBorrow(String isbn) {
        Integer count = bookWithUserMapper.selectCount(
                Wrappers.<BookWithUser>lambdaQuery().eq(BookWithUser::getIsbn, isbn));
        return count != null && count > 0;
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
