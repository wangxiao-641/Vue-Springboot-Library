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
mysql -uroot -p springboot-vue < sql/migrations/20260716_overdue_management.sql
mysql -uroot -p springboot-vue < sql/migrations/20260716_user_management.sql
```

库存迁移脚本会为 `book.isbn` 添加唯一索引，为 `book.total_count` / `book.available_count` 添加合法范围约束，并把 `bookwithuser` 从 `book_name` 主键迁移为 `borrow_id` 技术主键 + `(id, isbn)` 唯一约束。执行 ALTER 前会强制校验重复 ISBN、重复/孤立当前借阅、库存与当前借阅/未归还记录一致性以及已迁移/部分迁移结构；发现问题会直接中止并提示需要清理的数据类型。

逾期迁移脚本会先检查 `bookwithuser.deadtime`：发现任意 NULL 当前借阅时使用 `SIGNAL` 明确中止，不执行后续 ALTER；数据完整时将该字段改为 `NOT NULL`，并幂等添加逾期筛选索引。整个脚本可重复执行。新数据库直接导入基线 SQL 时已包含 `NOT NULL` 约束和索引。

用户管理迁移会在任何 ALTER 前检查 `user.username` 重复数据。如有重复会使用 `SIGNAL` 直接中止，不创建索引；数据安全时幂等添加唯一索引 `uk_user_username`，保证并发新增时也不会产生重复账号。

如果迁移报告 `deadtime 为 NULL`，可先定位需要业务纠正的记录：

```sql
SELECT borrow_id, id, isbn, book_name, lendtime
FROM bookwithuser
WHERE deadtime IS NULL;
```

必须逐条确认真实应还日期并完成数据纠正后再重跑迁移；脚本不会用当前时间或其他含糊默认值填充历史 NULL。

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

## 10. 逾期管理规则与接口

- 借书请求只提交 `{readerId, isbn}`；借书时间和应还时间均由后端生成，应还时间为借书时间后 30 个日历日。
- 业务时区固定为 `Asia/Shanghai`。应还日早于今天时计为逾期；今天到期不逾期；距应还日 0–3 天为“即将到期”。
- `GET /bookwithuser` 和 `GET /LendRecord` 均支持 `overdueOnly=true`，当前未还记录响应中包含 `dueStatus`、`dueStatusText`、`overdueDays`。
- 借阅者存在任意逾期未还图书时，`POST /circulation/borrow` 拒绝新借阅。`POST /circulation/renew` 拒绝续借已逾期的目标图书。归还逾期图书后限制自动解除。
- 旧 `POST /bookwithuser` 任意更新和 `/insertNew` 任意新增已被拒绝，避免绕过业务规则。

管理员纠正应还日期使用专用接口，只允许修改当前借阅的 `deadtime`：

```http
PUT /bookwithuser/due-date
Content-Type: application/json

{
  "operatorId": 1,
  "borrowId": 123,
  "dueDate": "2026-07-15 12:00:00"
}
```

`operatorId` 必须对应 `role=1` 的管理员，`dueDate` 必须为上海本地时间格式 `yyyy-MM-dd HH:mm:ss`。

## 11. 纯 HTTP 黑盒验收

只需 Python 3 标准库，不直连数据库，不需联网安装依赖：

```bash
BACKEND_URL=http://localhost:9090 ./verify_circulation_http.py
BACKEND_URL=http://localhost:9090 ./verify_inventory_http.py
BACKEND_URL=http://localhost:9090 ./verify_overdue_http.py
BACKEND_URL=http://localhost:9090 ADMIN_USERNAME=admin ADMIN_PASSWORD=123456 ./verify_user_management_http.py
```

`verify_overdue_http.py` 使用已有管理员和唯一的读者、两本测试图书，通过专用 HTTP 接口将应还日调整为昨天，覆盖全部逾期限制和解除流程。每项输出 `PASS` / `FAIL`，任一失败返回非零退出码；脚本结束时通过 HTTP 归还并删除测试记录、图书和读者账号。

## 12. 借书、还书、续借后端业务接口

借书、还书、续借已经收敛为三个后端事务接口。前端点击一次业务按钮时，只发送一个业务写请求，列表刷新请求不计入。请求体只传读者和图书标识，不传库存、状态、借阅时间、应还时间或续借后的日期。

### 12.1 借书

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

### 12.2 还书

```bash
curl -s -X POST "http://localhost:9090/circulation/return" \
  -H "Content-Type: application/json" \
  -d '{"readerId":25,"isbn":"TEST-ISBN-001"}'
