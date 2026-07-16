package com.example.demo.service;

import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.example.demo.dto.DueDateAdjustmentRequest;
import com.example.demo.entity.BookWithUser;
import com.example.demo.entity.User;
import com.example.demo.mapper.BookWithUserMapper;
import com.example.demo.mapper.UserMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.Resource;
import java.util.Date;

@Service
public class DueDateAdjustmentService {
    @Resource
    private BookWithUserMapper bookWithUserMapper;
    @Resource
    private LoanStatusService loanStatusService;
    @Resource
    private UserMapper userMapper;

    @Transactional(rollbackFor = Exception.class)
    public BookWithUser adjust(DueDateAdjustmentRequest request) {
        if (request == null || request.getOperatorId() == null || request.getBorrowId() == null) {
            throw new CirculationException("当前借阅标识不能为空");
        }
        User operator = userMapper.selectById(request.getOperatorId());
        if (operator == null || operator.getRole() == null || operator.getRole() != 1) {
            throw new CirculationException("只有管理员可以调整应还日期");
        }
        Date dueDate = loanStatusService.parseAdjustment(request.getDueDate());
        BookWithUser current = bookWithUserMapper.selectByBorrowIdForUpdate(request.getBorrowId());
        if (current == null) {
            throw new CirculationException("当前借阅不存在");
        }

        BookWithUser update = new BookWithUser();
        update.setDeadtime(dueDate);
        UpdateWrapper<BookWithUser> wrapper = new UpdateWrapper<>();
        wrapper.eq("borrow_id", request.getBorrowId());
        if (bookWithUserMapper.update(update, wrapper) != 1) {
            throw new CirculationException("应还日期调整失败");
        }

        current.setDeadtime(dueDate);
        loanStatusService.applyStatus(current);
        return current;
    }
}
