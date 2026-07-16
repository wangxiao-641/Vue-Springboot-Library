<template>
  <div class="app-shell" :data-layout="theme">
    <Header />
    <div class="app-body">
      <Aside />
      <main class="app-main"><router-view /></main>
    </div>
  </div>
</template>
<script>
import Header from "../components/Header";
import Aside from "../components/Aside";
import { mapState } from 'vuex';
export default { name: "Layout", components: { Header, Aside }, computed: { ...mapState(['theme']) } };
</script>
