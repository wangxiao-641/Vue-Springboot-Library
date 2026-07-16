<template>
  <div class="app-shell">
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
export default { name: "Layout", components: { Header, Aside } };
</script>
