<script lang="ts" setup>
  import Card from "./Card.vue";
  import { useModalStore } from "../../stores/ModalStore";
  import { ModalTypes } from "../../stores/ModalStore.api";

  const modalStore = useModalStore();

  function onLogShowClick () {
    modalStore.showModal(ModalTypes.CommsLog);
  }

  function onLogAddClick () {
    modalStore.showModal(ModalTypes.CommsLogAdd);
  }
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
      <a class="link" @click="onLogShowClick">Show</a>
      <span class="link"> | </span>
      <a class="link" @click="onLogAddClick">Add Entry</a>
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