<script lang="ts" setup>
  import FormSelect from "./FormSelect.vue";
  import Card from "./Card.vue";
  import { PermissionsComposable } from "../../tools/permissionsComposable.api";

  const props = defineProps<{
    permissionsComposable: PermissionsComposable,
  }>();

  const permissionsComposable = props.permissionsComposable;
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
        <span class="link">{{ permissionsComposable.currentEntry.value?.status?.label }}</span>
      </div>
      <div class="d-flex flex-column">
          <form-select field="assignedTo" name="Currently assigned to"
                       :disabled="!permissionsComposable.canAssign.value" :show-empty="true"
                       :values="permissionsComposable.assignableUsers.value?.map(value => [value.username, value.id])"
                       :value="permissionsComposable.currentEntry.value?.assignedTo?.id.toString()"
                       @value-updated="(username, id) => permissionsComposable.assignUser(parseInt(id))"/>
          <button v-if="permissionsComposable.canAssign.value" class="btn btn-link btn-sm align-self-end"
                  @click="() => permissionsComposable.assignMe()">
            Assign to me
          </button>
      </div>
      <div class="w-100 my-3 border-top"></div>
      <div class="d-flex flex-column gap-3">
        <button class="btn btn-info w-100 text-white" :disabled="!permissionsComposable.hasLockPermissions.value"
                @click="permissionsComposable.lockClicked">
          {{ permissionsComposable.canLock.value ? "Lock" : "Unlock" }}
        </button>
        <button class="btn btn-info w-100 text-white" :disabled="!permissionsComposable.hasLockPermissions.value"
                @click="permissionsComposable.declineClicked">Decline</button>
      </div>
    </template>
  </card>
</template>

<style>
  .link {
    color: #25a5ed!important;
  }
</style>
