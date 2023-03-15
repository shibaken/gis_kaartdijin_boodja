<script lang="ts" setup>
  import LogsCard from "./widgets/LogsCard.vue";
  import WorkflowCard from "./widgets/WorkflowCard.vue";
  import type { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
  import { usePermissionsComposable } from "../tools/permissionsComposable";
  import { watch } from "vue";
  import { PermissionsComposable } from "../tools/permissionsComposable.api";
  import { PublishEntry } from "../providers/publisherProvider.api";

  const props = defineProps<{
    entry: CatalogueEntry | PublishEntry | undefined
  }>();

  let permissionsComposable: PermissionsComposable = usePermissionsComposable(props.entry);
  watch(props, () => permissionsComposable.updateCurrentEntry(props.entry));
</script>

<template>
  <div class="me-4">
    <logs-card class="mb-4"/>
    <workflow-card class="mb-4" :permissions-composable="permissionsComposable"/>
  </div>
</template>
