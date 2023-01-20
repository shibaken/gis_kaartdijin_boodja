<script lang="ts" setup>
  import CataloguePage from "./components/CataloguePage.vue";
  import { catalogueEntryProvider } from "./providers/catalogueEntryProvider";
  import { onMounted } from "vue";
  import { logsProvider } from "./providers/logsProvider";

  onMounted(() => {
    catalogueEntryProvider.init();
    logsProvider.init();
  });
</script>

<template>
  <div class="mx-4">
    <CataloguePage/>
  </div>
</template>
