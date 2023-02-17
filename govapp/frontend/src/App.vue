<script lang="ts" setup>
  import CataloguePage from "./components/CataloguePage.vue";
  import { catalogueEntryProvider } from "./providers/catalogueEntryProvider";
  import { computed, ComputedRef, onMounted, ref } from "vue";
  import type { Component } from "vue";
  import { logsProvider } from "./providers/logsProvider";
  import PublishPage from "./components/PublishPage.vue";
  import { publisherProvider } from "./providers/publisherProvider";

  const routes: Record<string, Component> = {
    '#catalogue': CataloguePage,
    '#publish': PublishPage
  }
  const currentPath = ref(window.location.hash);
  const currentView: ComputedRef<Component> = computed(() => routes[currentPath.value || "#catalogue"] || CataloguePage)

  window.addEventListener('hashchange', () => currentPath.value = window.location.hash);


  onMounted(() => {
    catalogueEntryProvider.init();
    logsProvider.init();
    publisherProvider.init();
  });
</script>

<template>
  <div class="mx-4">
    <component :is="currentView"/>
  </div>
</template>
