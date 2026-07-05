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
│   └── DashboardController.java           # 展示板统计
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
| POST | /user | 新增读者 | body: User |
| PUT | /user/password | 修改密码 | ?id=&password2= |
| PUT | /user | 修改用户信息 | body: User |
| POST | /user/deleteBatch | 批量删除 | body: [id, ...] |
| DELETE | /user/{id} | 删除单个用户 | path: id |
| GET | /user | 读者分页查询 | ?pageNum=&pageSize=&search= |
| GET | /user/usersearch | 读者多条件查询 | ?search1=&search2=&search3=&search4= |

### BookController (路径分散)

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /book | 新增图书 |
| PUT | /book | 更新图书（含借/还书状态变更） |
| DELETE | /book/{id} | 删除图书 |
| POST | /book/deleteBatch | 批量删除 |
| GET | /book | 分页查询 |

### LendRecordController (`/LendRecord`)

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /LendRecord | 新增借阅记录 |
| GET | /LendRecord | 分页查询 |
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
| POST | /bookwithuser/insertNew | 新增当前借阅 |
| GET | /bookwithuser | 分页查询 |
| POST | /bookwithuser/deleteBatch | 批量删除 |
| DELETE | /bookwithuser/{id}/{isbn} | 还书后删除 |
| PUT | /bookwithuser/update | 续借（延长 deadtime + prolong-1） |

### DashboardController (`/dashboard`)

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /dashboard | 返回 {visitCount, userCount, bookCount, lendRecordCount} |

## 4. 数据库完整结构

### user 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint, PK, AUTO | 用户 ID |
| username | varchar(255) | 用户名 |
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
| isbn | varchar(255) | 图书编号 |
| name | varchar(255) | 书名 |
| price | decimal(10,2) | 价格 |
| author | varchar(255) | 作者 |
| publisher | varchar(255) | 出版社 |
| create_time | date | 出版时间 |
| status | varchar(1) | 0=已借出, 1=可借 |
| borrownum | int | 累计借阅次数 |

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
| id | bigint | 读者 ID |
| isbn | varchar(255) | 图书编号 |
| book_name | varchar(255), PK | 书名（注意：以此为 PK 有设计问题） |
| nick_name | varchar(255) | 读者姓名 |
| lendtime | datetime | 借阅时间 |
| deadtime | datetime | 应归还时间 |
| prolong | int | 续借剩余次数 |

## 5. Entity ↔ 数据库字段映射注意事项

- User: `nickName`(Java) ↔ `nick_name`(DB), MyBatis-Plus 自动驼峰转换
- Book: `createTime` ↔ `create_time`, `borrownum` ↔ `borrownum`
- LendRecord: `readerId` ↔ `reader_id`, `lendTime` ↔ `lend_time`, `returnTime` ↔ `return_time`, `bookname` ↔ `bookname`
- BookWithUser: `bookName` ↔ `book_name`, `nickName` ↔ `nick_name`

## 6. 已知设计问题（不要擅自修复，除非用户要求）

1. Controller 直接调 Mapper，没有 Service 层
2. 借还书流程靠前端串行调用多个 API，没有事务保证
3. `bookwithuser` 表用 `book_name` 做主键，同名书、多副本场景有问题
4. Token 生成但未在前端请求头中携带，后端无统一鉴权拦截器
5. `book.status` 只支持单本借出/可借，不支持多副本

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
```

### 测试账号
- 管理员: admin / admin
- 读者: 需要自行在数据库查看或通过注册创建
