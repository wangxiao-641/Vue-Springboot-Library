package com.example.demo.dto;

import lombok.Data;

@Data
public class ReaderCreateRequest {
    private Integer operatorId;
    private String username;
    private String password;
    private String nickName;
    private String phone;
    private String sex;
    private String address;
    private Integer role;
}
