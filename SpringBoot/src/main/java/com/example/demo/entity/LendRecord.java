package com.example.demo.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.util.Date;

@TableName("lend_record")
@Data
public class LendRecord {
    private Integer readerId;
    private String isbn;
    private String bookname;
    @JsonFormat(locale="zh",timezone="GMT+8", pattern="yyyy-MM-dd HH:mm:ss")
    private Date lendTime;
    @JsonFormat(locale="zh",timezone="GMT+8", pattern="yyyy-MM-dd HH:mm:ss")
    private Date returnTime;
    private String status;
    private Integer borrownum;
    @TableField(exist = false)
    @JsonFormat(locale="zh",timezone="GMT+8", pattern="yyyy-MM-dd HH:mm:ss")
    private Date deadtime;
    @TableField(exist = false)
    private String dueStatus;
    @TableField(exist = false)
    private String dueStatusText;
    @TableField(exist = false)
    private Long overdueDays;
}
