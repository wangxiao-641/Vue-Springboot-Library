package com.example.demo.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.example.demo.commom.Result;
import com.example.demo.entity.Book;
import com.example.demo.entity.BookWithUser;
import com.example.demo.entity.LendRecord;
import com.example.demo.entity.User;
import com.example.demo.mapper.BookMapper;
import com.example.demo.mapper.BookWithUserMapper;
import com.example.demo.mapper.LendRecordMapper;
import com.example.demo.mapper.UserMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;

@Service
public class BorrowService {

    @Resource
    BookMapper bookMapper;

    @Resource
    LendRecordMapper lendRecordMapper;

    @Resource
    BookWithUserMapper bookWithUserMapper;

    @Resource
    UserMapper userMapper;

    @Transactional
    public Result<?> borrow(Integer readerId, String isbn) {
        // 1. 查找图书
        Book book = bookMapper.selectOne(Wrappers.<Book>lambdaQuery().eq(Book::getIsbn, isbn));
        if (book == null) {
            return Result.error("-1", "图书不存在");
        }

        // 2. 检查是否已借过同一本书且未归还
        Integer alreadyBorrowed = bookWithUserMapper.selectCount(
                Wrappers.<BookWithUser>lambdaQuery()
                        .eq(BookWithUser::getId, readerId)
                        .eq(BookWithUser::getIsbn, isbn));
        if (alreadyBorrowed != null && alreadyBorrowed > 0) {
            return Result.error("-1", "您已借阅该书，不可重复借阅");
        }

        // 3. 检查借阅数量上限
        Integer currentBorrowed = bookWithUserMapper.selectCount(
                Wrappers.<BookWithUser>lambdaQuery().eq(BookWithUser::getId, readerId));
        if (currentBorrowed != null && currentBorrowed >= 5) {
            return Result.error("-1", "您已达到最大借阅数量(5本)");
        }

        // 4. 检查是否有逾期未还的书
        List<BookWithUser> borrowedList = bookWithUserMapper.selectList(
                Wrappers.<BookWithUser>lambdaQuery().eq(BookWithUser::getId, readerId));
        Date now = new Date();
        for (BookWithUser bw : borrowedList) {
            if (bw.getDeadtime() != null && bw.getDeadtime().before(now)) {
                return Result.error("-1", "您有逾期未还图书，请先归还");
            }
        }

        // 5. 原子更新库存
        UpdateWrapper<Book> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("isbn", isbn);
        updateWrapper.gt("available", 0);
        updateWrapper.setSql("available = available - 1, borrownum = borrownum + 1");
        int rows = bookMapper.update(null, updateWrapper);
        if (rows == 0) {
            return Result.error("-1", "该图书已全部借出，暂无可借副本");
        }

        // 6. 获取更新后的图书信息（获取新的 borrownum）
        Book updatedBook = bookMapper.selectOne(Wrappers.<Book>lambdaQuery().eq(Book::getIsbn, isbn));
        Integer borrownum = updatedBook.getBorrownum();

        // 7. 获取读者昵称
        User reader = userMapper.selectById(readerId);
        String nickName = reader != null ? reader.getNickName() : "";

        // 8. 计算应还日期（30天后）
        long thirtyDaysMs = 30L * 24 * 60 * 60 * 1000;
        Date deadtime = new Date(now.getTime() + thirtyDaysMs);

        // 9. 插入借阅历史记录
        LendRecord lendRecord = new LendRecord();
        lendRecord.setReaderId(readerId);
        lendRecord.setIsbn(isbn);
        lendRecord.setBookname(updatedBook.getName());
        lendRecord.setLendTime(now);
        lendRecord.setStatus("0");
        lendRecord.setBorrownum(borrownum);
        lendRecordMapper.insert(lendRecord);

        // 10. 插入当前借阅记录
        BookWithUser bookWithUser = new BookWithUser();
        bookWithUser.setId(readerId);
        bookWithUser.setIsbn(isbn);
        bookWithUser.setBookName(updatedBook.getName());
        bookWithUser.setNickName(nickName);
        bookWithUser.setLendtime(now);
        bookWithUser.setDeadtime(deadtime);
        bookWithUser.setProlong(1);
        bookWithUserMapper.insert(bookWithUser);

        return Result.success();
    }

