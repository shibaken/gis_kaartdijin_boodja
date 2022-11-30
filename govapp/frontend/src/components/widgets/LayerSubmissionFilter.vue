<script lang="ts" setup>
  import { useLayerSubmissionStore, submissionStatuses } from "../../stores/LayerSubmissionStore";
  import FormInput from "./FormInput.vue";
  import FormSelect from "./FormSelect.vue";
  import { storeToRefs } from "pinia";
  import { DateTime } from "luxon";
  import { onMounted, Ref, ref } from "vue";
  import { LayerSubmissionStatus, RecordStatus } from "../../backend/backend.api";
  import { LayerSubmissionFilter } from "../../providers/layerSubmissionProvider.api";

  // get Stores and fetch with `storeToRef` to
  const layerSubmissionStore = useLayerSubmissionStore();
  const { filters } = storeToRefs(layerSubmissionStore);
  const { setFilter } = layerSubmissionStore;
  const statuses: Ref<RecordStatus<LayerSubmissionStatus>[]> = ref([]);

  function setDateFilter (field: keyof LayerSubmissionFilter, dateString: string) {
    setFilter({
      field,
      value: DateTime.fromISO(dateString).toISO({ suppressMilliseconds: true, includeOffset: false })
    });
  }

  onMounted(async () => {
    statuses.value = await submissionStatuses;
  });
</script>

<template>
  <form-select field="status" name="Status" :values="statuses.map(status => [status.label, status.id])"
               :value="filters.status" @value-updated="(field, value) => setFilter({ field, value })"/>
  <form-input field="submittedFrom" name="Submitted from" type="date" placeholder="DD/MM/YYYY"
              :value="filters.submittedFrom" @value-updated="(name, value) => setDateFilter(name, value)"/>
  <form-input field="submittedTo" name="Submitted to" type="date" placeholder="DD/MM/YYYY"
              :value="filters.submittedTo" @value-updated="(name, value) => setDateFilter(name, value)"/>
</template>
