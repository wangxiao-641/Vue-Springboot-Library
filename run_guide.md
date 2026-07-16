# 图书馆管理系统运行指南

## 1. 项目目录

本项目名称为 `Vue-Springboot-Library`，主要目录如下：

```text
Vue-Springboot-Library
├─ SpringBoot   后端项目
├─ vue          前端项目
├─ sql          数据库初始化脚本
├─ images       项目截图
├─ run          原项目提供的运行文件
└─ README.md    项目说明
```

运行系统时，需要同时准备数据库、后端服务和前端服务。

## 2. 环境准备

请先确认本机已经安装以下环境：

- JDK
- Maven
- Node.js
- npm
- MySQL

建议使用命令检查环境：

```powershell
java -version
mvn -version
node -v
npm -v
mysql --version
```

如果某个命令无法识别，说明对应工具没有安装，或者没有配置到系统环境变量。

## 3. 初始化数据库

项目数据库脚本位于：

```text
Vue-Springboot-Library/sql/springboot-vue.sql
```

需要将该 SQL 文件导入 MySQL。导入后会创建数据库：

```text
springboot-vue
```

可以使用 Navicat、DataGrip、MySQL Workbench 等数据库工具导入，也可以使用命令行导入：

```powershell
mysql -uroot -p < sql/springboot-vue.sql
```

执行命令后会提示输入 MySQL 密码。

如果是在已有数据库上升级本次库存数量需求，需要执行迁移脚本：

```powershell
mysql -uroot -p springboot-vue < sql/migrations/20260716_inventory_counts.sql
```

该脚本会为 `book.isbn` 添加唯一索引，为 `book.total_count` / `book.available_count` 添加合法范围约束，并把 `bookwithuser` 从 `book_name` 主键迁移为 `borrow_id` 技术主键 + `(id, isbn)` 唯一约束。执行 ALTER 前会强制校验重复 ISBN、重复/孤立当前借阅、库存与当前借阅/未归还记录一致性以及已迁移/部分迁移结构；发现问题会直接中止并提示需要清理的数据类型。

## 4. 修改后端数据库配置

后端配置文件位于：

```text
Vue-Springboot-Library/SpringBoot/src/main/resources/application.properties
```

需要重点检查数据库连接配置：

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/springboot-vue?useUnicode=true&characterEncoding=utf-8&allowMultiQueries=true&useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=GMT%2b8
spring.datasource.username=root
spring.datasource.password=你的MySQL密码
```

请将 `spring.datasource.password` 改成本机 MySQL 的真实密码。

如果你的 MySQL 用户不是 `root`，也需要同步修改：

```properties
spring.datasource.username=你的MySQL用户名
```

## 5. 启动后端

进入后端目录：

```powershell
cd "Vue-Springboot-Library/SpringBoot"
```

使用 Maven 打包：

```powershell
mvn -DskipTests package
```

打包成功后，运行后端 jar：

```powershell
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

后端默认端口为：

```text
http://127.0.0.1:9090/
```

可以在浏览器访问下面地址测试后端是否正常：

```text
http://127.0.0.1:9090/dashboard
```

如果能返回 JSON 数据，说明后端已经连上数据库。

## 6. 启动前端

重新打开一个终端，进入前端目录：

```powershell
cd "Vue-Springboot-Library/vue"
```

安装前端依赖：

```powershell
npm install --legacy-peer-deps
```

启动前端开发服务：

```powershell
npm run serve
```

前端默认访问地址为：

```text
http://127.0.0.1:9876/
```

打开浏览器访问该地址，即可进入系统登录页面。

## 7. 前后端关系

前端运行在：

```text
http://127.0.0.1:9876/
```

后端运行在：

```text
http://127.0.0.1:9090/
```

前端代码中通过 `/api` 访问后端接口。开发环境下，`vue/vue.config.js` 会把 `/api` 请求代理到后端 `9090` 端口。

也就是说，前端页面请求：

```text
/api/book
```

实际会转发到：

```text
http://127.0.0.1:9090/book
```

## 8. 准备测试账号

原项目 README 中说明：测试账号需要自己插入数据库。

