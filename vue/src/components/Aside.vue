<template>
  <aside class="sidebar">
    <div class="nav-label">工作区</div>
    <el-menu :default-active="path" router class="atlas-menu">
      <el-menu-item index="/dashboard"
        ><el-icon><DataAnalysis /></el-icon><span>展示板</span></el-menu-item
      >
      <el-menu-item v-if="user.role == 1" index="/book"
        ><el-icon><Collection /></el-icon><span>书籍管理</span></el-menu-item
      >
      <el-menu-item v-else index="/book"
        ><el-icon><Collection /></el-icon><span>图书查询</span></el-menu-item
      >
      <el-menu-item v-if="user.role == 1" index="/user"
        ><el-icon><UserFilled /></el-icon><span>读者管理</span></el-menu-item
      >
      <el-menu-item index="/bookwithuser"
        ><el-icon><Reading /></el-icon><span>借阅状态</span></el-menu-item
      >
      <el-menu-item index="/lendrecord"
        ><el-icon><Tickets /></el-icon
        ><span>{{
          user.role == 1 ? "借阅管理" : "借阅信息"
        }}</span></el-menu-item
      >
    </el-menu>
    <div class="nav-label secondary">账户</div>
    <el-menu :default-active="path" router class="atlas-menu">
      <el-menu-item index="/person"
        ><el-icon><User /></el-icon><span>个人信息</span></el-menu-item
      >
      <el-menu-item index="/password"
        ><el-icon><Lock /></el-icon><span>修改密码</span></el-menu-item
      >
    </el-menu>
    <div class="sidebar-foot">Atlas / 2026</div>
  </aside>
</template>
<script>
export default {
  name: "Aside",
  data: () => ({ user: {}, path: "" }),
  created() {
    this.user = JSON.parse(sessionStorage.getItem("user") || "{}");
    this.path = this.$route.path;
  },
};
</script>
<style scoped>
.sidebar {
  flex: 0 0 224px;
  min-height: calc(100vh - 72px);
  padding: 24px 14px;
  background: #fff;
  border-right: 1px solid var(--line);
}
.nav-label {
  padding: 0 14px 10px;
  color: var(--ink-400);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}
.nav-label.secondary {
  margin-top: 26px;
}
.atlas-menu {
  border-right: 0;
  background: transparent;
}
.atlas-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 3px 0;
  border-radius: 9px;
  color: var(--ink-600);
}
.atlas-menu :deep(.el-menu-item .el-icon) {
  margin-right: 11px;
  color: var(--ink-400);
}
.atlas-menu :deep(.el-menu-item.is-active) {
  color: var(--accent);
  background: var(--accent-soft);
  font-weight: 750;
}
.atlas-menu :deep(.el-menu-item.is-active .el-icon) {
  color: var(--accent);
}
.sidebar-foot {
  margin: 34px 14px 0;
  color: var(--ink-400);
  font-size: 11px;
}
@media (max-width: 800px) {
  .sidebar {
    flex-basis: 68px;
    padding: 18px 8px;
  }
  .nav-label,
  .sidebar-foot,
  .atlas-menu :deep(.el-menu-item span) {
    display: none;
  }
  .atlas-menu :deep(.el-menu-item) {
    justify-content: center;
    padding: 0;
  }
  .atlas-menu :deep(.el-menu-item .el-icon) {
    margin: 0;
    font-size: 18px;
  }
}
</style>
