<script lang="ts" setup>
  import OpenLayersMap from "../widgets/OpenLayersMap.vue";
  import { LayerSubmission } from "../../providers/layerSubmissionProvider.api";

  const props = defineProps<{
    submission: LayerSubmission
  }>();

</script>

<template>
  <open-layers-map :submission="submission"/>
</template>
