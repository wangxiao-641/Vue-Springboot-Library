<template>
  <div style="padding:20px">
    <h2>展示板</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in cards" :key="item.title">
        <el-card class="box-card">
          <div class="clearfix">{{ item.title }}</div>
          <div class="text">{{ item.data }}</div>
        </el-card>
      </el-col>
    </el-row>
    <div style="margin-top:20px;color:#999">{{ timer }}</div>
  </div>
</template>

<script>
import request from "../utils/request";

export default {
  data() {
    return {
      timer: '',
      cards: [
        { title: '已借阅', data: 0 },
        { title: '总访问', data: 0 },
        { title: '图书数', data: 0 },
        { title: '用户数', data: 0 }
      ]
    }
  },
  mounted() {
    this.getTimer()
    setInterval(() => { this.getTimer() }, 1000)

    request.get("/dashboard").then(res => {
      if (res.code == 0) {
        this.cards[0].data = res.data.lendRecordCount
        this.cards[1].data = res.data.visitCount
        this.cards[2].data = res.data.bookCount
        this.cards[3].data = res.data.userCount
      }
    })
  },
  methods: {
    getTimer() {
      this.timer = new Date().toLocaleString()
    }
  }
}
</script>

<style scoped>
.box-card { width: 80%; margin-bottom: 25px; margin-left: 10px; }
.clearfix { text-align: center; font-size: 15px; }
.text { text-align: center; font-size: 24px; font-weight: 700; }
</style>
