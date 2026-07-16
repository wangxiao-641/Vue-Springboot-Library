package com.example.demo.service;

import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.example.demo.dto.CirculationRequest;
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
public class CirculationService {
    private static final String BOOK_AVAILABLE = "1";
    private static final String BOOK_UNAVAILABLE = "0";
    private static final String LEND_NOT_RETURNED = "0";
    private static final String LEND_RETURNED = "1";
    private static final int BORROW_DAYS = 30;
    private static final int INITIAL_RENEW_TIMES = 1;

    @Resource
    private BookMapper bookMapper;
    @Resource
    private BookWithUserMapper bookWithUserMapper;
    @Resource
    private LendRecordMapper lendRecordMapper;
    @Resource
    private UserMapper userMapper;
    @Resource
    private LoanStatusService loanStatusService;

    @Transactional(rollbackFor = Exception.class)
    public void borrowBook(CirculationRequest request) {
        validateRequest(request);
        User reader = getReader(request.getReaderId());
        List<BookWithUser> readerBorrows = bookWithUserMapper.selectByReaderIdForUpdate(request.getReaderId());
        if (readerBorrows.stream().anyMatch(current -> loanStatusService.isOverdue(current.getDeadtime()))) {
            throw new CirculationException("存在逾期未还图书，归还后才能借新书");
        }
        if (readerBorrows.stream().anyMatch(current -> request.getIsbn().equals(current.getIsbn()))) {
            throw new CirculationException("当前读者已借阅该图书");
        }
        Book book = getBookForUpdate(request.getIsbn());
        if (findOpenLendRecord(request.getReaderId(), request.getIsbn()) != null) {
            throw new CirculationException("该图书存在未归还记录");
        }

        int nextBorrownum = book.getBorrownum() == null ? 1 : book.getBorrownum() + 1;
        markBookBorrowed(book, nextBorrownum);

        Date lendTime = loanStatusService.now();
        LendRecord lendRecord = new LendRecord();
        lendRecord.setReaderId(request.getReaderId());
        lendRecord.setIsbn(book.getIsbn());
        lendRecord.setBookname(book.getName());
        lendRecord.setLendTime(lendTime);
        lendRecord.setStatus(LEND_NOT_RETURNED);
        lendRecord.setBorrownum(nextBorrownum);
        if (lendRecordMapper.insert(lendRecord) != 1) {
            throw new CirculationException("借阅记录写入失败");
        }

        BookWithUser current = new BookWithUser();
        current.setId(request.getReaderId());
        current.setIsbn(book.getIsbn());
        current.setBookName(book.getName());
        current.setNickName(readerName(reader));
        current.setLendtime(lendTime);
        current.setDeadtime(loanStatusService.addCalendarDays(lendTime, BORROW_DAYS));
        current.setProlong(INITIAL_RENEW_TIMES);
        if (bookWithUserMapper.insert(current) != 1) {
            throw new CirculationException("当前借阅写入失败");
        }
    }

    @Transactional(rollbackFor = Exception.class)
    public void returnBook(CirculationRequest request) {
        validateRequest(request);
        Book book = getBookForUpdate(request.getIsbn());
        BookWithUser current = findCurrentBorrow(request.getReaderId(), request.getIsbn());
        if (current == null) {
            throw new CirculationException("未找到当前借阅，不能重复还书");
        }
        LendRecord openRecord = findOpenLendRecord(request.getReaderId(), request.getIsbn());
        if (openRecord == null) {
            throw new CirculationException("未找到未归还借阅记录");
        }

        LendRecord returnedRecord = new LendRecord();
        returnedRecord.setReturnTime(loanStatusService.now());
        returnedRecord.setStatus(LEND_RETURNED);
        UpdateWrapper<LendRecord> lendUpdate = new UpdateWrapper<>();
        lendUpdate.eq("reader_id", request.getReaderId())
                .eq("isbn", request.getIsbn())
                .eq("borrownum", openRecord.getBorrownum())
                .eq("status", LEND_NOT_RETURNED);
        if (lendRecordMapper.update(returnedRecord, lendUpdate) < 1) {
            throw new CirculationException("借阅记录归还更新失败");
        }

        UpdateWrapper<BookWithUser> currentDelete = new UpdateWrapper<>();
        currentDelete.eq("id", request.getReaderId()).eq("isbn", request.getIsbn());
        if (bookWithUserMapper.delete(currentDelete) < 1) {
            throw new CirculationException("当前借阅删除失败");
        }

        markBookReturned(book);
    }

