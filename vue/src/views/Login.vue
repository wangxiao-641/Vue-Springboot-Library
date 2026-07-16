<template>
  <div class="login-screen">
    <section class="login-story">
      <div class="story-brand">
        <span class="story-mark">L</span> Library Atlas
      </div>
      <div class="story-copy">
        <div class="eyebrow light">Knowledge in motion</div>
        <h1>让每一次借阅<br />都有清晰的轨迹</h1>
        <p>统一管理馆藏、读者与流通状态，让图书馆日常运营更从容。</p>
      </div>
      <div class="story-stats">
        <span><b>实时</b> 馆藏状态</span><span><b>清晰</b> 逾期提醒</span
        ><span><b>可靠</b> 流通记录</span>
      </div>
    </section>
    <section class="login-panel">
      <el-form
        ref="form"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="login"
      >
        <div class="mobile-brand">Library Atlas</div>
        <div class="login-kicker">欢迎回来</div>
        <h2>登录馆藏工作台</h2>
        <p class="login-hint">请输入账号信息继续访问系统</p>
        <el-form-item prop="username"
          ><el-input
            v-model="form.username"
            size="large"
            clearable
            placeholder="用户名"
            ><template #prefix
              ><el-icon><User /></el-icon></template></el-input
        ></el-form-item>
        <el-form-item prop="password"
          ><el-input
            v-model="form.password"
            size="large"
            clearable
            show-password
            type="password"
            placeholder="密码"
            ><template #prefix
              ><el-icon><Lock /></el-icon></template></el-input
        ></el-form-item>
        <el-form-item
          ><div class="code-row">
            <el-input
              v-model="form.validCode"
              size="large"
              placeholder="验证码"
            /><ValidCode class="valid-code" @input="createValidCode" /></div
        ></el-form-item>
        <el-form-item
          ><el-button
            type="primary"
            size="large"
            class="login-button"
            @click="login"
            >进入系统 <el-icon><Right /></el-icon></el-button
        ></el-form-item>
        <div class="register-link">
          还没有账号？<button type="button" @click="$router.push('/register')">
            前往注册
          </button>
        </div>
      </el-form>
    </section>
  </div>
</template>
<script>
import request from "../utils/request";
import { ElMessage } from "element-plus";
import ValidCode from "../components/Validate";
export default {
  name: "Login",
  components: { ValidCode },
  data() {
    return {
      validCode: "",
      form: {},
      rules: {
        username: [
          { required: true, message: "请输入用户名", trigger: "blur" },
        ],
        password: [{ required: true, message: "请输入密码", trigger: "blur" }],
      },
    };
  },
  methods: {
    createValidCode(data) {
      this.validCode = data;
    },
    login() {
      this.$refs.form.validate((valid) => {
        if (!valid) return;
        if (!this.form.validCode) return ElMessage.error("请填写验证码");
        if (this.form.validCode.toLowerCase() !== this.validCode.toLowerCase())
          return ElMessage.error("验证码错误");
        request.post("user/login", this.form).then((res) => {
          if (res.code == 0) {
            ElMessage.success("登录成功");
            sessionStorage.setItem("user", JSON.stringify(res.data));
            this.$router.push("/dashboard");
          } else ElMessage.error(res.msg);
        });
      });
    },
  },
};
</script>
<style scoped>
.login-screen {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(520px, 1.15fr) minmax(420px, 0.85fr);
  background: #fff;
}
.login-story {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100vh;
  padding: 46px 58px 42px;
  color: #fff;
  overflow: hidden;
  background: var(--ink-950);
}
.login-story::before,
.login-story::after {
  content: "";
  position: absolute;
  border-radius: 50%;
}
.login-story::before {
  width: 460px;
  height: 460px;
  right: -180px;
  top: 13%;
  border: 1px solid rgba(141, 226, 213, 0.22);
  box-shadow:
    0 0 0 80px rgba(141, 226, 213, 0.025),
    0 0 0 160px rgba(141, 226, 213, 0.02);
}
.login-story::after {
  width: 220px;
  height: 220px;
  left: 18%;
  bottom: -150px;
  background: #0f766e;
  filter: blur(2px);
}
.story-brand {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 11px;
  font-weight: 750;
  letter-spacing: 0.02em;
}
.story-mark {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  color: var(--ink-950);
  background: #8de2d5;
  font-size: 19px;
}
.story-copy {
  position: relative;
  z-index: 1;
  max-width: 620px;
}
.eyebrow.light {
  color: #8de2d5;
}
.story-copy h1 {
  margin-top: 14px;
  font-size: clamp(44px, 5vw, 68px);
  line-height: 1.08;
  letter-spacing: -0.045em;
}
.story-copy p {
  max-width: 500px;
  margin-top: 24px;
  color: #bcccdc;
  font-size: 17px;
  line-height: 1.8;
}
.story-stats {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 30px;
  color: #9fb3c8;
  font-size: 12px;
}
.story-stats b {
  display: block;
  color: #fff;
  font-size: 14px;
}
.login-panel {
  display: grid;
  place-items: center;
  padding: 48px;
}
.login-form {
  width: min(390px, 100%);
}
.mobile-brand {
  display: none;
}
.login-kicker {
  color: var(--accent);
  font-size: 13px;
  font-weight: 750;
}
.login-form h2 {
  margin-top: 6px;
  color: var(--ink-950);
  font-size: 30px;
  letter-spacing: -0.025em;
}
.login-hint {
  margin: 8px 0 30px;
  color: var(--ink-600);
}
.login-form .el-form-item {
  margin-bottom: 20px;
}
.code-row {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 136px;
  gap: 10px;
}
.valid-code {
  width: 136px !important;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
}
.login-button {
  width: 100%;
  height: 44px;
}
.login-button .el-icon {
  margin-left: 8px;
}
.register-link {
  text-align: center;
  color: var(--ink-400);
  font-size: 13px;
}
.register-link button {
  border: 0;
  color: var(--accent);
  background: none;
  cursor: pointer;
  font-weight: 700;
}
@media (max-width: 900px) {
  .login-screen {
    grid-template-columns: 1fr;
    background: var(--paper);
  }
  .login-story {
    display: none;
  }
  .login-panel {
    min-height: 100vh;
    padding: 30px;
  }
  .login-form {
    padding: 34px;
    border: 1px solid var(--line);
    border-radius: 18px;
    background: #fff;
    box-shadow: var(--shadow-md);
  }
  .mobile-brand {
    display: block;
    margin-bottom: 34px;
    color: var(--ink-950);
    font-weight: 800;
  }
}
</style>
