# 变更模板：新增前后端完整功能

> 适用场景：用户要求新增一个功能模块，涉及数据库表 + 后端 API + 前端页面。按此模板跨越全栈，一步到位。

## 前置分析

记下以下决策再动手：

- 功能名称：________
- 核心数据字段：________
- 是否需要新表？（是/否，表名：________）
- 如果不需要新表，改动哪些现有表？________
- 是否需要新页面？（是/否，页面路径：________）
- 是否需要菜单入口？（是/否，菜单中的位置：________）
- 权限：仅管理员 / 仅读者 / 两者都可访问？
- 是否需要新 Controller？（是/否，路径前缀：________）
- 是否需要新 Service？（是/否）

## 执行步骤（从上到下依次完成）

### 阶段一：数据层

> 参考模板：`add-db-table.md`

- [ ] 编写建表 SQL，追加到 `sql/springboot-vue.sql`
- [ ] 在 Docker MySQL 中执行建表
- [ ] 新建 Entity 实体类
- [ ] 新建 Mapper 接口
- [ ] 编译验证：`cd SpringBoot && mvn package -DskipTests -q`

### 阶段二：后端 API

> 参考模板：`add-api.md`

- [ ] 新建或修改 Controller，提供 CRUD 接口
- [ ] 标准接口清单：
  - `GET /xxx?pageNum=&pageSize=&search=` — 分页+搜索
  - `POST /xxx` — 新增
  - `PUT /xxx` — 更新（或 `POST /xxx/update`）
  - `DELETE /xxx/{id}` — 删除
- [ ] 如果操作涉及多表，添加 `@Transactional`
- [ ] API 验证：用 curl 测试每个接口返回 200 且 `code=0`

```bash
# 验证新增
curl -s -X POST http://localhost:9090/xxx \
  -H 'Content-Type: application/json' \
  -d '{"name":"test"}' | python3 -c "import sys,json; print(json.load(sys.stdin).get('code'))"
# 期望输出: 0

# 验证查询
curl -s "http://localhost:9090/xxx?pageNum=1&pageSize=5" | \
  python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('code'), 'total:', r.get('data',{}).get('total'))"
```

### 阶段三：前端页面

> 参考模板：`add-page.md`

- [ ] 在 `vue/src/views/` 下新建 Vue 页面组件
- [ ] 在 `vue/src/router/index.js` 添加路由
- [ ] 如需菜单入口，修改 `vue/src/components/Aside.vue`
- [ ] 前端编译验证：`cd vue && npm run build 2>&1 | tail -3`

### 阶段四：端到端验收

- [ ] 确保前后端都在运行
- [ ] 用 `./dev.sh verify` 确认原有功能不受影响
- [ ] 手动验证新功能：
  - [ ] 访问页面，确认正常渲染
  - [ ] 新增一条数据，确认出现在表格中
  - [ ] 搜索功能正常
  - [ ] 编辑和删除正常
  - [ ] 权限控制正确（不该看到的人看不到）

### 阶段五：文档更新

- [ ] 更新 `library-context.md`：API 路径表、数据库表、前端页面清单
- [ ] 如有新模板，总结本次改动的模式
