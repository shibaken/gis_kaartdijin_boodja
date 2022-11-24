<script lang="ts" setup>
  import Card from "./Card.vue";
  import NotificationDatatable from "../dataTable/NotificationDatatable.vue";
</script>

<template>
  <card class="mt-4">
    <template #header>
      <h4>Notifications</h4>
    </template>
    <template #body>
      <notification-datatable/>
    </template>
  </card>
</template>
