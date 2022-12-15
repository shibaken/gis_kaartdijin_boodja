<script lang="ts" setup>
  import FormSelect from "./FormSelect.vue";
  import Card from "./Card.vue";
  import { WorkFlowComposable } from "../../tools/workflowComposable.api";

  const props = defineProps<{
    workflowComposable: WorkFlowComposable,
  }>();

  const workflowComposable = props.workflowComposable;
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
        <span class="link">{{ workflowComposable.currentEntry.value?.status?.label }}</span>
      </div>
      <div class="d-flex flex-column">
        <template v-if="workflowComposable.hasLockPermissions">
          <form-select field="assignedTo" name="Currently assigned to"
                       :values="workflowComposable.assignableUsers.value?.map(value => [value.username, value.id])"
                       :value="workflowComposable.currentEntry.value?.assignedTo?.id.toString()"
                       @value-updated="(username, id) => workflowComposable.assignUser(parseInt(id))"/>
          <button class="btn btn-link btn-sm align-self-end" @click="() => workflowComposable.assignMe()">
            Assign to me
          </button>
        </template>
      </div>
      <div class="w-100 my-3 border-top"></div>
      <div class="d-flex flex-column gap-3">
        <button class="btn btn-info w-100 text-white" :class="{ disabled: !workflowComposable.hasLockPermissions }"
                @click="workflowComposable.lockClicked">
          {{ workflowComposable.canLock.value ? "Lock" : "Unlock" }}
        </button>
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
