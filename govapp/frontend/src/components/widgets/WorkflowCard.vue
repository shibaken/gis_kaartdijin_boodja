<script lang="ts" setup>
  import FormSelect from "./FormSelect.vue";
  import Card from "./Card.vue";
  import { User } from "../../backend/backend.api";
  import { UserProvider } from "../../providers/userProvider";
  import { onMounted, ref } from "vue";

  withDefaults(defineProps<{
      assignees: Array<User>
    }>(),
    {
      assignees: () => []
    });

  const userProvider = new UserProvider();
  const users = ref<Array<[string, string | number]>>([]);
  onMounted(async () => {
    for (const user of await userProvider.fetchUsers()) {
      users.value.push([user.username, user.id]);
    }
  });

</script>

<template>
  <card>
    <template #header>
      <h4>Workflow</h4>
    </template>
    <template #body>
      <div class="mb-2">
        <div class="w-100">
          <small>Status</small>
        </div>
        <span class="link">Locked</span>
      </div>
      <div class="d-flex flex-column">
        <form-select field="assignedTo" name="Currently assigned to" :values="users"/>
        <button class="btn btn-link btn-sm align-self-end">Assign to me</button>
      </div>
      <div class="w-100 my-3 border-top"></div>
      <div class="d-flex flex-column gap-3">
        <button class="btn btn-info w-100 text-white">Unlock</button>
        <button class="btn btn-info w-100 text-white">Cancel</button>
      </div>
    </template>
  </card>
</template>

<style>
  .link {
    color: #25a5ed!important;
  }
</style>
