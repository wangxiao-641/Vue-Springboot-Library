# 变更模板：新增后端 API

## 前置检查

- [ ] 确认不影响现有 API 的路径和参数签名
- [ ] 确认是否需要新增数据库表或字段

## 改动清单（按顺序执行）

### 1. 数据库变更（如需要）

如果新增表：
- [ ] 编写 CREATE TABLE 语句
- [ ] 追加到 `sql/springboot-vue.sql` 末尾
- [ ] 在 `library-context.md` 的数据库章节补充新表信息

如果新增字段：
- [ ] 编写 ALTER TABLE 语句
- [ ] 追加到 `sql/springboot-vue.sql` 末尾（注释标注日期和用途）

### 2. Entity 实体类

- [ ] 在 `SpringBoot/src/main/java/com/example/demo/entity/` 下新建或修改实体类
- [ ] 检查：`@TableName` 与表名一致，字段名驼峰自动映射下划线
- [ ] 检查：日期字段加 `@JsonFormat(locale="zh",timezone="GMT+8", pattern="yyyy-MM-dd")`
- [ ] 检查：主键加 `@TableId(type = IdType.AUTO)`

### 3. Mapper 接口

- [ ] 在 `SpringBoot/src/main/java/com/example/demo/mapper/` 下新建接口
- [ ] 格式：`public interface XxxMapper extends BaseMapper<Xxx> {}`
- [ ] 如需自定义 SQL，在接口方法上加 `@Select` / `@Update` 等注解

### 4. Controller 接口

- [ ] 在 `SpringBoot/src/main/java/com/example/demo/controller/` 下新建或修改 Controller
- [ ] 类注解：`@RestController` + `@RequestMapping("/xxx")`
- [ ] 注入 Mapper：`@Resource XxxMapper xxxMapper;`
- [ ] 所有方法返回 `Result<?>` 或 `Result<T>`
- [ ] 成功返回：`Result.success(data)` 或 `Result.success()`
- [ ] 失败返回：`Result.error("-1", "错误描述")`
- [ ] 分页查询：使用 `Page<Xxx>` + `selectPage(new Page<>(pageNum, pageSize), wrapper)`
- [ ] 条件查询：使用 `LambdaQueryWrapper` + `Wrappers.<Xxx>lambdaQuery()`

### 5. 编译验证

```bash
cd SpringBoot && mvn package -DskipTests -q 2>&1 | tail -5
# 期望输出: BUILD SUCCESS
```

### 6. 上下文文档更新

- [ ] 在 `library-context.md` 的 API 路径表格中添加新接口
- [ ] 如果有新表/新字段，更新 Entity 和数据库表格

## 示例：新增一个出版社管理接口

需求：管理员可以查看出版社列表，按名称搜索。

实际改动文件（4 个）：
1. `entity/Publisher.java` — 新增实体类
2. `mapper/PublisherMapper.java` — 新增 Mapper
3. `controller/PublisherController.java` — 新增 Controller 提供 GET 分页+搜索
4. `library-context.md` — 补充 API 文档
