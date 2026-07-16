<template>
  <aside class="sidebar" :data-nav="theme" aria-label="主导航">
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
    <div class="sidebar-foot">{{ theme === 'command' ? 'SYS / 2026' : theme === 'academy' ? '阅见 · 2026' : 'Atlas / 2026' }}</div>
  </aside>
</template>
<script>
import { mapState } from 'vuex';
export default {
  name: "Aside",
  data: () => ({ user: {} }),
  computed: { ...mapState(['theme']), path() { return this.$route.path } },
  created() {
    this.user = JSON.parse(sessionStorage.getItem("user") || "{}");
  },
};
</script>
<style scoped>
.sidebar {
  flex: 0 0 var(--nav-width);
  min-height: calc(100vh - var(--header-height));
  padding: 24px 14px;
  background: var(--nav-bg);
  border-right: 1px solid var(--theme-line);
}
.nav-label {
  padding: 0 14px 10px;
  color: var(--theme-muted);
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
  color: var(--theme-text);
}
.atlas-menu :deep(.el-menu-item .el-icon) {
  margin-right: 11px;
  color: var(--theme-muted);
}
.atlas-menu :deep(.el-menu-item.is-active) {
  color: var(--theme-accent);
  background: var(--theme-accent-soft);
  font-weight: 750;
}
.atlas-menu :deep(.el-menu-item.is-active .el-icon) {
  color: var(--theme-accent);
}
.sidebar-foot {
  margin: 34px 14px 0;
  color: var(--theme-muted);
  font-size: 11px;
}

.sidebar[data-nav='academy'] {
  min-height: auto; width: 100%; padding: 0 max(24px, calc((100vw - 1180px) / 2));
  border-right: 0; border-bottom: 1px solid var(--theme-line);
  display: flex; align-items: center; justify-content: space-between;
}
.sidebar[data-nav='academy'] .nav-label, .sidebar[data-nav='academy'] .sidebar-foot { display: none; }
.sidebar[data-nav='academy'] .atlas-menu { display: flex; }
.sidebar[data-nav='academy'] .atlas-menu :deep(.el-menu-item) { margin: 0 2px; border-radius: 0; height: 54px; line-height: 54px; }
.sidebar[data-nav='command'] { padding: 18px 8px; }
.sidebar[data-nav='command'] .nav-label, .sidebar[data-nav='command'] .sidebar-foot, .sidebar[data-nav='command'] .atlas-menu :deep(.el-menu-item span) { display: none; }
.sidebar[data-nav='command'] .atlas-menu :deep(.el-menu-item) { justify-content: center; padding: 0; border: 1px solid transparent; }
.sidebar[data-nav='command'] .atlas-menu :deep(.el-menu-item .el-icon) { margin: 0; font-size: 19px; }
.sidebar[data-nav='command'] .atlas-menu :deep(.el-menu-item.is-active) { border-color: var(--theme-accent); box-shadow: 0 0 18px rgba(139,124,255,.2); }
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
  .sidebar[data-nav='academy'] { padding: 0 8px; overflow-x: auto; justify-content: flex-start; }
  .sidebar[data-nav='academy'] .atlas-menu :deep(.el-menu-item span) { display: none; }
  .sidebar[data-nav='academy'] .atlas-menu :deep(.el-menu-item) { min-width: 48px; justify-content: center; padding: 0 12px; }
  .sidebar[data-nav='academy'] .atlas-menu :deep(.el-menu-item .el-icon) { margin: 0; }
}
</style>
