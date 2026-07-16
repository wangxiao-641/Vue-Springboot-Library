<template>
  <div class="page-shell data-page book-page">
    <PageHeader
      :title="user.role == 1 ? '馆藏管理' : '馆藏检索'"
      :description="
        user.role == 1
          ? '维护图书资料与库存，关注每一本书的流通状态。'
          : '检索可借馆藏，并完成借阅与归还操作。'
      "
    >
      <template #actions
        ><el-button v-if="user.role == 1" type="primary" @click="add"
          ><el-icon><Plus /></el-icon>上架图书</el-button
        ><el-button v-if="numOfOutDataBook" type="warning" plain @click="toLook"
          ><el-icon><Warning /></el-icon
          >{{ numOfOutDataBook }} 本逾期</el-button
        ></template
      >
    </PageHeader>
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
        ><el-form-item label="作者"
          ><el-input
            v-model="search3"
            placeholder="输入作者"
            clearable /></el-form-item
        ><el-form-item
          ><el-button type="primary" @click="load"
            ><el-icon><Search /></el-icon>查询</el-button
          ><el-button @click="clear">重置</el-button></el-form-item
        ></el-form
      >
    </div>
    <div v-if="user.role == 1" class="action-row">
      <el-popconfirm title="确认删除选中的图书？" @confirm="deleteBatch"
        ><template #reference
          ><el-button type="danger" plain
            ><el-icon><Delete /></el-icon>批量删除</el-button
          ></template
        ></el-popconfirm
      ><span class="muted">库存由系统随借还操作自动维护</span>
    </div>
    <div class="surface-card table-card">
      <div class="table-scroll">
        <el-table
          :data="tableData"
          @selection-change="handleSelectionChange"
          empty-text="暂无匹配图书"
        >
          <el-table-column
            v-if="user.role == 1"
            type="selection"
            width="48"
          /><el-table-column
            prop="isbn"
            label="图书编号"
            min-width="140"
            sortable
          /><el-table-column
            prop="name"
            label="图书名称"
            min-width="170"
          /><el-table-column
            prop="author"
            label="作者"
            min-width="110"
          /><el-table-column
            prop="publisher"
            label="出版社"
            min-width="140"
          /><el-table-column prop="price" label="价格" width="90" sortable
            ><template #default="scope"
              >¥ {{ scope.row.price }}</template
            ></el-table-column
          ><el-table-column
            prop="totalCount"
            label="馆藏"
            width="82"
            sortable
          /><el-table-column
            prop="availableCount"
            label="可借"
            width="82"
            sortable
          /><el-table-column
            prop="createTime"
            label="出版时间"
            min-width="120"
            sortable
          /><el-table-column label="状态" width="100"
            ><template #default="scope"
              ><el-tag
                :type="isBookUnavailable(scope.row) ? 'info' : 'success'"
                effect="light"
                >{{
                  isBookUnavailable(scope.row) ? "暂无库存" : "可借阅"
                }}</el-tag
              ></template
            ></el-table-column
          ><el-table-column
            fixed="right"
            label="操作"
            :width="user.role == 1 ? 150 : 150"
            ><template #default="scope"
              ><template v-if="user.role == 1"
                ><el-button link type="primary" @click="handleEdit(scope.row)"
                  >编辑</el-button
                ><el-popconfirm
                  title="确认删除这本图书？"
                  @confirm="handleDelete(scope.row.id)"
                  ><template #reference
                    ><el-button link type="danger">删除</el-button></template
                  ></el-popconfirm
                ></template
              ><template v-else
                ><el-button
                  link
                  type="primary"
                  :disabled="isBookUnavailable(scope.row)"
                  @click="handlelend(scope.row.isbn)"
                  >借阅</el-button
                ><el-popconfirm
                  title="确认归还这本图书？"
                  @confirm="handlereturn(scope.row.isbn)"
                  ><template #reference
                    ><el-button
                      link
                      type="danger"
                      :disabled="isbnArray.indexOf(scope.row.isbn) == -1"
                      >还书</el-button
                    ></template
                  ></el-popconfirm
                ></template
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
      v-model="dialogVisible3"
      title="逾期借阅提醒"
      width="min(760px, 90vw)"
      ><el-alert
        title="逾期期间不能借阅新书，请优先完成归还。"
        type="warning"
        :closable="false"
        show-icon
        class="status-note"
      />
      <div class="table-scroll">
        <el-table :data="outDateBook"
          ><el-table-column
            prop="isbn"
            label="图书编号"
            min-width="130" /><el-table-column
            prop="bookName"
            label="书名"
            min-width="150" /><el-table-column
            prop="deadtime"
            label="应还日期"
            min-width="170" /><el-table-column
            prop="overdueDays"
            label="逾期天数"
            width="100"
        /></el-table>
      </div>
      <template #footer
        ><el-button type="primary" @click="dialogVisible3 = false"
          >我知道了</el-button
        ></template
      ></el-dialog
    >
    <el-dialog v-model="dialogVisible" title="上架图书" width="min(560px, 90vw)"
      ><BookForm :form="form" /><template #footer
        ><el-button @click="dialogVisible = false">取消</el-button
        ><el-button type="primary" @click="save">确认上架</el-button></template
      ></el-dialog
    >
    <el-dialog
      v-model="dialogVisible2"
      title="编辑图书信息"
      width="min(560px, 90vw)"
      ><BookForm :form="form" :editing="true" /><template #footer
        ><el-button @click="dialogVisible2 = false">取消</el-button
        ><el-button type="primary" @click="save">保存修改</el-button></template
      ></el-dialog
    >
  </div>
