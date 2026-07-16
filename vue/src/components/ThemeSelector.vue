<template>
  <div class="theme-selector" role="group" aria-label="选择界面风格">
    <button
      v-for="(meta, key) in themes"
      :key="key"
      type="button"
      class="theme-option"
      :class="{ active: theme === key }"
      :aria-pressed="theme === key"
      :aria-label="`切换到${meta.label}`"
      :title="meta.label"
      @click="setTheme(key)"
    >
      <span class="theme-swatch" :class="`swatch-${key}`" aria-hidden="true"></span>
      <span class="theme-label">{{ meta.label }}</span>
    </button>
  </div>
</template>
<script>
import { mapMutations, mapState } from 'vuex'
import { THEMES } from '../store'
export default {
  name: 'ThemeSelector',
  computed: { ...mapState(['theme']), themes: () => THEMES },
  methods: { ...mapMutations(['setTheme']) }
}
</script>
<style scoped>
.theme-selector { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.theme-option {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 9px;
  border: 1px solid transparent; border-radius: 999px; color: var(--theme-muted);
  background: transparent; cursor: pointer; font-size: 12px; white-space: nowrap;
}
.theme-option:hover, .theme-option:focus-visible { border-color: var(--theme-accent); outline: none; }
.theme-option.active { color: var(--theme-accent); border-color: var(--theme-accent); background: var(--theme-accent-soft); font-weight: 750; }
.theme-swatch { width: 9px; height: 9px; border-radius: 50%; background: var(--theme-accent); }
.swatch-atlas { background: #12b8a6; }
.swatch-academy { background: #b44d3c; }
.swatch-command { background: #8b7cff; }
@media (max-width: 1120px) {
  .theme-label { display: none; }
  .theme-option { padding: 4px; }
  .theme-swatch { display: grid; place-items: center; width: 23px; height: 23px; color: #fff; font-size: 10px; font-weight: 800; }
  .swatch-atlas::after { content: "A"; }
  .swatch-academy::after { content: "书"; }
  .swatch-command::after { content: "C"; }
}
</style>