如果导入 SQL 后没有可用账号，可以在 MySQL 中执行以下语句创建测试账号：

```sql
INSERT INTO user(username, password, nick_name, phone, sex, address, role)
VALUES ('admin', '123456', '管理员', '13800000000', '男', '学校', 1);

INSERT INTO user(username, password, nick_name, phone, sex, address, role)
VALUES ('reader', '123456', '读者', '13900000000', '女', '学校', 2);
```

创建后可以使用以下账号登录：

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | `admin` | `123456` |
| 读者 | `reader` | `123456` |

## 9. 推荐验证流程

系统启动后，建议按下面顺序测试：

1. 使用管理员账号登录。
2. 进入书籍管理页面，查看图书列表。
3. 新增一本图书。
4. 使用读者账号登录。
5. 查询刚新增的图书。
6. 点击借阅。
7. 查看借阅状态。
8. 执行续借。
9. 执行还书。
10. 再次查看图书状态是否恢复为可借。

## 10. 借书、还书、续借后端业务接口

借书、还书、续借已经收敛为三个后端事务接口。前端点击一次业务按钮时，只发送一个业务写请求，列表刷新请求不计入。请求体只传读者和图书标识，不传库存、状态、借阅时间、应还时间或续借后的日期。

### 10.1 借书

```bash
curl -s -X POST "http://localhost:9090/circulation/borrow" \
  -H "Content-Type: application/json" \
  -d '{"readerId":25,"isbn":"TEST-ISBN-001"}'
```

后端会校验图书是否存在、库存是否充足、读者是否存在、当前是否已借该书，并统一扣减库存、生成当前借阅和借阅历史，应还日期为借书时间后 30 天，续借次数初始化为 1。

图书新增和编辑库存规则：

- `POST /book` 必须提交正整数 `totalCount`，不能提交 `availableCount`；后端会把 `availableCount` 初始化为 `totalCount`。
- `PUT /book` 修改馆藏总数时不能提交 `availableCount`；后端按“当前已借出数 = 旧总数 - 旧可借数”重算新可借数量。
- 新馆藏总数小于当前已借出数时，接口返回 `code=-1`，图书字段不变化。

### 10.2 还书

```bash
curl -s -X POST "http://localhost:9090/circulation/return" \
  -H "Content-Type: application/json" \
  -d '{"readerId":25,"isbn":"TEST-ISBN-001"}'
```

后端会校验当前借阅和未归还历史是否存在，并在一个事务内更新历史记录为已归还、删除当前借阅、恢复可借数量。重复还书会失败，库存不会再次增加。

### 10.3 续借

```bash
curl -s -X POST "http://localhost:9090/circulation/renew" \
  -H "Content-Type: application/json" \
  -d '{"readerId":25,"isbn":"TEST-ISBN-001"}'
```

后端会校验当前借阅和剩余续借次数。最多续借 1 次，成功后应还日期延长 30 天且剩余续借次数变为 0；第二次续借失败，应还日期不变化。

## 11. 借还续黑盒验证脚本

脚本文件：

```text
verify_circulation_http.py
```

运行环境：

- Python 3 标准库。
- 后端服务已启动。
- 数据库结构包含 `book.total_count` 和 `book.available_count` 字段。
- 不需要临时联网安装依赖。

默认验证本机 9090：

```bash
./verify_circulation_http.py
```

指定后端地址：

```bash
BACKEND_URL=http://localhost:9090 ./verify_circulation_http.py
```

脚本只通过 HTTP 调用后端接口，不直接连接或修改数据库。它会自动创建唯一读者和唯一图书，验证 6 个用例并逐项输出 `PASS` 或 `FAIL`；任一用例失败时返回非零退出码。

覆盖用例：

1. 可借图书借阅成功，库存减少，并生成一条当前借阅和历史记录。
2. 库存为 0 时借阅失败，失败前后库存和记录数量不变。
3. 首次续借成功，应还日期延长 30 天，剩余续借次数变为 0。
4. 再次续借失败，应还日期不变。
5. 正常还书成功，库存恢复，当前借阅消失，历史记录显示已归还。
6. 重复还书失败，库存不得再次增加。