```

后端会校验当前借阅和未归还历史是否存在，并在一个事务内更新历史记录为已归还、删除当前借阅、恢复可借数量。重复还书会失败，库存不会再次增加。

### 12.3 续借

```bash
curl -s -X POST "http://localhost:9090/circulation/renew" \
  -H "Content-Type: application/json" \
  -d '{"readerId":25,"isbn":"TEST-ISBN-001"}'
```

后端会校验当前借阅和剩余续借次数。最多续借 1 次，成功后应还日期延长 30 天且剩余续借次数变为 0；第二次续借失败，应还日期不变化。

## 13. 借还续黑盒验证脚本

脚本文件：

```text
verify_circulation_http.py
```

## 14. 一键后端现场演示

服务启动后，在项目根目录执行：

```bash
./demo_backend_verification.sh
```

脚本默认访问 `http://localhost:9090`，也支持现场透传管理员配置：

```bash
BACKEND_URL=http://localhost:9090 \
ADMIN_USERNAME=admin ADMIN_PASSWORD=123456 \
./demo_backend_verification.sh
```

`ADMIN_PASSWORD` 只有在非空时才会透传；显式设置为空字符串时，演示脚本会将其 unset，让四个 Python 脚本继续使用既有的 `admin` / `123456` fallback。

脚本会先请求 `/dashboard` 做健康检查。服务不可用时会输出明确错误并以非零状态退出；健康检查通过后按顺序运行四个既有 Python 黑盒脚本，单项失败不会阻断后续项目，并在末尾输出每项退出码与总 PASS/FAIL：

| 顺序 | 脚本 | 验证内容 | 预期 |
|---|---|---|---|
| 1 | `verify_circulation_http.py` | 借书、无库存拒绝、续借、重复续借拒绝、还书、重复还书拒绝 | 6/6 |
| 2 | `verify_inventory_http.py` | 库存初始化、借还库存、非法总数、合法扩容、并发编辑与重复借阅 | 9/9 |
| 3 | `verify_overdue_http.py` | 后端生成应还日、逾期调整、借阅/续借限制、筛选、归还解除限制 | 6/6 |
| 4 | `verify_user_management_http.py` | 新增、字段校验、登录、重复用户名、权限边界、借阅中删除保护、归还后删除 | 7/7 |

四个脚本只通过正式 HTTP API 操作临时测试数据；各自结束时都会验证并清理临时读者、图书、借阅记录和历史记录，不需要直连数据库。演示脚本本身不复制黑盒逻辑，也不写入业务数据。

如需单独确认某一项，可直接运行：

```bash
BACKEND_URL=http://localhost:9090 ./verify_circulation_http.py
BACKEND_URL=http://localhost:9090 ./verify_inventory_http.py
BACKEND_URL=http://localhost:9090 ./verify_overdue_http.py
BACKEND_URL=http://localhost:9090 ADMIN_USERNAME=admin ADMIN_PASSWORD=123456 ./verify_user_management_http.py
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

## 15. 库存数量黑盒验证脚本

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

## 16. 用户管理黑盒验收脚本

脚本文件：

```text
verify_user_management_http.py
```

该脚本使用已有管理员账号进行验收，默认尝试 `admin/admin` 和 `admin/123456`；也可显式指定：

```bash
BACKEND_URL=http://localhost:9090 ADMIN_USERNAME=admin ADMIN_PASSWORD=123456 ./verify_user_management_http.py
```

脚本只调用 HTTP，使用带时间和进程标识的唯一读者、图书和账号数据，每项输出 `PASS`/`FAIL`，失败返回非零退出码。覆盖：管理员新增普通读者、角色固定为 2、用户名/密码/姓名严格校验、读者登录、同名失败、普通读者 operator/管理员目标/旧批量删除被拒绝、有未归还时删除被拒绝且仍可登录、归还后删除成功且登录失败。脚本结束时通过 HTTP 归还并删除所有测试借阅、图书和读者数据，不创建或删除管理员。

### 用户管理接口

```http
POST /user
Content-Type: application/json

