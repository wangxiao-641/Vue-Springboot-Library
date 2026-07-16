package com.example.demo.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.StringUtils;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.demo.commom.Result;
import com.example.demo.dto.DueDateAdjustmentRequest;
import com.example.demo.entity.BookWithUser;
import com.example.demo.mapper.BookWithUserMapper;
import com.example.demo.service.CirculationException;
import com.example.demo.service.DueDateAdjustmentService;
import com.example.demo.service.LoanStatusService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/bookwithuser")
public class BookWithUserController {
    @Resource
    private BookWithUserMapper bookWithUserMapper;
    @Resource
    private LoanStatusService loanStatusService;
    @Resource
    private DueDateAdjustmentService dueDateAdjustmentService;

    @PostMapping("/insertNew")
    public Result<?> insertNew() {
        return Result.error("-1", "当前借阅只能通过借书业务接口创建");
    }

    @PostMapping
    public Result<?> update() {
        return Result.error("-1", "当前借阅不允许任意字段修改，请使用专用业务接口");
    }

    @PutMapping("/due-date")
    public Result<?> adjustDueDate(@RequestBody DueDateAdjustmentRequest request) {
        try {
            return Result.success(dueDateAdjustmentService.adjust(request));
        } catch (CirculationException e) {
            return Result.error("-1", e.getMessage());
        } catch (Exception e) {
            return Result.error("-1", "应还日期调整失败");
        }
    }

    @PostMapping("/deleteRecord")
    public Result<?> deleteRecord(@RequestBody BookWithUser bookWithUser) {
        Map<String, Object> map = new HashMap<>();
        map.put("isbn", bookWithUser.getIsbn());
        map.put("id", bookWithUser.getId());
        bookWithUserMapper.deleteByMap(map);
        return Result.success();
    }

    @PostMapping("/deleteRecords")
    public Result<?> deleteRecords(@RequestBody List<BookWithUser> bookWithUsers) {
        for (BookWithUser currentRecord : bookWithUsers) {
            Map<String, Object> map = new HashMap<>();
            map.put("isbn", currentRecord.getIsbn());
            map.put("id", currentRecord.getId());
            bookWithUserMapper.deleteByMap(map);
        }
        return Result.success();
    }

    @GetMapping
    public Result<?> findPage(@RequestParam(defaultValue = "1") Integer pageNum,
                              @RequestParam(defaultValue = "10") Integer pageSize,
                              @RequestParam(defaultValue = "") String search1,
                              @RequestParam(defaultValue = "") String search2,
                              @RequestParam(defaultValue = "") String search3,
                              @RequestParam(defaultValue = "false") Boolean overdueOnly) {
        LambdaQueryWrapper<BookWithUser> wrapper = Wrappers.<BookWithUser>lambdaQuery();
        if (StringUtils.isNotBlank(search1)) {
            wrapper.like(BookWithUser::getIsbn, search1);
        }
        if (StringUtils.isNotBlank(search2)) {
            wrapper.like(BookWithUser::getBookName, search2);
        }
        if (StringUtils.isNotBlank(search3)) {
            try {
                wrapper.eq(BookWithUser::getId, Integer.valueOf(search3));
            } catch (NumberFormatException e) {
                wrapper.like(BookWithUser::getNickName, search3);
            }
        }
        if (Boolean.TRUE.equals(overdueOnly)) {
            wrapper.lt(BookWithUser::getDeadtime, loanStatusService.startOfToday());
        }
        wrapper.orderByAsc(BookWithUser::getDeadtime).orderByAsc(BookWithUser::getBorrowId);
        Page<BookWithUser> page = bookWithUserMapper.selectPage(new Page<>(pageNum, pageSize), wrapper);
        page.getRecords().forEach(loanStatusService::applyStatus);
        return Result.success(page);
    }
}
