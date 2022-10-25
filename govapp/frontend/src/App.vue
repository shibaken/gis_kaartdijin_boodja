<script setup lang="ts">
  import CataloguePage from './components/CataloguePage.vue'
  import NavBar from "./components/NavBar.vue";
</script>

<template>
  <div class="container">
    <header>
      <img src="../static/webapp/assets/pvs_logo.gif" alt="Parks and Wildlife logo"/>
    </header>
    <NavBar class="mb-4"/>
    <CataloguePage class="mt-4"/>
  </div>
</template>