{
  "operatorId": 1,
  "username": "reader_new",
  "password": "initial123",
  "nickName": "新读者",
  "phone": "13800000000",
  "sex": "男",
  "address": "图书馆",
  "role": 2
}
```

`username` 必须是 2–32 位字母/数字/下划线，`password` 必须是 6–64 位非空白字符，`nickName` 必填。请求中的 `role` 只能为 2，后端也会强制写入 2。用户名由数据库 `uk_user_username` 保证并发不重复。

```http
DELETE /user/114?operatorId=1
```

删除只允许 `operatorId` 对应管理员、目标为普通读者且没有 `bookwithuser` 当前借阅。批量删除接口保留路径但明确拒绝，不会绕过未归还检查。项目当前没有统一 token 鉴权，`operatorId` 只能证明数据库中的角色，不能证明请求者持有该账号会话。

## 17. 常见问题

### 17.1 Maven 命令无法识别

说明 Maven 没有安装，或者没有配置环境变量。

可以检查：

```powershell
mvn -version
```

如果命令失败，需要重新安装 Maven，或将 Maven 的 `bin` 目录加入系统 `Path`。

### 17.2 后端启动失败，提示数据库连接错误

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

### 17.3 后端启动失败，提示 Public Key Retrieval is not allowed

可以检查 JDBC URL 中是否包含：

```properties
allowPublicKeyRetrieval=true
```

完整示例：

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/springboot-vue?useUnicode=true&characterEncoding=utf-8&allowMultiQueries=true&useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=GMT%2b8
```

### 17.4 前端 npm install 失败

可以尝试：

```powershell
npm install --legacy-peer-deps
```

如果依赖版本冲突，优先使用上面的命令。

### 17.5 前端页面能打开，但接口请求失败

检查后端是否已经启动。

后端地址应为：

```text
http://127.0.0.1:9090/
```

同时检查前端代理配置 `vue/vue.config.js` 中是否代理到正确端口。

### 17.6 登录失败

可能原因：

- 数据库中没有测试账号。
- 用户名或密码输入错误。
- 后端没有连接上数据库。

可以先在数据库中确认 `user` 表是否有账号数据。

## 18. 运行成功标志

当以下条件都满足时，说明项目运行成功：

- MySQL 中存在 `springboot-vue` 数据库。
- 后端服务启动在 `9090` 端口。
- 前端服务启动在 `9876` 端口。
- 浏览器能打开登录页面。
- 使用管理员或读者账号可以成功登录。
- 图书列表、借阅状态、借阅记录等页面能正常加载数据。

## 19. 新界面截图与视觉验收

需求变化 5 已将前端统一为 “Library Atlas / 馆藏运营工作台” 视觉系统。改造前后截图索引如下：

| 页面 | 改造前 | 改造后 |
|---|---|---|
| 登录页 | `images/login.png` | `acceptance/screenshots/after-login.png` |
| Dashboard | `images/dashboard.png` | `acceptance/screenshots/after-dashboard.png` |
| 图书管理 | `images/book.png` | `acceptance/screenshots/after-book.png` |
| 读者管理 | `images/reader.png` | `acceptance/screenshots/after-user.png` |

完整截图方式、1280×800 / 1024×768 响应式检查、主要页面请求和业务回归结果见：

```text
acceptance/需求5-前端风格验收.md
acceptance/screenshots/browser-check.json
```

若修改前端样式后需要重新发布静态资源，必须先重新生成并保留 `vue/dist`，再构建前端镜像：

```bash
npm run build --prefix vue
docker compose build frontend
docker compose up -d frontend
```
