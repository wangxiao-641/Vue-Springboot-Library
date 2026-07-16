<template>
  <header class="topbar">
    <div class="brand-lockup">
      <div class="brand-mark">L</div>
      <div>
        <div class="brand-name">Library Atlas</div>
        <div class="brand-subtitle">馆藏运营工作台</div>
      </div>
    </div>
    <div class="topbar-meta">
      <span class="system-status"><span class="status-dot" />系统在线</span>
      <el-dropdown>
        <button class="profile-trigger" type="button">
          <span class="avatar">{{
            (user.nickName || user.username || "U").slice(0, 1)
          }}</span
          ><span>{{ user.nickName || user.username || "用户" }}</span
          ><el-icon><arrow-down /></el-icon>
        </button>
        <template #dropdown
          ><el-dropdown-menu
            ><el-dropdown-item @click="exit"
              >退出系统</el-dropdown-item
            ></el-dropdown-menu
          ></template
        >
      </el-dropdown>
    </div>
  </header>
</template>
<script>
import { ElMessage } from "element-plus";
export default {
  name: "Header",
  data: () => ({ user: {} }),
  created() {
    this.user = JSON.parse(sessionStorage.getItem("user") || "{}");
  },
  methods: {
    exit() {
      sessionStorage.removeItem("user");
      this.$router.push("/login");
      ElMessage.success("已安全退出");
    },
  },
};
</script>
<style scoped>
.topbar {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  color: #fff;
  background: var(--ink-950);
}
.brand-lockup,
.topbar-meta,
.profile-trigger,
.system-status {
  display: flex;
  align-items: center;
}
.brand-lockup {
  gap: 12px;
}
.brand-mark {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  color: var(--ink-950);
  background: #8de2d5;
  font-weight: 800;
  font-size: 20px;
}
.brand-name {
  font-weight: 750;
  letter-spacing: 0.02em;
}
.brand-subtitle {
  color: #9fb3c8;
  font-size: 11px;
  margin-top: 1px;
}
.topbar-meta {
  gap: 24px;
}
.system-status {
  gap: 7px;
  color: #b8c7d8;
  font-size: 12px;
}
.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #65d6a6;
  box-shadow: 0 0 0 4px rgba(101, 214, 166, 0.13);
}
.profile-trigger {
  border: 0;
  gap: 9px;
  color: #fff;
  background: transparent;
  cursor: pointer;
  font-weight: 650;
}
.profile-trigger .el-icon {
  color: #9fb3c8;
}
.avatar {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: var(--ink-950);
  background: #d9f5ef;
  font-size: 13px;
  font-weight: 800;
}
@media (max-width: 800px) {
  .topbar {
    padding: 0 16px;
  }
  .system-status,
  .brand-subtitle {
    display: none;
  }
  .topbar-meta {
    gap: 8px;
  }
}
</style>
