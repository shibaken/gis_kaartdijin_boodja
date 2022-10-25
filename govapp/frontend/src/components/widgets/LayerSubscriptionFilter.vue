<script lang="ts" setup>
  import { watch } from 'vue';
  import { useTableFilterComposable } from '../../tools/filterComposable';
  import { useLayerSubscriptionStore } from '../../stores/LayerSubscriptionStore';
  import { LayerSubscriptionFilter } from '../../providers/layerSubscriptionProvider.api';
  import Select from './Select.vue';
  import Input from './Input.vue';

  const tableFilterComposable = useTableFilterComposable<LayerSubscriptionFilter>();
  const { tableFilters, setFilter } = tableFilterComposable;

  // get Stores and fetch with `storeToRef` to
  const layerSubscriptionStore = useLayerSubscriptionStore();
  const { getLayerSubscriptions } = layerSubscriptionStore;

  watch(tableFilters, function () {
    getLayerSubscriptions();
  });
</script>

<template>
  <Select name="Status" :values="['Draft', 'Locked', 'Cancelled']" :value="tableFilters.status?.toString() || ''"
          @value-updated="(name, value) => setFilter({ name, value })"/>
  <Input name="Subscribed from" type="date" placeholder="DD/MM/YYYY" :value="tableFilters.subscribedFrom"
         @value-updated="(name, value) => setFilter({ name, value })"/>
  <Input name="Subscribed to" type="date" placeholder="DD/MM/YYYY" :value="tableFilters.subscribedTo"
         @value-updated="(name, value) => setFilter({ name, value })"/>
</template>
