<script lang="ts" setup>
  import LogsCard from "./widgets/LogsCard.vue";
  import WorkflowCard from "./widgets/WorkflowCard.vue";
  import type { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
  import { useEntryWorkflowComposable } from "../tools/workflowComposable";
  import { watch } from "vue";
  import { WorkFlowComposable } from "../tools/workflowComposable.api";

  const props = defineProps<{
    entry: CatalogueEntry | undefined
  }>();

  let workflowComposable: WorkFlowComposable;
  // TODO: workflow composable refactor for subscriptions
  if (props.entry) {
    workflowComposable = useEntryWorkflowComposable(props.entry);
    watch(props, () => workflowComposable.currentEntry.value = props.entry!);
  }
</script>

<template>
  <div class="me-4">
    <logs-card class="mb-4"/>
    <workflow-card v-if="workflowComposable" class="mb-4" :workflow-composable="workflowComposable"/>
  </div>
</template>
