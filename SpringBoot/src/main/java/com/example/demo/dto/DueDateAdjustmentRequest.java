package com.example.demo.dto;

import lombok.Data;

@Data
public class DueDateAdjustmentRequest {
    private Integer operatorId;
    private Long borrowId;
    private String dueDate;
}