清理说明：脚本结束时会通过 HTTP 删除本次创建的当前借阅、借阅历史、测试图书和测试读者。若后端中途不可用，脚本会输出 `CLEANUP WARN`，可按输出中的唯一 ISBN 或用户名在系统里定位残留测试数据。

## 12. 库存数量黑盒验证脚本

脚本文件：

```text
verify_inventory_http.py
```

默认验证本机 9090：

```bash
./verify_inventory_http.py
```

指定后端地址：

```bash
BACKEND_URL=http://localhost:9090 ./verify_inventory_http.py
```

脚本只通过 HTTP 调用后端接口，不直接连接或修改数据库。它会自动创建两个唯一读者和一本唯一图书，逐项输出 `PASS` 或 `FAIL`，任一用例失败时返回非零退出码。

覆盖用例：

1. 新增馆藏总数为 1 的图书后，总数为 1、可借为 1，伪造 `availableCount` 被拒绝。
2. 读者 A 借阅成功后可借数量变为 0。
3. 读者 B 在库存为 0 时借阅失败，图书、当前借阅、借阅历史均不变化。
4. 读者 A 归还后可借数量恢复为 1。
5. 已有 1 本借出时，管理员把馆藏总数改为 0 失败且数据不变化。
6. 管理员把馆藏总数合法改为 3 后，可借数量按已借出数调整为 2。
7. 扩大馆藏后，并发执行馆藏编辑和同一读者两次借阅：编辑成功、借阅恰好一次成功一次失败；不同读者可同时持有同一 ISBN，同一读者不会产生重复当前借阅或未归还记录。
8. 刷新查询后，总数和可借数量仍正确；清理失败或清理后仍有测试数据时脚本返回非零退出码。

清理说明：脚本结束时会通过 HTTP 删除本次创建的当前借阅、借阅历史、测试图书和测试读者。若后端中途不可用，脚本会输出 `CLEANUP WARN`，可按输出中的唯一 ISBN 或用户名在系统里定位残留测试数据。

## 13. 常见问题

### 13.1 Maven 命令无法识别

说明 Maven 没有安装，或者没有配置环境变量。

可以检查：

```powershell
mvn -version
```

如果命令失败，需要重新安装 Maven，或将 Maven 的 `bin` 目录加入系统 `Path`。

### 13.2 后端启动失败，提示数据库连接错误

重点检查：

- MySQL 是否已经启动。
- `springboot-vue` 数据库是否已经创建。
- `application.properties` 中的用户名和密码是否正确。
- MySQL 端口是否为 `3306`。

如果看到类似错误：

```text
Access denied for user 'root'@'localhost'
```

通常说明数据库用户名或密码不正确。

### 13.3 后端启动失败，提示 Public Key Retrieval is not allowed

可以检查 JDBC URL 中是否包含：

```properties
allowPublicKeyRetrieval=true
```

完整示例：

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/springboot-vue?useUnicode=true&characterEncoding=utf-8&allowMultiQueries=true&useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=GMT%2b8
```

### 13.4 前端 npm install 失败

可以尝试：

```powershell
npm install --legacy-peer-deps
```

如果依赖版本冲突，优先使用上面的命令。

### 13.5 前端页面能打开，但接口请求失败

检查后端是否已经启动。

后端地址应为：

```text
http://127.0.0.1:9090/
```

同时检查前端代理配置 `vue/vue.config.js` 中是否代理到正确端口。

### 13.6 登录失败

可能原因：

- 数据库中没有测试账号。
- 用户名或密码输入错误。
- 后端没有连接上数据库。

可以先在数据库中确认 `user` 表是否有账号数据。

## 14. 运行成功标志

当以下条件都满足时，说明项目运行成功：

- MySQL 中存在 `springboot-vue` 数据库。
- 后端服务启动在 `9090` 端口。
- 前端服务启动在 `9876` 端口。
- 浏览器能打开登录页面。
- 使用管理员或读者账号可以成功登录。
- 图书列表、借阅状态、借阅记录等页面能正常加载数据。
