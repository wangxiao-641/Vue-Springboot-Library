<template>
  <div class="app-root" :class="`theme-${theme}`">
    <router-view />
<!--    头部-->

  </div>

</template>

<style>

</style>
<script>


  import { mapState } from 'vuex'
  export default { name: 'App', computed: { ...mapState(['theme']) } }
</script>
