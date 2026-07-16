<template>
  <div class="register-screen" :data-register-theme="theme">
    <div class="register-theme-switch"><ThemeSelector /></div>
    <section class="register-intro">
      <div class="register-brand">{{ theme === 'command' ? 'LIBRARY / CORE' : theme === 'academy' ? '阅见书院' : 'Library Atlas' }}</div>
      <div>
        <span class="eyebrow">Create your library identity</span>
        <h1>加入馆藏系统<br />开启阅读轨迹</h1>
        <p>创建账号后即可检索馆藏、查看借阅状态并管理个人资料。</p>
      </div>
      <div class="register-points"><span>馆藏检索</span><span>借阅追踪</span><span>到期提醒</span></div>
    </section>
    <section class="register-panel">
    <el-form ref="form" :model="form" :rules="rules" class="register-form themed-form">
      <div class="register-kicker">新用户登记</div>
      <h2>创建账号</h2>
      <p class="register-hint">填写基本信息，选择你的账号角色。</p>
      <el-form-item prop="username">
        <el-input v-model="form.username" size="large" placeholder="请输入用户名" clearable>
          <template #prefix>
            <el-icon class="el-input__icon"><User/></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="form.password" size="large" type="password" placeholder="请输入密码" clearable show-password>
          <template #prefix>
            <el-icon class="el-input__icon"><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="confirm">
        <el-input v-model="form.confirm" size="large" type="password" placeholder="请再次确认密码" clearable show-password>
          <template #prefix>
            <el-icon class="el-input__icon"><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="role">
        <div class="role-choice"><el-radio v-model="form.role" :label="2">读者</el-radio>
        <el-radio v-model="form.role" :label="1">管理员</el-radio></div>
      </el-form-item>
      <el-form-item prop="authorize" v-if="form.role==1">
        <el-input v-model="form.authorize" size="large" type="password" placeholder="请输入管理员注册码" clearable show-password>
          <template #prefix>
            <el-icon class="el-input__icon"><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <div class="register-code-row">
          <el-input v-model="form.validCode" size="large" placeholder="请输入验证码"></el-input>
          <ValidCode class="register-code" @input="createValidCode"/>
        </div>
      </el-form-item>
      <el-form-item >
        <el-button type="primary" size="large" class="register-submit" @click="register">创建账号</el-button>
      </el-form-item>
      <div class="register-login">已有账号？<button type="button" @click="$router.push('/login')">返回登录</button></div>
    </el-form>
    </section>
</div>

</template>

<script>
import request from "../utils/request";
import {ElMessage} from "element-plus";
import ValidCode from "../components/Validate";
import ThemeSelector from "../components/ThemeSelector";
import { mapState } from "vuex";
export default {
  name: "Register",
  components:{
    ValidCode, ThemeSelector
  },
  computed: { ...mapState(["theme"]) },
  data(){
    return{
      form:{role: 2},
      validCode: '',
      rules: {
        username: [
          {
            required: true,
            message: '请输入用户名',
            trigger: 'blur',
          },
          {
            min: 2,
            max: 13,
            message: '长度要求为2到13位',
            trigger: 'blur',
          },
        ],
        password: [
          {
            required: true,
            message: '请输入密码',
            trigger: 'blur',
          }
        ],
      confirm:[
        {
          required:true,
          message:"请确认密码",
          trigger:"blur"
        }
      ],
        authorize:[
          {
            required:true,
            message:"请输入注册码",
            trigger:"blur"
          }
        ],
      }
    }
    },

  methods:{
    createValidCode(data){
      this.validCode =data
    },
    register(){
      this.$refs['form'].validate((valid) => {
        if (valid) {
          if (!this.form.validCode) {
            ElMessage.error("请填写验证码")
            return
          }
          if(this.form.validCode.toLowerCase() !== this.validCode.toLowerCase()) {
            ElMessage.error("验证码错误")
            return
          }
          if(this.form.password != this.form.confirm)
          {
            ElMessage.error("两次密码输入不一致")
            return
          }
          if(this.form.role == 1 && this.form.authorize != "1234")
          {
            ElMessage.error("请输入正确的注册码")
            return
          }
          request.post("user/register",this.form).then(res=>{
            if(res.code == 0)
            {
              ElMessage.success("注册成功")
              this.$router.push("/login")
            }
            else {ElMessage.error(res.msg)}
          })
        }
      })

    }
  }

  }

