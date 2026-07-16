<template>
  <div class="home" style ="padding: 10px">
    <!-- 搜索-->
    <div style="margin: 10px 0;">

      <el-form inline="true" size="small" >
        <el-form-item label="图书编号" >
          <el-input v-model="search1" placeholder="请输入图书编号"  clearable>
            <template #prefix><el-icon class="el-input__icon"><search/></el-icon></template>
          </el-input>
        </el-form-item >
        <el-form-item label="图书名称" >
          <el-input v-model="search2" placeholder="请输入图书名称"  clearable>
            <template #prefix><el-icon class="el-input__icon"><search /></el-icon></template>
          </el-input>
        </el-form-item >
        <el-form-item label="借阅者" v-if="user.role == 1">
          <el-input v-model="search3" placeholder="请输入借阅者昵称"  clearable>
            <template #prefix><el-icon class="el-input__icon"><search /></el-icon></template>
          </el-input>
        </el-form-item >
        <el-form-item v-if="user.role == 1">
          <el-checkbox v-model="overdueOnly">仅看逾期未还</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="margin-left: 1%" @click="load" size="mini">查询</el-button>
        </el-form-item>
        <el-form-item>
          <el-button size="mini"  type="danger" @click="clear">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    <el-alert
        v-if="hasOverdue"
        title="存在逾期未还图书，逾期期间不能借新书或续借该逾期图书，请尽快归还。"
        type="error"
        :closable="false"
        show-icon
        style="margin-bottom: 12px"
    />
    <!-- 按钮-->
    <div style="margin: 10px 0;" >
      <el-popconfirm title="确认删除?" @confirm="deleteBatch" v-if="user.role == 1">
        <template #reference>
          <el-button type="danger" size="mini" >批量删除</el-button>
        </template>
      </el-popconfirm>
    </div>
    <!-- 数据字段-->
    <el-table :data="tableData" stripe border="true" @selection-change="handleSelectionChange">
      <el-table-column v-if="user.role ==1"
          type="selection"
          width="55">
      </el-table-column>
      <el-table-column prop="isbn" label="图书编号" sortable />
      <el-table-column prop="bookName" label="图书名称" />
      <el-table-column prop="nickName" label="借阅者" />
      <el-table-column prop="lendtime" label="借阅时间" />
      <el-table-column prop="deadtime" label="最迟归还日期" />
      <el-table-column label="借阅状态" width="130">
        <template #default="scope">
          <el-tag :type="statusTagType(scope.row.dueStatus)">{{ scope.row.dueStatusText }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="逾期天数" width="150">
        <template #default="scope">
          <span v-if="scope.row.dueStatus === 'OVERDUE'" class="overdue-text">已逾期 {{ scope.row.overdueDays }} 天</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="prolong" label="可续借次数" />
      <el-table-column fixed="right" label="操作" >
        <template v-slot="scope">
          <el-button size="mini" @click="handleEdit(scope.row)" v-if="user.role == 1">调整应还日期</el-button>
          <el-popconfirm title="确认删除?" @confirm="handleDelete(scope.row) " v-if="user.role == 1">
            <template #reference>
              <el-button type="danger" size="mini" >删除</el-button>
            </template>
          </el-popconfirm>
          <el-popconfirm title="确认续借(续借一次延长30天)?" @confirm="handlereProlong(scope.row)" v-if="user.role == 2" :disabled="scope.row.prolong == 0 || scope.row.dueStatus === 'OVERDUE'">
            <template #reference>
              <el-button type="danger" size="mini" :disabled="scope.row.prolong == 0 || scope.row.dueStatus === 'OVERDUE'" >续借</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <!--    分页-->
    <div style="margin: 10px 0">
      <el-pagination
          v-model:currentPage="currentPage"
          :page-sizes="[5, 10, 20]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
      >
      </el-pagination>

      <el-dialog v-model="dialogVisible2" title="调整应还日期" width="420px">
        <el-form :model="form" label-width="120px">
          <el-form-item label="借阅信息">
            <span>{{ form.nickName }} / {{ form.bookName }}</span>
          </el-form-item>
          <el-form-item label="应还日期" required>
            <el-date-picker
                v-model="form.deadtime"
                type="datetime"
                value-format="YYYY-MM-DD HH:mm:ss"
                placeholder="选择应还日期"
                style="width: 100%"
            />
          </el-form-item>
        </el-form>
        <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible2 = false">取 消</el-button>
        <el-button type="primary" @click="save">确 定</el-button>
      </span>
        </template>
      </el-dialog>

    </div>
  </div>
</template>

<script>
// @ is an alias to /src
import request from "../utils/request";
import {ElMessage} from "element-plus";
export default {
  created(){
    let userStr = sessionStorage.getItem("user") ||"{}"
    this.user = JSON.parse(userStr)
    this.load()
  },
  name: 'bookwithuser',
  methods: {

    handleSelectionChange(val){
      this.forms = val
    },
    deleteBatch(){
      if (!this.forms.length) {
        ElMessage.warning("请选择数据！")
        return
      }
    //  一个小优化，直接发送这个数组，而不是一个一个的提交删除
      request.post("bookwithuser/deleteRecords",this.forms).then(res =>{
        if(res.code === '0'){
          ElMessage.success("批量删除成功")
          this.load()
        }
        else {
          ElMessage.error(res.msg)
        }
      })
    },
    load(){
      if(this.user.role == 1){
        request.get("/bookwithuser",{
          params:{
            pageNum: this.currentPage,
            pageSize: this.pageSize,
            search1: this.search1,
            search2: this.search2,
            search3: this.search3,
            overdueOnly: this.overdueOnly,
          }
        }).then(res =>{
          console.log(res)
          this.tableData = res.data.records
          this.total = res.data.total
        })
      }
      else {
        request.get("/bookwithuser",{
          params:{
            pageNum: this.currentPage,
            pageSize: this.pageSize,
            search1: this.search1,
            search2: this.search2,
            search3: this.user.id,
            overdueOnly: false,
          }
        }).then(res =>{
          console.log(res)
          this.tableData = res.data.records
          this.total = res.data.total
        })
      }
    },
    clear(){
      this.search1 = ""
      this.search2 = ""
      this.search3 = ""
      this.overdueOnly = false
      this.load()
    },
    handleDelete(row){
      const form3 = JSON.parse(JSON.stringify(row))
      request.post("bookwithuser/deleteRecord",form3).then(res =>{
        console.log(res)
        if(res.code == 0 ){
          ElMessage.success("删除成功")
        }
        else
          ElMessage.error(res.msg)
        this.load()
      })
    },
    handlereProlong(row){
      request.post("/circulation/renew",{
        readerId: this.user.id,
        isbn: row.isbn,
      }).then(res =>{
        console.log(res)
        if(res.code == 0){
          ElMessage({
            message: '续借成功',
            type: 'success',
          })
        }
        else {
          ElMessage.error(res.msg)
        }
        this.load()
        this.dialogVisible2 = false
      })
    },
    save(){
      //ES6语法
      //地址,但是？IP与端口？+请求参数
      // this.form?这是自动保存在form中的，虽然显示时没有使用，但是这个对象中是有它的
        if (!this.form.deadtime) {
          ElMessage.warning("请选择应还日期")
          return
        }
        request.put("/bookwithuser/due-date", {
          operatorId: this.user.id,
          borrowId: this.form.borrowId,
          dueDate: this.form.deadtime,
        }).then(res =>{
          console.log(res)
          if(res.code == 0){
            ElMessage({
              message: '修改信息成功',
              type: 'success',
            })
          }
          else {
            ElMessage.error(res.msg)
          }
          this.load()
          this.dialogVisible2 = false
        })
    },

    handleEdit(row){
      this.form = JSON.parse(JSON.stringify(row))
      this.dialogVisible2 = true
    },
    statusTagType(status){
      if (status === 'OVERDUE') return 'danger'
      if (status === 'DUE_SOON') return 'warning'
      return 'success'
    },
    handleSizeChange(pageSize){
      this.pageSize = pageSize
      this.load()
    },
    handleCurrentChange(pageNum){
      this.currentPage = pageNum
      this.load()
    },

  },
  data() {
    return {
      form: {},
      form2:{},
      form3:{},
      dialogVisible: false,
      dialogVisible2: false,
      search1:'',
      search2:'',
      search3:'',
      overdueOnly: false,
      total:10,
      currentPage:1,
      pageSize: 10,
      tableData: [],
      user:{},
      forms:[],
    }
  },
  computed: {
    hasOverdue(){
      return this.tableData.some(item => item.dueStatus === 'OVERDUE')
    }
  }
}
</script>

<style scoped>
.overdue-text {
  color: #f56c6c;
  font-weight: 600;
}
</style>
