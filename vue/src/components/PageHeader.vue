<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">{{ eyebrow }}</div>
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="description" class="page-description">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="page-actions">
      <slot name="actions" />
    </div>
  </div>
</template>
<script>
export default {
  name: "PageHeader",
  props: {
    eyebrow: { type: String, default: "Library Atlas" },
    title: { type: String, required: true },
    description: { type: String, default: "" },
  },
};
</script>
