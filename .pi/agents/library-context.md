# Vue-Springboot-Library 项目结构地图

> Agent 工作前必读。包含完整文件映射、API 路径、数据库结构和操作命令。

## 1. 项目概览

| 项 | 值 |
|---|----|
| 项目名 | Vue-Springboot-Library |
| 类型 | 图书馆管理系统（前后端分离） |
| 角色 | 管理员（role=1）、读者（role=2） |
| 后端 | Spring Boot 2.6.1 + MyBatis-Plus, 端口 9090 |
| 前端 | Vue 3 + Element Plus + Axios, 端口 9876 |
| 数据库 | MySQL 8.0, 库名 springboot-vue |
| 部署 | Docker Compose |

## 2. 完整文件清单

### 2.1 后端 Java 文件

```
SpringBoot/src/main/java/com/example/demo/
├── DemoApplication.java                    # 启动类
├── LoginUser.java                         # 访问计数器
├── commom/
│   ├── Result.java                        # 统一返回 {code, msg, data}
│   └── MybatisPlusConfig.java             # 分页插件配置
├── controller/
│   ├── UserController.java                # 登录/注册/读者CRUD/密码
│   ├── BookController.java                # 图书CRUD/批量删除/查询
│   ├── LendRecordController.java          # 借阅记录增删查
│   ├── LendRecordController1.java         # 还书时更新借阅记录
│   ├── BookWithUserController.java        # 当前借阅状态管理/续借
│   ├── CirculationController.java         # 借书/还书/续借事务业务接口
│   └── DashboardController.java           # 展示板统计
├── dto/
│   ├── CirculationRequest.java            # 流通业务请求 {readerId, isbn}
│   ├── DueDateAdjustmentRequest.java      # 应还日期纠正 {operatorId, borrowId, dueDate}
│   └── ReaderCreateRequest.java           # 管理员新增读者（含 operatorId）
├── entity/
│   ├── User.java                          # 对应 user 表
│   ├── Book.java                          # 对应 book 表
│   ├── LendRecord.java                    # 对应 lend_record 表
│   └── BookWithUser.java                  # 对应 bookwithuser 表
├── mapper/
│   ├── UserMapper.java                    # extends BaseMapper<User>
│   ├── BookMapper.java                    # extends BaseMapper<Book>
│   ├── LendRecordMapper.java              # extends BaseMapper<LendRecord>
│   └── BookWithUserMapper.java            # extends BaseMapper<BookWithUser>
├── service/
│   ├── CirculationService.java            # @Transactional 流通业务逻辑
│   ├── CirculationException.java          # 流通业务异常
│   ├── LoanStatusService.java             # 上海时区逾期边界与状态计算
│   └── DueDateAdjustmentService.java      # 管理员应还日期业务纠正
└── utils/
    └── TokenUtils.java                    # JWT Token 生成
```

### 2.2 前端 Vue 文件

```
vue/src/
├── main.js                                # 入口，挂载 Element Plus
├── App.vue                                # 根组件
├── router/index.js                        # 路由定义（7 个页面 + login/register）
├── store/index.js                         # Vuex 状态管理
├── utils/request.js                       # Axios 实例，baseURL='/api'
├── layout/Layout.vue                      # 主布局（Header + Aside + 内容区）
├── components/
│   ├── Aside.vue                          # 侧边菜单（按角色显示）
│   ├── Header.vue                         # 顶栏（用户信息+登出）
│   └── Validate.vue                       # 表单验证组件
├── views/
│   ├── Login.vue                          # 登录页 → POST /user/login
│   ├── Register.vue                       # 注册页 → POST /user/register
│   ├── Dashboard.vue                      # 展示板 → GET /dashboard
│   ├── User.vue                           # 读者管理 → GET/POST/PUT/DELETE /user
│   ├── Book.vue                           # 图书管理+借阅 → /book
│   ├── LendRecord.vue                     # 借阅记录 → /LendRecord
│   ├── BookWithUser.vue                   # 当前借阅+续借 → /bookwithuser
│   ├── Person.vue                         # 个人信息 → PUT /user
│   └── Password.vue                       # 修改密码 → PUT /user/password
└── assets/
    ├── css/global.css, style.css
    └── icon/
```

### 2.3 其他重要文件

| 文件 | 作用 |
|------|------|
| `sql/springboot-vue.sql` | 数据库建表+初始数据 |
| `sql/migrations/20260716_overdue_management.sql` | 已有数据库的应还日期非空约束与筛选索引迁移 |
| `sql/migrations/20260716_user_management.sql` | 已有数据库的用户名唯一约束幂等迁移；重复数据 fail-fast |
| `verify_user_management_http.py` | 管理员新增/删除读者纯 HTTP 黑盒验收 |
| `SpringBoot/pom.xml` | Maven 依赖 |
| `vue/vue.config.js` | Vue CLI 配置（含 /api 代理到 localhost:9090） |
| `docker-compose.yml` | 全栈容器部署 |
| `Dockerfile.backend` | 后端镜像构建 |
| `Dockerfile.frontend` | 前端 nginx 镜像构建 |
| `nginx.conf` | 前端 nginx 配置 |

