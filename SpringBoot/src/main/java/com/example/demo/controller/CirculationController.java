package com.example.demo.controller;

import com.example.demo.commom.Result;
import com.example.demo.dto.CirculationRequest;
import com.example.demo.service.CirculationException;
import com.example.demo.service.CirculationService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;

@RestController
@RequestMapping("/circulation")
public class CirculationController {
    @Resource
    private CirculationService circulationService;

    @PostMapping("/borrow")
    public Result<?> borrow(@RequestBody CirculationRequest request) {
        try {
            circulationService.borrowBook(request);
            return Result.success();
        } catch (CirculationException e) {
            return Result.error("-1", e.getMessage());
        } catch (Exception e) {
            return Result.error("-1", "借书失败");
        }
    }

    @PostMapping("/return")
    public Result<?> returnBook(@RequestBody CirculationRequest request) {
        try {
            circulationService.returnBook(request);
            return Result.success();
        } catch (CirculationException e) {
            return Result.error("-1", e.getMessage());
        } catch (Exception e) {
            return Result.error("-1", "还书失败");
        }
    }

    @PostMapping("/renew")
    public Result<?> renew(@RequestBody CirculationRequest request) {
        try {
            circulationService.renewBook(request);
            return Result.success();
        } catch (CirculationException e) {
            return Result.error("-1", e.getMessage());
        } catch (Exception e) {
            return Result.error("-1", "续借失败");
        }
    }
}
