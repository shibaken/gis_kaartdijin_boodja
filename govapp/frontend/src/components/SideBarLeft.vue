<script lang="ts" setup>
  import LogsCard from "./widgets/LogsCard.vue";
  import WorkflowCard from "./widgets/WorkflowCard.vue";
  import type { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
  import { catalogueEntryProvider } from "../providers/catalogueEntryProvider";
  import { useEntryWorkflowComposable } from "../tools/workflowComposable";
  import { watch } from "vue";
  import { WorkFlowComposable } from "../tools/workflowComposable.api";

  const props = defineProps<{
    entry: CatalogueEntry | undefined
  }>();

  let workflowComposable: WorkFlowComposable;
  if (props.entry) {
    workflowComposable = useEntryWorkflowComposable(props.entry);
    watch(props, () => workflowComposable.currentEntry.value = props.entry!);
  }

  function assignUser (userId: number) {
    if (props.entry) {
      catalogueEntryProvider.assignUser(props.entry.id, userId);
    }
  }
</script>

<template>
  <div class="me-4">
    <logs-card class="mb-4"/>
    <workflow-card class="mb-4" :workflow-composable="workflowComposable"/>
  </div>
</template>
