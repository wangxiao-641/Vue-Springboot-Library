<template>
  <div class="page-shell data-page loan-page">
    <PageHeader
      title="当前借阅"
      :description="
        user.role == 1
          ? '查看全部在借图书，处理逾期与应还日期纠正。'
          : '查看你的借阅期限、到期状态与续借机会。'
      "
    />
    <el-alert
      v-if="hasOverdue"
      class="status-note"
      title="存在逾期未还图书，逾期期间不能借新书或续借逾期图书，请尽快归还。"
      type="error"
      :closable="false"
      show-icon
    />
    <div class="surface-card toolbar-card">
      <el-form :inline="true"
        ><el-form-item label="图书编号"
          ><el-input
            v-model="search1"
            placeholder="输入 ISBN"
            clearable /></el-form-item
        ><el-form-item label="图书名称"
          ><el-input
            v-model="search2"
            placeholder="输入书名"
            clearable /></el-form-item
        ><el-form-item v-if="user.role == 1" label="借阅者"
          ><el-input
            v-model="search3"
            placeholder="输入昵称"
            clearable /></el-form-item
        ><el-form-item v-if="user.role == 1"
          ><el-checkbox v-model="overdueOnly"
            >仅看逾期未还</el-checkbox
          ></el-form-item
        ><el-form-item
          ><el-button type="primary" @click="load"
            ><el-icon><Search /></el-icon>查询</el-button
          ><el-button @click="clear">重置</el-button></el-form-item
        ></el-form
      >
    </div>
    <div v-if="user.role == 1" class="action-row">
      <el-popconfirm title="确认删除选中的借阅记录？" @confirm="deleteBatch"
        ><template #reference
          ><el-button type="danger" plain
            ><el-icon><Delete /></el-icon>批量删除</el-button
          ></template
        ></el-popconfirm
      ><span class="muted">日期调整仅用于业务纠正</span>
    </div>
    <div class="surface-card table-card">
      <div class="table-scroll">
        <el-table
          :data="tableData"
          @selection-change="handleSelectionChange"
          empty-text="暂无当前借阅"
        >
          <el-table-column
            v-if="user.role == 1"
            type="selection"
            width="48"
          /><el-table-column
            prop="isbn"
            label="图书编号"
            min-width="135"
            sortable
          /><el-table-column
            prop="bookName"
            label="图书名称"
            min-width="160"
          /><el-table-column
            prop="nickName"
            label="借阅者"
            min-width="100"
          /><el-table-column
            prop="lendtime"
            label="借阅时间"
            min-width="165"
          /><el-table-column
            prop="deadtime"
            label="应还日期"
            min-width="165"
          /><el-table-column label="借阅状态" width="112"
            ><template #default="scope"
              ><el-tag :type="statusTagType(scope.row.dueStatus)">{{
                scope.row.dueStatusText
              }}</el-tag></template
            ></el-table-column
          ><el-table-column label="逾期" width="110"
            ><template #default="scope"
              ><span
                v-if="scope.row.dueStatus === 'OVERDUE'"
                class="overdue-text"
                >{{ scope.row.overdueDays }} 天</span
              ><span v-else class="muted">—</span></template
            ></el-table-column
          ><el-table-column
            prop="prolong"
            label="可续借"
            width="90"
          /><el-table-column
            fixed="right"
            label="操作"
            :width="user.role == 1 ? 190 : 90"
            ><template #default="scope"
              ><template v-if="user.role == 1"
                ><el-button link type="primary" @click="handleEdit(scope.row)"
                  >调整日期</el-button
                ><el-popconfirm
                  title="确认删除？"
                  @confirm="handleDelete(scope.row)"
                  ><template #reference
                    ><el-button link type="danger">删除</el-button></template
                  ></el-popconfirm
                ></template
              ><el-popconfirm
                v-else
                title="确认续借？续借后延长30天。"
                @confirm="handlereProlong(scope.row)"
                ><template #reference
                  ><el-button
                    link
                    type="primary"
                    :disabled="
                      scope.row.prolong == 0 ||
                      scope.row.dueStatus === 'OVERDUE'
                    "
                    >续借</el-button
                  ></template
                ></el-popconfirm
              ></template
            ></el-table-column
          >
        </el-table>
      </div>
      <div class="pagination-row">
        <el-pagination
          v-model:currentPage="currentPage"
          :page-sizes="[5, 10, 20]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
    <el-dialog
      v-model="dialogVisible2"
      title="调整应还日期"
      width="min(480px, 90vw)"
      ><el-form :model="form" label-width="100px"
        ><el-form-item label="借阅信息"
          ><b>{{ form.nickName }}</b
          >&nbsp; / &nbsp;{{ form.bookName }}</el-form-item
        ><el-form-item label="应还日期" required
          ><el-date-picker
            v-model="form.deadtime"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择应还日期"
            style="width: 100%" /></el-form-item></el-form
      ><template #footer
        ><el-button @click="dialogVisible2 = false">取消</el-button
        ><el-button type="primary" @click="save">保存日期</el-button></template
      ></el-dialog
    >
  </div>
