<script lang="ts" setup>
  import { watch } from 'vue';
  import { useTableFilterComposable } from '../../tools/filterComposable';
  import { useCatalogueEntryStore } from '../../stores/CatalogueEntryStore';
  import { CatalogueEntryFilter } from '../../providers/catalogueEntryProvider.api';
  import Select from './Select.vue';
  import Input from './Input.vue';

  const tableFilterComposable = useTableFilterComposable<CatalogueEntryFilter>();
  const { tableFilters, setFilter } = tableFilterComposable;

  // get Stores and fetch with `storeToRef` to
  const catalogueEntryStore = useCatalogueEntryStore();
  const { getCatalogueEntries } = catalogueEntryStore;

  watch(tableFilters, function () {
    getCatalogueEntries();
  });
</script>

<template>
  <Select name="Custodian" :values="['All']" :value="tableFilters.custodian"
          @value-updated="(name, value) => setFilter({ name, value })"/>
  <Select name="Status" :values="['Draft', 'Locked', 'Cancelled']" :value="tableFilters.status"
          @value-updated="(name, value) => setFilter({ name, value })"/>
  <Input name="Last Updated From" type="date" placeholder="DD/MM/YYYY" :value="tableFilters.updateFrom"
         @value-updated="(name, value) => setFilter({ name, value })"/>
  <Input name="Last Updated To" type="date" placeholder="DD/MM/YYYY" :value="tableFilters.updateTo"
         @value-updated="(name, value) => setFilter({ name, value })"/>
  <Select name="Assigned to" :values="['Rodney Sales']" :value="tableFilters.assignedTo"
          @value-updated="(name, value) => setFilter({ name, value })"/>
</template>
