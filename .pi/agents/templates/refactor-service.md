# 变更模板：Controller 业务逻辑抽取到 Service 层

> ⚠️ 这是一个结构性变更模板。仅在用户明确要求引入 Service 层时使用。不要主动做这个重构。

## 前置检查

- [ ] 确认要重构的 Controller 和方法范围
- [ ] 确认是否需要对借还书流程加事务控制（涉及多表操作时需要）
- [ ] 确认后端编译能通过（作为基线）

## 改动步骤

### 1. 创建 Service 包

```bash
mkdir -p SpringBoot/src/main/java/com/example/demo/service
```

### 2. 创建 Service 接口和实现类

对于每个要重构的 Controller，创建：

```
service/
├── XxxService.java          # 接口
└── impl/
    └── XxxServiceImpl.java  # 实现类
```

示例模式：

```java
// XxxService.java
package com.example.demo.service;

import com.example.demo.commom.Result;

public interface XxxService {
    Result<?> findPage(Integer pageNum, Integer pageSize, String search);
    Result<?> save(Xxx entity);
    Result<?> update(Xxx entity);
    Result<?> delete(Long id);
}

// XxxServiceImpl.java
package com.example.demo.service.impl;

import com.example.demo.entity.Xxx;
import com.example.demo.mapper.XxxMapper;
import com.example.demo.service.XxxService;
import com.example.demo.commom.Result;
import org.springframework.stereotype.Service;
import javax.annotation.Resource;

@Service
public class XxxServiceImpl implements XxxService {
    @Resource
    private XxxMapper xxxMapper;

    @Override
    public Result<?> findPage(Integer pageNum, Integer pageSize, String search) {
        // 业务逻辑从 Controller 迁移过来
    }
    // ...
}
```

### 3. 修改 Controller

将 Controller 中的业务逻辑调用改为注入 Service：

```java
@RestController
@RequestMapping("/xxx")
public class XxxController {
    @Resource
    private XxxService xxxService;  // 替换原来的 @Resource XxxMapper

    // 方法体简化为调用 service
    @GetMapping
    public Result<?> findPage(...) {
        return xxxService.findPage(pageNum, pageSize, search);
    }
}
```

### 4. 事务支持（借还书等涉及多表的操作必须加）

```java
@Service
public class BorrowServiceImpl implements BorrowService {
    @Resource
    private BookMapper bookMapper;
    @Resource
    private LendRecordMapper lendRecordMapper;
    @Resource
    private BookWithUserMapper bookWithUserMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<?> borrowBook(Integer userId, String isbn) {
        // 1. 更新图书状态
        // 2. 新增借阅记录
        // 3. 新增当前借阅状态
        // 以上三步在同一个事务中
    }
}
```

需要启用的配置：

1. 在 SpringBoot 启动类或配置类上加 `@EnableTransactionManagement`（Spring Boot 2.x 通常自动启用）
2. 确保 `application.properties` 中数据源配置正确
3. Service 方法上加 `@Transactional(rollbackFor = Exception.class)`

### 5. 编译验证

```bash
cd SpringBoot && mvn package -DskipTests -q 2>&1 | tail -5
# 期望: BUILD SUCCESS
```

### 6. 功能验证

重构后必须运行 `./dev.sh verify` 确认核心流程不受影响。

### 7. 上下文文档更新

- [ ] 在 `library-context.md` 的包结构中添加 `service/` 和 `service/impl/`
- [ ] 更新 API 映射表格（通常路径不变，但调用链变了）

## 注意事项

- 不要一次性把所有 Controller 都重构。按模块逐个来，每重构一个就验证一个。
- Service 方法签名不用和 Controller 一一对应——可以合并多个简单操作。
- 借还书流程移到 Service 层后，前端仍然调用多个 API，但每个 API 调链变成 Controller→Service→Mapper。
- 事务边界只在 Service 层，Controller 层不加事务注解。