    @Transactional
    public Result<?> returnBook(Integer readerId, String isbn) {
        // 1. 查找图书
        Book book = bookMapper.selectOne(Wrappers.<Book>lambdaQuery().eq(Book::getIsbn, isbn));
        if (book == null) {
            return Result.error("-1", "图书不存在");
        }

        // 2. 检查该读者是否借了这本书
        BookWithUser existing = bookWithUserMapper.selectOne(
                Wrappers.<BookWithUser>lambdaQuery()
                        .eq(BookWithUser::getId, readerId)
                        .eq(BookWithUser::getIsbn, isbn));
        if (existing == null) {
            return Result.error("-1", "您未借阅该书，无法归还");
        }

        // 3. 原子更新库存：available + 1（防重复归还）
        UpdateWrapper<Book> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("isbn", isbn);
        updateWrapper.apply("available < total");
        updateWrapper.setSql("available = available + 1");
        int rows = bookMapper.update(null, updateWrapper);
        if (rows == 0) {
            return Result.error("-1", "还书失败：可借数量已达馆藏总数");
        }

        // 4. 更新借阅历史记录：通过 readerId + isbn + status=0 找到最新借阅记录，更新为已归还
        Date now = new Date();
        List<LendRecord> records = lendRecordMapper.selectList(
                Wrappers.<LendRecord>lambdaQuery()
                        .eq(LendRecord::getReaderId, readerId)
                        .eq(LendRecord::getIsbn, isbn)
                        .eq(LendRecord::getStatus, "0")
                        .orderByDesc(LendRecord::getLendTime));
        if (records != null && !records.isEmpty()) {
            LendRecord target = records.get(0);
            LendRecord updateLendRecord = new LendRecord();
            updateLendRecord.setReturnTime(now);
            updateLendRecord.setStatus("1");
            com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper<LendRecord> lendWrapper =
                    new com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper<>();
            lendWrapper.eq("reader_id", target.getReaderId());
            lendWrapper.eq("isbn", target.getIsbn());
            lendWrapper.eq("borrownum", target.getBorrownum());
            lendRecordMapper.update(updateLendRecord, lendWrapper);
        }

        // 5. 删除当前借阅记录
        bookWithUserMapper.delete(
                Wrappers.<BookWithUser>lambdaQuery()
                        .eq(BookWithUser::getId, readerId)
                        .eq(BookWithUser::getIsbn, isbn));

        return Result.success();
    }

    @Transactional
    public Result<?> renew(Integer readerId, String isbn) {
        // 1. 查找当前借阅记录
        BookWithUser existing = bookWithUserMapper.selectOne(
                Wrappers.<BookWithUser>lambdaQuery()
                        .eq(BookWithUser::getId, readerId)
                        .eq(BookWithUser::getIsbn, isbn));
        if (existing == null) {
            return Result.error("-1", "您未借阅该书，无法续借");
        }

        // 2. 检查续借次数
        if (existing.getProlong() == null || existing.getProlong() <= 0) {
            return Result.error("-1", "续借次数已用完");
        }

        // 3. 原子更新：prolong - 1, deadtime + 30天
        UpdateWrapper<BookWithUser> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("id", readerId);
        updateWrapper.eq("isbn", isbn);
        updateWrapper.eq("prolong", existing.getProlong());
        updateWrapper.setSql("prolong = prolong - 1, deadtime = DATE_ADD(deadtime, INTERVAL 30 DAY)");
        int rows = bookWithUserMapper.update(null, updateWrapper);
        if (rows == 0) {
            return Result.error("-1", "续借失败，请稍后重试");
        }

        return Result.success();
    }
}
