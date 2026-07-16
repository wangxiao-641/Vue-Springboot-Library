package com.example.demo.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;

import java.math.BigDecimal;
import java.util.Date;

@TableName("book")
public class Book {

    @TableId (type = IdType.AUTO)
    private Integer id;
    private String isbn;
    private String name;
    private BigDecimal price;
    private String author;
    private Integer borrownum;
    private String publisher;
    @JsonFormat(locale="zh",timezone="GMT+8", pattern="yyyy-MM-dd")
    private Date createTime;
    private Integer total;
    private Integer available;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }
    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }
    public Integer getBorrownum() { return borrownum; }
    public void setBorrownum(Integer borrownum) { this.borrownum = borrownum; }
    public String getPublisher() { return publisher; }
    public void setPublisher(String publisher) { this.publisher = publisher; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
    public Integer getTotal() { return total; }
    public void setTotal(Integer total) { this.total = total; }
    public Integer getAvailable() { return available; }
    public void setAvailable(Integer available) { this.available = available; }
}
