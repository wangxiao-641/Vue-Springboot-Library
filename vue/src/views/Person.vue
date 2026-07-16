<template>
  <div class="page-shell profile-page person-page">
    <PageHeader title="个人信息" description="维护账号展示信息与联系方式。" />
    <section class="surface-card profile-card">
      <div class="profile-aside">
        <span class="profile-monogram">{{ (form.nickName || form.username || 'U').slice(0, 1) }}</span>
        <strong>{{ form.nickName || form.username || '用户' }}</strong>
        <span>{{ form.role == 1 ? '管理员账号' : '读者账号' }}</span>
      </div>
      <el-form :model="form" ref="form" label-width="88px" class="profile-form themed-form">
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled></el-input>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.nickName"></el-input>
        </el-form-item>
        <el-form-item label="权限">
            <el-tag v-if="form.role==1">管理员</el-tag>
            <el-tag v-if="form.role==2" type="info">读者</el-tag>
        </el-form-item>
        <el-form-item label="电话号码">
          <el-input v-model="form.phone"></el-input>
        </el-form-item>
        <el-form-item label="性别">
          <div>
            <el-radio v-model="form.sex" label="男">男</el-radio>
            <el-radio v-model="form.sex" label="女">女</el-radio>
          </div>
        </el-form-item>
        <el-form-item label="地址">
          <el-input type="textarea" :rows="3" v-model="form.address"></el-input>
        </el-form-item>
        <el-form-item class="form-actions">
          <el-button type="primary" @click="update">保存个人信息</el-button>
        </el-form-item>
      </el-form>
    </section>
  </div>
</template>

<script>
import request from "@/utils/request";
import {ElMessage} from "element-plus";
import PageHeader from "../components/PageHeader";

export default {
  name: "Person",
  components: { PageHeader },
  data() {
    return {
      form: {}
    }
  },
  created() {
    let str = sessionStorage.getItem("user") || "{}"
    this.form = JSON.parse(str)
  },
  methods: {
    update() {
      request.put("/user", this.form).then(res => {
        console.log(res)
        if (res.code === '0') {
          ElMessage.success("更新成功")
          sessionStorage.setItem("user", JSON.stringify(this.form))
          // 触发Layout更新用户信息
          this.$emit("userInfo")
        } else {
          ElMessage.error(res.msg)
        }
      })

    }
  }
}
</script>

<style scoped></style>