</script>

<style scoped>
.register-screen { min-height: 100vh; display: grid; grid-template-columns: minmax(380px,.85fr) minmax(480px,1.15fr); background: var(--theme-bg); }
.register-theme-switch { position: fixed; z-index: 5; top: 22px; right: 28px; }
.register-intro { display: flex; flex-direction: column; justify-content: space-between; padding: 42px 48px; color: #fff; background: #102a43; }
.register-brand { font-weight: 800; letter-spacing: .04em; }
.register-intro h1 { margin: 14px 0 18px; font-size: clamp(38px,4vw,58px); line-height: 1.08; }
.register-intro p { max-width: 480px; color: #bcccdc; line-height: 1.8; }
.register-points { display: flex; gap: 12px; flex-wrap: wrap; }
.register-points span { padding: 7px 10px; border: 1px solid rgba(255,255,255,.18); border-radius: 999px; font-size: 12px; }
.register-panel { display: grid; place-items: center; padding: 70px 36px 38px; }
.register-form { width: min(440px,100%); padding: 30px; border: 1px solid var(--theme-line); border-radius: 18px; background: var(--theme-surface); box-shadow: var(--theme-shadow); }
.register-kicker { color: var(--theme-accent); font-weight: 750; }
.register-form h2 { margin: 5px 0; color: var(--theme-text); font-size: 30px; }
.register-hint { margin-bottom: 24px; color: var(--theme-muted); }
.role-choice { width: 100%; padding: 8px 12px; border: 1px solid var(--theme-line); border-radius: 9px; }
.register-code-row { width: 100%; display: grid; grid-template-columns: 1fr 138px; gap: 10px; }
.register-code { width: 138px !important; height: 40px; overflow: hidden; border-radius: 8px; }
.register-submit { width: 100%; }
.register-login { color: var(--theme-muted); text-align: center; font-size: 13px; }
.register-login button { border: 0; color: var(--theme-accent); background: transparent; cursor: pointer; font-weight: 750; }
.register-screen[data-register-theme="academy"] { display: block; padding: 0 24px 50px; }
.register-screen[data-register-theme="academy"] .register-intro { min-height: 300px; border-radius: 0 0 42px 42px; background: #4e3328; }
.register-screen[data-register-theme="academy"] .register-intro h1 { font-family: Georgia,"Songti SC",serif; }
.register-screen[data-register-theme="academy"] .register-panel {
  width: min(720px,calc(100% - 30px)); margin: -80px auto 0; padding: 36px;
  border-radius: 26px; background: #fffdf8; box-shadow: var(--theme-shadow);
}
.register-screen[data-register-theme="academy"] .register-form { box-shadow: none; border: 0; }
.register-screen[data-register-theme="command"] .register-intro {
  background-color: #080d1d;
  background-image: linear-gradient(rgba(139,124,255,.12) 1px,transparent 1px),
    linear-gradient(90deg,rgba(139,124,255,.12) 1px,transparent 1px);
  background-size: 26px 26px;
}
.register-screen[data-register-theme="command"] .register-form { border-radius: 6px; background: #111a31; }
@media (max-width: 900px) {
  .register-screen, .register-screen[data-register-theme="academy"] { display: block; padding: 0; }
  .register-intro { display: none; }
  .register-panel, .register-screen[data-register-theme="academy"] .register-panel {
    width: 100%; min-height: 100vh; margin: 0; padding: 72px 20px 30px; border-radius: 0;
  }
  .register-theme-switch { top: 14px; right: 14px; }
}
</style>
