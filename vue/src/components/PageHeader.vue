<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">{{ displayEyebrow }}</div>
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="description" class="page-description">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="page-actions">
      <slot name="actions" />
    </div>
  </div>
</template>
<script>
import { mapState } from "vuex";
export default {
  name: "PageHeader",
  props: {
    eyebrow: { type: String, default: "" },
    title: { type: String, required: true },
    description: { type: String, default: "" },
  },
  computed: {
    ...mapState(["theme"]),
    displayEyebrow() {
      if (this.eyebrow) return this.eyebrow;
      return {
        atlas: "Library Atlas / Operations",
        academy: "阅见书院 · 馆藏志",
        command: "LIBRARY CORE // CONSOLE",
      }[this.theme];
    },
  },
};
</script>
