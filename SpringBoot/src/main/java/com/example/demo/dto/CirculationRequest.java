package com.example.demo.dto;

import lombok.Data;

@Data
public class CirculationRequest {
    private Integer readerId;
    private String isbn;
}
