<script lang="ts" setup>
  import Card from "./Card.vue";

</script>

<template>
  <card>
    <template #header>
      <h4>Logs</h4>
    </template>
    <template #body>
      <div class="w-100">
        <small>Communications</small>
      </div>
      <a class="link">Show</a>
      <span class="link"> | </span>
      <a class="link">Add Entry</a>
      <div class="w-100 my-3 border-top"></div>
      <div class="w-100">
        <small>Actions</small>
      </div>
      <a class="link">Show</a>
    </template>
  </card>
</template>

<style>
  .link {
    color: #25a5ed!important;
  }
</style>