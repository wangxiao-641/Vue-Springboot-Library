<template>
  <header class="topbar">
    <div class="brand-lockup">
      <div class="brand-mark">{{ theme === 'command' ? '⌁' : 'L' }}</div>
      <div>
        <div class="brand-name">{{ brand.name }}</div>
        <div class="brand-subtitle">{{ brand.subtitle }}</div>
      </div>
    </div>
    <div class="topbar-meta">
      <ThemeSelector />
      <span class="system-status"><span class="status-dot" />{{ theme === 'command' ? 'NODE ONLINE' : '系统在线' }}</span>
      <el-dropdown>
        <button class="profile-trigger" type="button">
          <span class="avatar">{{
            (user.nickName || user.username || "U").slice(0, 1)
          }}</span
          ><span class="profile-name">{{ user.nickName || user.username || "用户" }}</span
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
import { mapState } from 'vuex';
import ThemeSelector from './ThemeSelector';
export default {
  name: "Header",
  components: { ThemeSelector },
  data: () => ({ user: {} }),
  computed: {
    ...mapState(['theme']),
    brand() {
      return {
        atlas: { name: 'Library Atlas', subtitle: '馆藏运营工作台' },
        academy: { name: '阅见书院', subtitle: '阅读与馆藏' },
        command: { name: 'LIBRARY / CORE', subtitle: '数字流通指挥舱' }
      }[this.theme]
    }
  },
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
  position: relative;
  z-index: 30;
  min-height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  color: var(--header-text);
  background: var(--header-bg);
  border-bottom: 1px solid var(--header-line);
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
  color: var(--theme-on-accent);
  background: var(--theme-accent);
  font-weight: 800;
  font-size: 20px;
}
.brand-name {
  font-weight: 750;
  letter-spacing: 0.02em;
}
.brand-subtitle {
  color: var(--header-muted);
  font-size: 11px;
  margin-top: 1px;
}
.topbar-meta {
  gap: 24px;
}
.system-status {
  gap: 7px;
  color: var(--header-muted);
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
  color: var(--header-text);
  background: transparent;
  cursor: pointer;
  font-weight: 650;
}
.profile-trigger .el-icon {
  color: var(--header-muted);
}
.avatar {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: var(--theme-on-accent);
  background: var(--theme-accent);
  font-size: 13px;
  font-weight: 800;
}
:global(.theme-command) .topbar {
  position: sticky; z-index: 40; top: 12px; width: calc(100% - 108px);
  margin: 12px 18px 0 90px; border: 1px solid var(--theme-line);
  border-radius: 10px; box-shadow: 0 14px 34px rgba(0,0,0,.32);
}
:global(.theme-academy) .brand-name { font-family: Georgia, "Songti SC", serif; font-size: 18px; }
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
  .profile-name { display: none; }
  :global(.theme-command) .topbar { width: calc(100% - 24px); margin: 12px; }
}
</style>
