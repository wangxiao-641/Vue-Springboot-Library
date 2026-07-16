package com.example.demo.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;

import java.util.Date;

@TableName("bookwithuser")
public class BookWithUser {
    private Integer id;
    private String isbn;
    private String bookName;
    private String nickName;
    @JsonFormat(locale="zh",timezone="GMT+8", pattern="yyyy-MM-dd HH:mm:ss")
    private Date lendtime;
    @JsonFormat(locale="zh",timezone="GMT+8", pattern="yyyy-MM-dd HH:mm:ss")
    private Date deadtime;
    private Integer prolong;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }
    public String getBookName() { return bookName; }
    public void setBookName(String bookName) { this.bookName = bookName; }
    public String getNickName() { return nickName; }
    public void setNickName(String nickName) { this.nickName = nickName; }
    public Date getLendtime() { return lendtime; }
    public void setLendtime(Date lendtime) { this.lendtime = lendtime; }
    public Date getDeadtime() { return deadtime; }
    public void setDeadtime(Date deadtime) { this.deadtime = deadtime; }
    public Integer getProlong() { return prolong; }
    public void setProlong(Integer prolong) { this.prolong = prolong; }
}
