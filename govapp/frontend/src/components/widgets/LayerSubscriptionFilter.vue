<script lang="ts" setup>
  import { useLayerSubscriptionStore, subscriptionStatuses } from "../../stores/LayerSubscriptionStore";
  import FormInput from "./FormInput.vue";
  import FormSelect from "./FormSelect.vue";
  import { storeToRefs } from "pinia";
  import { DateTime } from "luxon";

  // get Stores and fetch with `storeToRef` to
  const layerSubscriptionStore = useLayerSubscriptionStore();
  const { filters } = storeToRefs(layerSubscriptionStore);
  const { setFilter } = layerSubscriptionStore;

  function setDateFilter (field: string, dateString: string) {
    setFilter({
      field,
      value: DateTime.fromISO(dateString).toISO({ suppressMilliseconds: true, includeOffset: false })
    });
  }

  const statuses = await subscriptionStatuses;
</script>

<template>
  <form-select field="status" name="Status" :values="statuses.map(status => [status.label, status.id])"
               @value-updated="(field, value) => setFilter({ field, value })"/>
  <form-input field="subscribedFrom" name="Subscribed from" type="date" placeholder="DD/MM/YYYY"
              :value="filters.subscribedFrom" @value-updated="(name, value) => setDateFilter(name, value)"/>
  <form-input field="subscribedTo" name="Subscribed to" type="date" placeholder="DD/MM/YYYY"
              :value="filters.subscribedTo" @value-updated="(name, value) => setDateFilter(name, value)"/>
</template>
