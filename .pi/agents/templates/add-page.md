# 变更模板：新增前端页面

## 前置检查

- [ ] 后端对应的 API 是否已就绪（Controller + Mapper + Entity）
- [ ] 确定新页面的路由路径、是否显示在侧边菜单、对哪些角色可见

## 改动清单（按顺序执行）

### 1. Vue 页面组件

在 `vue/src/views/` 下新建 Vue 文件。使用以下模板：

```vue
<template>
  <div style="padding: 10px">
    <!-- 搜索区 -->
    <div style="margin: 10px 0">
      <el-form inline size="small">
        <el-form-item label="搜索">
          <el-input v-model="search" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="load" size="mini">查询</el-button>
        </el-form-item>
        <el-form-item>
          <el-button size="mini" @click="clear">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮 -->
    <div style="margin: 10px 0">
      <el-button type="primary" @click="add">新增</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table :data="tableData" stripe border>
      <el-table-column prop="name" label="名称" />
      <!-- 操作列 -->
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="mini" @click="edit(scope.row)">编辑</el-button>
          <el-popconfirm title="确认删除?" @confirm="del(scope.row.id)">
            <template #reference>
              <el-button size="mini" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div style="margin: 10px 0">
      <el-pagination
        v-model:currentPage="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="load"
        @current-change="load"
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" title="信息" width="30%">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="save">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import request from "@/utils/request";

export default {
  name: 'NewPage',
  data() {
    return {
      user: JSON.parse(sessionStorage.getItem("user") || "{}"),
      search: '',
      currentPage: 1,
      pageSize: 10,
      total: 0,
      tableData: [],
      dialogVisible: false,
      form: {}
    }
  },
  created() {
    this.load()
  },
  methods: {
    load() {
      request.get("/xxx", {
        params: { pageNum: this.currentPage, pageSize: this.pageSize, search: this.search }
      }).then(res => {
        this.tableData = res.data.records
        this.total = res.data.total
      })
    },
    clear() { this.search = ''; this.load() },
    add() { this.form = {}; this.dialogVisible = true },
    edit(row) { this.form = JSON.parse(JSON.stringify(row)); this.dialogVisible = true },
    save() {
      request.post("/xxx", this.form).then(res => {
        if (res.code === '0') {
          this.$message.success("操作成功")
          this.dialogVisible = false
          this.load()
        } else {
          this.$message.error(res.msg)
        }
      })
    },
    del(id) {
      request.delete("/xxx/" + id).then(res => {
        if (res.code === '0') {
          this.$message.success("删除成功")
          this.load()
        } else {
          this.$message.error(res.msg)
        }
      })
    }
  }
}
</script>
```

**使用 Element Plus 组件时必须按以下方式**：
- 表格：`<el-table>` + `<el-table-column>` （不是 `el-table-column` 自闭合）
- 弹窗：`<el-dialog v-model="dialogVisible">`（不是 `:visible.sync`）
- 分页：`v-model:currentPage`、`v-model:page-size`（不是 `:current-page.sync`）
- 表单：`<el-form>` + `<el-form-item>`
- 日期：`<el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" />`
- API 调用统一通过 `import request from "@/utils/request"`，不直接用 axios

### 2. 路由注册

在 `vue/src/router/index.js` 中添加：

```js
{
  path: 'newpage',
  name: 'NewPage',
  component: () => import("@/views/NewPage")
}
```

**注意**：
- 需要登录才能访问的页面放在 `Layout` 的 `children` 数组里
- 不需要布局的页面（如登录/注册）放在顶层路由数组里

### 3. 菜单项（如需要）

如果新页面需要显示在侧边菜单，修改 `vue/src/components/Aside.vue`：

```html
<el-menu-item index="newpage" v-if="user.role == 1">
  <span>新页面</span>
</el-menu-item>
```

### 4. 前端编译验证

```bash
cd vue && npm run build 2>&1 | tail -3
# 期望: 无 error，输出 dist 目录
```

### 5. 上下文文档更新

- [ ] 在 `library-context.md` 的前端文件清单和 API 映射表格中添加新页面信息

## 跨页面关系注意事项

- 侧边菜单点击通过 `index` 属性匹配 `router/index.js` 中的 `path`
- `request.js` 中 baseURL 是 `/api`，`vue.config.js` 将 `/api` 代理到 `http://localhost:9090`
- 所有页面从 `sessionStorage.getItem("user")` 读取当前登录用户信息
- `user.role == 1` 为管理员，`user.role == 2` 为读者
