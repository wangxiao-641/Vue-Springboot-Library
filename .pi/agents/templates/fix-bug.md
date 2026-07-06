# 变更模板：修复 Bug

## 前置排查（动手改代码前先走完）

### 1. 复现 Bug

用最小步骤复现问题：

```
重现步骤：
1. ________
2. ________
3. ________

实际结果：________
期望结果：________
```

### 2. 定位问题层次

根据错误现象判断在哪一层：

| 现象 | 可能位置 |
|------|---------|
| 前端页面报错、白屏 | Vue 组件 / API 调用 / 数据格式 |
| 前端操作无反应 | `request.js` 实现 / `sessionStorage` / 权限判断 |
| 后端返回 `code="-1"` | Controller 逻辑 / Service 逻辑 / 参数校验 |
| 后端返回 500 | Mapper SQL 错误 / 空指针 / 事务问题 |
| 数据没存入数据库 | Mapper 映射 / 字段类型不匹配 / 事务未提交 |
| 数据存入但查不到 | 查询条件错误 / 分页参数 / 字符编码 |

### 3. 查看日志

```bash
# 后端日志
./dev.sh docker-logs backend | tail -50

# 前端编译错误（如果有）
cd vue && npm run build 2>&1 | tail -20
```

### 4. 检查相关文件

根据 API 路径定位后端文件：

| API 路径前缀 | Controller 文件 |
|-------------|----------------|
| `/user` | `controller/UserController.java` |
| `/book` | `controller/BookController.java` |
| `/LendRecord` | `controller/LendRecordController.java` |
| `/bookwithuser` | `controller/BookWithUserController.java` |
| `/dashboard` | `controller/DashboardController.java` |

根据前端路由路径定位前端文件：

| 路由 | 页面文件 |
|------|---------|
| `/bookManage` | `views/Book.vue` |
| `/readerManage` | `views/User.vue` |
| `/lendRecord` | `views/LendRecord.vue` |
| `/borrowStatus` | `views/BookWithUser.vue` |
| `/login` | `views/Login.vue` |

## 修复

### 后端 Bug

- [ ] 修改对应的 Controller / Service / Mapper 文件
- [ ] 编译验证：`cd SpringBoot && mvn package -DskipTests -q`
- [ ] Docker 重启后端：`docker restart library-backend`
- [ ] 用 curl 验证修复

### 前端 Bug

- [ ] 修改对应的 Vue 组件文件
- [ ] 编译验证：`cd vue && npm run build 2>&1 | tail -3`
- [ ] 如果是 Element Plus 组件问题：
  - `el-dialog` 用 `v-model` 而不是 `:visible.sync`
  - `el-pagination` 用 `v-model:currentPage` 而不是 `:current-page.sync`
  - `el-input` 的 `v-model` 值如果是数字类型，确保用 `.number` 修饰符
  - 日期组件加 `value-format="YYYY-MM-DD"`
- [ ] Docker 重启前端：`docker restart library-frontend`

### 数据库 Bug

- [ ] 确认字段类型和长度和 Java Entity 一致
- [ ] 确认 `sql/springboot-vue.sql` 中的建表语句正确
- [ ] 如果需修改表结构，写 ALTER 语句并在 MySQL 中执行
- [ ] 将 ALTER 语句追加到 `sql/springboot-vue.sql` 末尾

### 修复后验证

- [ ] Bug 不再复现
- [ ] `./dev.sh api-test` 全部通过
- [ ] 相关功能的手动测试

### 记录

- [ ] 如果是一个值得记住的坑，在 `library-context.md` 的对应章节加注释
