<script lang="ts" setup>
  import LogsCard from "./widgets/LogsCard.vue";
  import WorkflowCard from "./widgets/WorkflowCard.vue";
  import type { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
  import { CatalogueEntryProvider } from "../providers/catalogueEntryProvider";

  const props = defineProps<{
    catalogueEntry: CatalogueEntry
  }>();
  const catalogueEntryProvider = new CatalogueEntryProvider();

  function assignUser (userId: number) {
    catalogueEntryProvider.assignUser(userId, props.catalogueEntry.id);
  }

  function assignMe () {
    catalogueEntryProvider.assignMe(props.catalogueEntry.id);
  }
</script>

<template>
  <div class="me-4">
    <logs-card class="mb-4"/>
    <workflow-card class="mb-4" :assigned-to="props.catalogueEntry?.assignedTo?.id" @assign-user="assignUser"
                   @assign-me="assignMe"/>
  </div>
</template>
