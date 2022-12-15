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
          <form-select field="assignedTo" name="Currently assigned to"
                       :disabled="!workflowComposable.canAssign.value"
                       :values="workflowComposable.assignableUsers.value?.map(value => [value.username, value.id])"
                       :value="workflowComposable.currentEntry.value?.assignedTo?.id.toString()"
                       @value-updated="(username, id) => workflowComposable.assignUser(parseInt(id))"/>
          <button v-if="workflowComposable.canAssign.value" class="btn btn-link btn-sm align-self-end"
                  @click="() => workflowComposable.assignMe()">
            Assign to me
          </button>
      </div>
      <div class="w-100 my-3 border-top"></div>
      <div class="d-flex flex-column gap-3">
        <button class="btn btn-info w-100 text-white" :disabled="!workflowComposable.hasLockPermissions.value"
                @click="workflowComposable.lockClicked">
          {{ workflowComposable.canLock.value ? "Lock" : "Unlock" }}
        </button>
      </div>
    </template>
  </card>
</template>

<style>
  .link {
    color: #25a5ed!important;
  }
</style>
