<script lang="ts" setup>
  import { useLayerSubscriptionStore, subscriptionStatuses,
    LayerSubscriptionStore } from "../../stores/LayerSubscriptionStore";
  import FormInput from "./FormInput.vue";
  import FormSelect from "./FormSelect.vue";
  import { storeToRefs } from "pinia";
  import { DateTime } from "luxon";
  import { onMounted, ref, Ref } from "vue";
  import { LayerSubscriptionStatus, RecordStatus } from "../../backend/backend.api";
  import { LayerSubmissionFilter } from "../../providers/layerSubmissionProvider.api";

  // get Stores and fetch with `storeToRef` to
  const layerSubscriptionStore = useLayerSubscriptionStore();
  const { filters }: Pick<LayerSubscriptionStore, "filters"> = storeToRefs(layerSubscriptionStore);
  const { setFilter } = layerSubscriptionStore;
  const statuses: Ref<RecordStatus<LayerSubscriptionStatus>[]> = ref([]);

  function setDateFilter (field: keyof LayerSubmissionFilter, dateString: string) {
    // Date inputs trigger change events when moving between day/month/year
    const dateObject = DateTime.fromISO(dateString);
    if (dateString !== "" && !dateObject.isValid && dateObject.year.toString().length === 4 ||
      formatShortDate(dateString) !== dateString) {
      return;
    }

    setFilter({
      field,
      value: DateTime.fromISO(dateString).toISO({ suppressMilliseconds: true, includeOffset: false })
    });
  }

  function formatShortDate(date: string | undefined) {
    const dateObject = DateTime.fromISO(date || "");
    // Ensure user has finished typing the date. (0001 is a valid date!)
    return dateObject.isValid && dateObject.year.toString().length === 4 ? dateObject.toFormat('yyyy-MM-dd') : "";
  }

  // Catch input clear button
  function clearFilter (field: keyof LayerSubmissionFilter, value: unknown) {
    const parsedValue: string = Number.isInteger(value) ? (value as number).toString() : value as string;
    if (parsedValue === "") {
      setDateFilter(field, parsedValue);
    }
  }

  onMounted(async () => {
    return statuses.value = await subscriptionStatuses;
  });
</script>

<template>
  <form-select field="status" name="Status" :values="statuses.map(status => [status.label, status.id])"
               @value-updated="(field, value) => setFilter({ field, value })"/>
  <form-input field="subscribedFrom" name="Subscribed from" type="date" placeholder="DD/MM/YYYY"
              :value="formatShortDate(filters.subscribedFrom)"
              @value-blurred="(name, value) => setDateFilter(name, value.toString())"
              @value-updated="clearFilter"/>
  <form-input field="subscribedTo" name="Subscribed to" type="date" placeholder="DD/MM/YYYY"
              :value="formatShortDate(filters.subscribedTo)"
              @value-blurred="(name, value) => setDateFilter(name, value.toString())"
              @value-updated="clearFilter"/>
</template>