</template>
<script>
import request from "../utils/request";
import { ElMessage } from "element-plus";
import PageHeader from "../components/PageHeader";
import BookForm from "../components/BookForm";
export default {
  name: "Book",
  components: { PageHeader, BookForm },
  created() {
    this.user = JSON.parse(sessionStorage.getItem("user") || "{}");
    this.load();
  },
  data() {
    return {
      form: {},
      dialogVisible: false,
      dialogVisible2: false,
      dialogVisible3: false,
      search1: "",
      search2: "",
      search3: "",
      total: 10,
      currentPage: 1,
      pageSize: 10,
      tableData: [],
      user: {},
      bookData: [],
      isbnArray: [],
      outDateBook: [],
      numOfOutDataBook: 0,
      ids: [],
    };
  },
  methods: {
    handleSelectionChange(val) {
      this.ids = val.map((v) => v.id);
    },
    deleteBatch() {
      if (!this.ids.length) return ElMessage.warning("请选择数据！");
      request.post("/book/deleteBatch", this.ids).then((res) => {
        if (res.code === "0") {
          ElMessage.success("批量删除成功");
          this.load();
        } else ElMessage.error(res.msg);
      });
    },
    load() {
      this.numOfOutDataBook = 0;
      this.outDateBook = [];
      this.isbnArray = [];
      request
        .get("/book", {
          params: {
            pageNum: this.currentPage,
            pageSize: this.pageSize,
            search1: this.search1,
            search2: this.search2,
            search3: this.search3,
          },
        })
        .then((res) => {
          this.tableData = res.data.records;
          this.total = res.data.total;
        });
      if (this.user.role == 2)
        request
          .get("/bookwithuser", {
            params: {
              pageNum: 1,
              pageSize: 100,
              search1: "",
              search2: "",
              search3: this.user.id,
            },
          })
          .then((res) => {
            this.bookData = res.data.records;
            this.isbnArray = this.bookData.map((i) => i.isbn);
            this.outDateBook = this.bookData
              .filter((i) => i.dueStatus === "OVERDUE")
              .map((i) => ({
                isbn: i.isbn,
                bookName: i.bookName,
                deadtime: i.deadtime,
                lendtime: i.lendtime,
                overdueDays: i.overdueDays,
              }));
            this.numOfOutDataBook = this.outDateBook.length;
          });
    },
    clear() {
      this.search1 = "";
      this.search2 = "";
      this.search3 = "";
      this.currentPage = 1;
      this.load();
    },
    handleDelete(id) {
      request.delete("book/" + id).then((res) => {
        res.code == 0
          ? ElMessage.success("删除成功")
          : ElMessage.error(res.msg);
        this.load();
      });
    },
    handlereturn(isbn) {
      request
        .post("/circulation/return", { readerId: this.user.id, isbn })
        .then((res) => {
          res.code == 0
            ? ElMessage.success("还书成功")
            : ElMessage.error(res.msg);
          this.load();
        });
    },
    handlelend(isbn) {
      request
        .post("/circulation/borrow", { readerId: this.user.id, isbn })
        .then((res) => {
          res.code == 0
            ? ElMessage.success("借阅成功")
            : ElMessage.error(res.msg);
          this.load();
        });
    },
    isBookUnavailable(row) {
      return row.availableCount !== null && row.availableCount !== undefined
        ? row.availableCount == 0
        : row.status == 0;
    },
    add() {
      this.form = {};
      this.dialogVisible = true;
    },
    save() {
      if (!Number.isInteger(this.form.totalCount) || this.form.totalCount <= 0)
        return ElMessage.error("馆藏总数必须为正整数");
      const payload = JSON.parse(JSON.stringify(this.form));
      delete payload.availableCount;
      const req = this.form.id
        ? request.put("/book", payload)
        : request.post("/book", payload);
      req.then((res) => {
        if (res.code == 0) {
          ElMessage.success(this.form.id ? "修改书籍信息成功" : "上架书籍成功");
          this.load();
          this.dialogVisible = false;
          this.dialogVisible2 = false;
        } else ElMessage.error(res.msg);
      });
    },
    handleEdit(row) {
      this.form = JSON.parse(JSON.stringify(row));
      this.dialogVisible2 = true;
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
    toLook() {
      this.dialogVisible3 = true;
    },
  },
};
</script>