## 3. 完整 API 路径映射

### UserController (`/user`)

| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| POST | /user/register | 注册 | body: User |
| POST | /user/login | 登录 | body: {username, password} |
| POST | /user | 管理员新增普通读者 | body: `{operatorId, username, password, nickName, phone?, sex?, address?, role:2}` |
| PUT | /user/password | 修改密码 | ?id=&password2= |
| PUT | /user | 修改用户信息 | body: User |
| POST | /user/deleteBatch | 批量删除 | 已停用并明确拒绝，避免绕过未归还检查 |
| DELETE | /user/{id} | 管理员删除普通读者 | `?operatorId=`；拒绝管理员目标和存在当前借阅的读者 |
| GET | /user | 读者分页查询 | ?pageNum=&pageSize=&search= |
| GET | /user/usersearch | 读者多条件查询 | ?search1=&search2=&search3=&search4= |

### BookController (路径分散)

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /book | 新增图书（必须提交正整数 totalCount；availableCount 由后端初始化） |
| PUT | /book | 更新图书基础信息和馆藏总数（availableCount 由后端按已借出数重算） |
| DELETE | /book/{id} | 删除图书 |
| POST | /book/deleteBatch | 批量删除 |
| GET | /book | 分页查询 |

### LendRecordController (`/LendRecord`)

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /LendRecord | 新增借阅记录 |
| GET | /LendRecord | 分页查询；`overdueOnly=true` 筛选逾期未还并附带应还日期/状态/逾期天数 |
| DELETE | /LendRecord/{readerId}/{isbn}/{borrownum} | 删除 |
| POST | /LendRecord/deleteBatch | 批量删除 |
| GET | /LendRecord/status | 查询归还状态的记录 |

### LendRecordController1（还书更新）

| 方法 | 路径 | 功能 |
|------|------|------|
| PUT | /LendRecord/更新 | 还书时更新借阅记录状态和归还时间 |

### BookWithUserController (`/bookwithuser`)

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /bookwithuser/insertNew | 已拒绝直写，当前借阅只能通过借书业务接口创建 |
| GET | /bookwithuser | 分页查询；返回 `dueStatus`/`dueStatusText`/`overdueDays`，支持 `overdueOnly=true` |
| POST | /bookwithuser/deleteRecord | 删除一条当前借阅 |
| POST | /bookwithuser/deleteRecords | 批量删除当前借阅 |
| POST | /bookwithuser | 已拒绝任意字段直写 |
| PUT | /bookwithuser/due-date | 管理员专用应还日期纠正；body: `{operatorId, borrowId, dueDate}` |

### CirculationController (`/circulation`)

| 方法 | 路径 | 功能 | 请求体 |
|------|------|------|--------|
| POST | /circulation/borrow | 借书事务业务接口 | `{readerId, isbn}` |
| POST | /circulation/return | 还书事务业务接口 | `{readerId, isbn}` |
| POST | /circulation/renew | 续借事务业务接口 | `{readerId, isbn}` |

说明：三个接口只接收读者和图书标识。后端统一校验库存、当前借阅、未归还记录和续借次数，并在同一事务内更新 `book`、`bookwithuser`、`lend_record`。前端页面点击借书、还书、续借时只发一个业务写请求，列表刷新请求不计入。

逾期规则：借书时后端以 `Asia/Shanghai` 生成借书时间及其后 30 个日历日的应还时间。应还日期早于当前上海自然日才算逾期，“昨天”稳定计为 1 天，今天到期不逾期。距应还日 0–3 天为 `DUE_SOON`，更远为 `NORMAL`，已逾期为 `OVERDUE`。存在任意逾期未还时拒绝借新书，逾期目标拒绝续借，归还后自动解除。

### DashboardController (`/dashboard`)

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /dashboard | 返回 {visitCount, userCount, bookCount, lendRecordCount} |

## 4. 数据库完整结构

### user 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint, PK, AUTO | 用户 ID |
| username | varchar(255), UNIQUE | 用户名；`uk_user_username` 保证并发新增不会产生重复账号 |
| nick_name | varchar(255) | 姓名 |
| password | varchar(255) | 密码 |
| sex | varchar(1) | 性别 |
| address | varchar(255) | 地址 |
| phone | varchar(255) | 电话 |
| role | int | 1=管理员, 2=读者 |

### book 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint, PK, AUTO | 图书 ID |
| isbn | varchar(255), UNIQUE | 图书编号 |
| name | varchar(255) | 书名 |
| price | decimal(10,2) | 价格 |
| author | varchar(255) | 作者 |
| publisher | varchar(255) | 出版社 |
| create_time | date | 出版时间 |
| status | varchar(1) | 0=已借出, 1=可借 |
| borrownum | int | 累计借阅次数 |
| total_count | int | 馆藏总数 |
| available_count | int | 可借数量 |

