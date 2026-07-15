package com.example.demo.controller;

import com.example.demo.commom.Result;
import com.example.demo.service.BorrowService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class BorrowController {

    @Resource
    BorrowService borrowService;

    @PostMapping("/borrow")
    public Result<?> borrow(@RequestBody Map<String, Object> params) {
        Integer readerId = params.get("readerId") != null ?
                Integer.parseInt(params.get("readerId").toString()) : null;
        String isbn = params.get("isbn") != null ? params.get("isbn").toString() : null;
        if (readerId == null || isbn == null) {
            return Result.error("-1", "参数错误：readerId 和 isbn 不能为空");
        }
        return borrowService.borrow(readerId, isbn);
    }

    @PostMapping("/return")
    public Result<?> returnBook(@RequestBody Map<String, Object> params) {
        Integer readerId = params.get("readerId") != null ?
                Integer.parseInt(params.get("readerId").toString()) : null;
        String isbn = params.get("isbn") != null ? params.get("isbn").toString() : null;
        if (readerId == null || isbn == null) {
            return Result.error("-1", "参数错误：readerId 和 isbn 不能为空");
        }
        return borrowService.returnBook(readerId, isbn);
    }

    @PostMapping("/renew")
    public Result<?> renew(@RequestBody Map<String, Object> params) {
        Integer readerId = params.get("readerId") != null ?
                Integer.parseInt(params.get("readerId").toString()) : null;
        String isbn = params.get("isbn") != null ? params.get("isbn").toString() : null;
        if (readerId == null || isbn == null) {
            return Result.error("-1", "参数错误：readerId 和 isbn 不能为空");
        }
        return borrowService.renew(readerId, isbn);
    }
}
