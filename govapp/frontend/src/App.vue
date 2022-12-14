<script setup lang="ts">
  import CataloguePage from "./components/CataloguePage.vue";
  import { onMounted } from "vue";
  import { catalogueEntryProvider } from "./providers/catalogueEntryProvider";

  onMounted(() => {
    catalogueEntryProvider.init();
  });
</script>

<template>
  <div class="mx-4">
    <CataloguePage/>
  </div>
</template>