### lend_record 表
| 字段 | 类型 | 说明 |
|------|------|------|
| reader_id | bigint | 读者 ID |
| isbn | varchar(255) | 图书编号 |
| bookname | varchar(255) | 书名 |
| lend_time | datetime | 借书时间 |
| return_time | datetime | 还书时间 |
| status | varchar(1) | 0=未还, 1=已还 |
| borrownum | int | 借阅次数编号 |

### bookwithuser 表
| 字段 | 类型 | 说明 |
|------|------|------|
| borrow_id | bigint, PK, AUTO | 当前借阅 ID |
| id | bigint | 读者 ID |
| isbn | varchar(255) | 图书编号 |
| book_name | varchar(255) | 书名 |
| nick_name | varchar(255) | 读者姓名 |
| lendtime | datetime | 借阅时间 |
| deadtime | datetime, NOT NULL | 应归还时间；每条当前借阅必须存在 |
| prolong | int | 续借剩余次数 |

约束：`bookwithuser` 使用技术主键 `borrow_id`，并通过唯一索引 `(id, isbn)` 保证同一读者不能重复借同一 ISBN；不同读者可以同时借同一 ISBN 的不同馆藏。`deadtime` 为 `NOT NULL`，迁移在 ALTER 前发现 NULL 会 `SIGNAL` 中止，不会在查询层伪造状态。

## 5. Entity ↔ 数据库字段映射注意事项

- User: `nickName`(Java) ↔ `nick_name`(DB), MyBatis-Plus 自动驼峰转换
- Book: `createTime` ↔ `create_time`, `totalCount` ↔ `total_count`, `availableCount` ↔ `available_count`, `borrownum` ↔ `borrownum`
- LendRecord: `readerId` ↔ `reader_id`, `lendTime` ↔ `lend_time`, `returnTime` ↔ `return_time`, `bookname` ↔ `bookname`
- BookWithUser: `borrowId` ↔ `borrow_id`, `bookName` ↔ `book_name`, `nickName` ↔ `nick_name`

## 6. 已知设计问题（不要擅自修复，除非用户要求）

1. 多数旧 Controller 仍直接调 Mapper；借书/还书/续借新流程已新增 `CirculationService`
2. 旧借还书拆分接口仍存在；新页面流程应使用 `/circulation/borrow`、`/circulation/return`、`/circulation/renew` 三个后端事务接口
3. Token 生成但未在前端请求头中携带，后端无统一鉴权拦截器
4. `book.status` 仍是列表展示用的汇总状态：`available_count > 0` 时为 1，否则为 0；真实库存以 `total_count` / `available_count` 为准
5. 用户新增/删除通过 `operatorId` 查询数据库确认管理员，能拒绝普通读者和前端绕过，但因无统一 token 鉴权，不能证明请求发起者实际持有该管理员会话

## 7. 操作命令

### 本地开发
```bash
# 后端编译
mvn package -f SpringBoot/pom.xml -DskipTests

# 后端启动（确保 MySQL 运行且库已建）
java -jar SpringBoot/target/demo-0.0.1-SNAPSHOT.jar

# 前端安装依赖
cd vue && npm install

# 前端开发服务器 (http://localhost:9876)
cd vue && npm run serve

# 前端生产构建
cd vue && npm run build
```

### Docker Compose 部署
```bash
docker-compose up -d          # 启动全部服务
docker-compose down           # 停止
docker-compose logs backend   # 查看后端日志
docker-compose restart backend # 重启后端
```

### 验证脚本
```bash
./dev.sh verify    # 运行核心流程冒烟测试
BACKEND_URL=http://localhost:9090 ./verify_circulation_http.py  # 借书/还书/续借事务黑盒验证
BACKEND_URL=http://localhost:9090 ./verify_inventory_http.py    # 库存数量黑盒验证
BACKEND_URL=http://localhost:9090 ./verify_overdue_http.py      # 逾期管理与限制黑盒验证
BACKEND_URL=http://localhost:9090 ADMIN_USERNAME=admin ADMIN_PASSWORD=123456 ./verify_user_management_http.py  # 用户管理黑盒验证
```

### 现有数据库迁移
```bash
mysql -uroot -p springboot-vue < sql/migrations/20260716_inventory_counts.sql
mysql -uroot -p springboot-vue < sql/migrations/20260716_overdue_management.sql
mysql -uroot -p springboot-vue < sql/migrations/20260716_user_management.sql
```

库存迁移会给 `book.isbn` 添加唯一索引，给库存数量添加检查约束，并将 `bookwithuser` 从 `book_name` 主键改为 `borrow_id` 技术主键 + `(id, isbn)` 唯一约束。逾期迁移会先拒绝任意 `deadtime IS NULL` 数据，然后幂等将字段改为 `NOT NULL` 并添加 `idx_bookwithuser_deadtime`。用户管理迁移会在 ALTER 前检查重复用户名，发现重复即 `SIGNAL` 中止；数据安全时幂等添加 `uk_user_username`。

### 测试账号
- 管理员: admin / admin
- 读者: 需要自行在数据库查看或通过注册创建