</template>
<script>
import request from "../utils/request";
import { ElMessage } from "element-plus";
import PageHeader from "../components/PageHeader";
export default {
  name: "bookwithuser",
  components: { PageHeader },
  created() {
    this.user = JSON.parse(sessionStorage.getItem("user") || "{}");
    this.load();
  },
  data() {
    return {
      form: {},
      dialogVisible2: false,
      search1: "",
      search2: "",
      search3: "",
      overdueOnly: false,
      total: 10,
      currentPage: 1,
      pageSize: 10,
      tableData: [],
      user: {},
      forms: [],
    };
  },
  computed: {
    hasOverdue() {
      return this.tableData.some((i) => i.dueStatus === "OVERDUE");
    },
  },
  methods: {
    handleSelectionChange(val) {
      this.forms = val;
    },
    deleteBatch() {
      if (!this.forms.length) return ElMessage.warning("请选择数据！");
      request.post("bookwithuser/deleteRecords", this.forms).then((res) => {
        if (res.code === "0") {
          ElMessage.success("批量删除成功");
          this.load();
        } else ElMessage.error(res.msg);
      });
    },
    load() {
      const params = {
        pageNum: this.currentPage,
        pageSize: this.pageSize,
        search1: this.search1,
        search2: this.search2,
        search3: this.user.role == 1 ? this.search3 : this.user.id,
        overdueOnly: this.user.role == 1 ? this.overdueOnly : false,
      };
      request.get("/bookwithuser", { params }).then((res) => {
        this.tableData = res.data.records;
        this.total = res.data.total;
      });
    },
    clear() {
      this.search1 = "";
      this.search2 = "";
      this.search3 = "";
      this.overdueOnly = false;
      this.currentPage = 1;
      this.load();
    },
    handleDelete(row) {
      request
        .post("bookwithuser/deleteRecord", JSON.parse(JSON.stringify(row)))
        .then((res) => {
          res.code == 0
            ? ElMessage.success("删除成功")
            : ElMessage.error(res.msg);
          this.load();
        });
    },
    handlereProlong(row) {
      request
        .post("/circulation/renew", { readerId: this.user.id, isbn: row.isbn })
        .then((res) => {
          res.code == 0
            ? ElMessage.success("续借成功")
            : ElMessage.error(res.msg);
          this.load();
        });
    },
    save() {
      if (!this.form.deadtime) return ElMessage.warning("请选择应还日期");
      request
        .put("/bookwithuser/due-date", {
          operatorId: this.user.id,
          borrowId: this.form.borrowId,
          dueDate: this.form.deadtime,
        })
        .then((res) => {
          if (res.code == 0) {
            ElMessage.success("应还日期已更新");
            this.dialogVisible2 = false;
            this.load();
          } else ElMessage.error(res.msg);
        });
    },
    handleEdit(row) {
      this.form = JSON.parse(JSON.stringify(row));
      this.dialogVisible2 = true;
    },
    statusTagType(status) {
      return status === "OVERDUE"
        ? "danger"
        : status === "DUE_SOON"
          ? "warning"
          : "success";
    },
    handleSizeChange(size) {
      this.pageSize = size;
      this.currentPage = 1;
      this.load();
    },
    handleCurrentChange(page) {
      this.currentPage = page;
      this.load();
    },
  },
};
</script>
<style scoped>
.overdue-text {
  color: var(--danger);
  font-weight: 750;
}
</style>
