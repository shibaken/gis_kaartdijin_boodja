<script lang="ts" setup>
  import FormSelect from "./FormSelect.vue";
  import Card from "./Card.vue";
  import { userProvider } from "../../providers/userProvider";
  import { onMounted, ref } from "vue";
  import { User } from "../../backend/backend.api";

  const props = defineProps<{
    assignedTo: number | undefined
  }>();

  const emit = defineEmits<{
    (e: "assign-user", userId: number): void,
    (e: "assign-me"): void
  }>();

  const users = ref<Array<[string, string | number]>>([]);
  const me = ref<User>();

  onMounted(async () => {
    users.value = (await userProvider.users)
      .map(user => {
        return [user.username, user.id]
      });

    me.value = await userProvider.me;
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
        <form-select field="assignedTo" name="Currently assigned to" :values="users" :value="assignedTo?.toString()"
                     @value-updated="(username, id) => emit('assign-user', parseInt(id))"/>
        <button class="btn btn-link btn-sm align-self-end"
                @click="() => emit('assign-me')">
          Assign to me
        </button>
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
