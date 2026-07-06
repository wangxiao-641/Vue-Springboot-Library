# Vue-Springboot-Library 项目指引

## 读到需求后先做什么

收到任何关于本项目的任务后，**第一步**读 `.pi/agents/library-context.md`。这是项目的完整地图：所有 API 路径、数据库表结构、前后端文件清单、常用命令都在里面。不要在没读完地图的情况下开始改代码。

## 改代码时用什么 agent

`.pi/agents/library-worker.md` 是本项目的专属修改 agent 定义。它配置好了技术栈认知、改动纪律、验证流程。复杂修改任务通过 `subagent` 工具分派给它，不要自己裸写。

## 模板

`.pi/agents/templates/` 下有七个操作模板：
- `add-api.md` — 新增后端 API
- `add-db-table.md` — 新增数据库表 + Entity + Mapper
- `add-page.md` — 新增前端页面
- `add-feature.md` — 新增完整功能（跨前后端+数据库）
- `refactor-service.md` — 重构 Service 层
- `fix-bug.md` — 修复 Bug 的排查和改动流程
- `acceptance-checklist.md` — 验收清单模板（改动完成后必须填写）

新增功能时参考对应模板。改动完成后，按 `acceptance-checklist.md` 逐项验收。

## 项目速览

| 项 | 值 |
|---|----|
| 后端 | SpringBoot 2.6.1 + MyBatis-Plus，端口 9090 |
| 前端 | Vue 3 + Element Plus，端口 9876 |
| 数据库 | MySQL 8.0，库名 springboot-vue，脚本在 `sql/springboot-vue.sql` |
| 部署 | Docker Compose |
| 验证 | `./dev.sh verify` 冒烟 / `./dev.sh verify-full` 完整验收 |
