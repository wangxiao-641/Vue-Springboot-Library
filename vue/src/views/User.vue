<template>
  <div class="home" style="padding: 10px">
    <div style="margin: 10px 0">
      <el-form :inline="true" size="small">
        <el-form-item label="读者编号">
          <el-input v-model="search1" placeholder="请输入读者编号" clearable>
            <template #prefix><el-icon class="el-input__icon"><search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="search2" placeholder="请输入姓名" clearable>
            <template #prefix><el-icon class="el-input__icon"><search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="电话号码">
          <el-input v-model="search3" placeholder="请输入电话号码" clearable>
            <template #prefix><el-icon class="el-input__icon"><search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="search4" placeholder="请输入地址" clearable>
            <template #prefix><el-icon class="el-input__icon"><search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="load" size="mini">查询</el-button>
        </el-form-item>
        <el-form-item>
          <el-button size="mini" type="danger" @click="clear">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div style="margin: 10px 0" v-if="user.role === 1">
      <el-button type="primary" size="mini" @click="add">新增读者</el-button>
    </div>

    <el-table :data="tableData" stripe :border="true">
      <el-table-column prop="id" label="读者编号" sortable />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="nickName" label="姓名" />
      <el-table-column prop="phone" label="电话号码" />
      <el-table-column prop="sex" label="性别" />
      <el-table-column prop="address" label="地址" />
      <el-table-column v-if="user.role === 1" fixed="right" label="操作">
        <template #default="scope">
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-popconfirm
            title="确定删除该读者？有未归还图书时将无法删除。"
            confirm-button-text="确定删除"
            cancel-button-text="取消"
            @confirm="handleDelete(scope.row.id)"
          >
            <template #reference>
              <el-button type="danger" size="mini">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin: 10px 0">
      <el-pagination
        v-model:currentPage="currentPage"
        :page-sizes="[5, 10, 20]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑读者信息' : '新增读者'" width="34%">
      <el-form
        ref="userForm"
        :model="form"
        :rules="form.id ? editRules : createRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" maxlength="32" placeholder="2-32位字母、数字或下划线" />
        </el-form-item>
        <el-form-item v-if="!form.id" label="初始密码" prop="password">
          <el-input v-model="form.password" type="password" show-password maxlength="64" placeholder="6-64位，不能包含空白字符" />
        </el-form-item>
        <el-form-item label="姓名" prop="nickName">
          <el-input v-model="form.nickName" maxlength="50" placeholder="请输入读者姓名" />
        </el-form-item>
        <el-form-item label="电话号码" prop="phone">
          <el-input v-model="form.phone" maxlength="20" placeholder="6-20位数字，可包含+或-" />
        </el-form-item>
        <el-form-item label="性别" prop="sex">
          <el-radio v-model="form.sex" label="男">男</el-radio>
          <el-radio v-model="form.sex" label="女">女</el-radio>
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" type="textarea" maxlength="255" show-word-limit />
        </el-form-item>
        <el-form-item v-if="!form.id" label="账号角色">
          <el-tag type="info">普通读者</el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="save">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import request from "../utils/request";
import { ElMessage } from "element-plus";

const usernameRule = {
  pattern: /^[A-Za-z0-9_]{2,32}$/,
  message: "用户名必须为2到32位字母、数字或下划线",
  trigger: "blur",
};

export default {
  name: "User",
  created() {
    const userStr = sessionStorage.getItem("user") || "{}";
    this.user = JSON.parse(userStr);
    this.load();
  },
  data() {
    return {
      form: {},
      dialogVisible: false,
      search1: "",
      search2: "",
      search3: "",
      search4: "",
      total: 0,
      currentPage: 1,
      pageSize: 10,
      tableData: [],
      user: {},
      createRules: {
        username: [
          { required: true, message: "请输入用户名", trigger: "blur" },
          usernameRule,
        ],
        password: [
          { required: true, message: "请输入初始密码", trigger: "blur" },
          { pattern: /^\S{6,64}$/, message: "初始密码必须为6到64位非空白字符", trigger: "blur" },
        ],
        nickName: [
          { required: true, message: "请输入姓名", trigger: "blur" },
          { max: 50, message: "姓名不能超过50个字符", trigger: "blur" },
        ],
        phone: [
          { pattern: /^$|^[0-9+\-]{6,20}$/, message: "电话号码格式不正确", trigger: "blur" },
        ],
      },
      editRules: {
        username: [
          { required: true, message: "请输入用户名", trigger: "blur" },
          usernameRule,
        ],
        nickName: [
          { required: true, message: "请输入姓名", trigger: "blur" },
          { max: 50, message: "姓名不能超过50个字符", trigger: "blur" },
        ],
        phone: [
          { pattern: /^$|^[0-9+\-]{6,20}$/, message: "电话号码格式不正确", trigger: "blur" },
        ],
      },
    };
  },
  methods: {
    load() {
      request.get("user/usersearch", {
        params: {
          pageNum: this.currentPage,
          pageSize: this.pageSize,
          search1: this.search1,
          search2: this.search2,
          search3: this.search3,
          search4: this.search4,
        },
      }).then((res) => {
        if (res.code === "0") {
          this.tableData = res.data.records;
          this.total = res.data.total;
        } else {
          ElMessage.error(res.msg);
        }
      });
    },
    clear() {
      this.search1 = "";
      this.search2 = "";
      this.search3 = "";
      this.search4 = "";
      this.currentPage = 1;
      this.load();
    },
    handleDelete(id) {
      request.delete("user/" + id, {
        params: { operatorId: this.user.id },
      }).then((res) => {
        if (res.code === "0") {
          ElMessage.success("删除成功");
          this.load();
        } else {
          ElMessage.error(res.msg);
        }
      });
    },
    add() {
      this.form = { role: 2, phone: "", sex: "", address: "" };
      this.dialogVisible = true;
      this.$nextTick(() => this.$refs.userForm && this.$refs.userForm.clearValidate());
    },
    save() {
      this.$refs.userForm.validate((valid) => {
        if (!valid) return;
        if (this.form.id) {
          request.put("/user", this.form).then((res) => {
            if (res.code === "0") {
              ElMessage.success("更新成功");
              this.dialogVisible = false;
              this.load();
            } else {
              ElMessage.error(res.msg);
            }
          });
          return;
        }

        const payload = {
          operatorId: this.user.id,
          username: this.form.username,
          password: this.form.password,
          nickName: this.form.nickName,
          phone: this.form.phone,
          sex: this.form.sex,
          address: this.form.address,
          role: 2,
        };
        request.post("/user", payload).then((res) => {
          if (res.code === "0") {
            ElMessage.success("读者新增成功");
            this.dialogVisible = false;
            this.load();
          } else {
            ElMessage.error(res.msg);
          }
        });
      });
    },
    handleEdit(row) {
      this.form = JSON.parse(JSON.stringify(row));
      this.dialogVisible = true;
      this.$nextTick(() => this.$refs.userForm && this.$refs.userForm.clearValidate());
    },
    handleSizeChange(pageSize) {
      this.pageSize = pageSize;
      this.currentPage = 1;
      this.load();
    },
    handleCurrentChange(pageNum) {
      this.currentPage = pageNum;
      this.load();
    },
  },
};
</script>