    @Transactional(rollbackFor = Exception.class)
    public void renewBook(CirculationRequest request) {
        validateRequest(request);
        BookWithUser current = findCurrentBorrow(request.getReaderId(), request.getIsbn());
        if (current == null) {
            throw new CirculationException("未找到当前借阅，不能续借");
        }
        if (loanStatusService.isOverdue(current.getDeadtime())) {
            throw new CirculationException("该图书已逾期，不能续借");
        }
        if (current.getProlong() == null || current.getProlong() <= 0) {
            throw new CirculationException("该图书已无可续借次数");
        }

        BookWithUser update = new BookWithUser();
        Date baseDeadtime = current.getDeadtime();
        if (baseDeadtime == null) {
            throw new CirculationException("当前借阅缺少应还日期");
        }
        update.setDeadtime(loanStatusService.addCalendarDays(baseDeadtime, BORROW_DAYS));
        update.setProlong(current.getProlong() - 1);
        UpdateWrapper<BookWithUser> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("id", request.getReaderId())
                .eq("isbn", request.getIsbn())
                .eq("prolong", current.getProlong());
        if (bookWithUserMapper.update(update, updateWrapper) < 1) {
            throw new CirculationException("续借更新失败");
        }
    }

    private void validateRequest(CirculationRequest request) {
        if (request == null || request.getReaderId() == null || request.getIsbn() == null || request.getIsbn().trim().isEmpty()) {
            throw new CirculationException("读者和图书标识不能为空");
        }
    }

    private Book getBookForUpdate(String isbn) {
        Book book = bookMapper.selectByIsbnForUpdate(isbn);
        if (book == null) {
            throw new CirculationException("图书不存在");
        }
        return book;
    }

    private User getReader(Integer readerId) {
        User reader = userMapper.selectById(readerId);
        if (reader == null) {
            throw new CirculationException("读者不存在");
        }
        return reader;
    }

    private BookWithUser findCurrentBorrow(Integer readerId, String isbn) {
        return bookWithUserMapper.selectByReaderIdAndIsbnForUpdate(readerId, isbn);
    }

    private LendRecord findOpenLendRecord(Integer readerId, String isbn) {
        return lendRecordMapper.selectOpenRecordForUpdate(readerId, isbn);
    }

    private void markBookBorrowed(Book book, int nextBorrownum) {
        validateInventory(book);
        if (book.getAvailableCount() <= 0) {
            throw new CirculationException("可借数量不足");
        }
        book.setAvailableCount(book.getAvailableCount() - 1);
        book.setStatus(book.getAvailableCount() <= 0 ? BOOK_UNAVAILABLE : BOOK_AVAILABLE);
        book.setBorrownum(nextBorrownum);
        if (bookMapper.updateById(book) != 1) {
            throw new CirculationException("图书库存更新失败");
        }
    }

    private void markBookReturned(Book book) {
        validateInventory(book);
        if (book.getAvailableCount() >= book.getTotalCount()) {
            throw new CirculationException("图书库存状态异常，不能重复还书");
        }
        book.setAvailableCount(book.getAvailableCount() + 1);
        book.setStatus(book.getAvailableCount() > 0 ? BOOK_AVAILABLE : BOOK_UNAVAILABLE);
        if (bookMapper.updateById(book) != 1) {
            throw new CirculationException("图书库存更新失败");
        }
    }

    private void validateInventory(Book book) {
        if (book.getTotalCount() == null || book.getAvailableCount() == null) {
            throw new CirculationException("图书库存数量缺失");
        }
        if (book.getTotalCount() <= 0 || book.getAvailableCount() < 0 || book.getAvailableCount() > book.getTotalCount()) {
            throw new CirculationException("图书库存状态异常");
        }
    }

    private String readerName(User reader) {
        if (reader.getNickName() != null && !reader.getNickName().trim().isEmpty()) {
            return reader.getNickName();
        }
        return reader.getUsername();
    }
}
