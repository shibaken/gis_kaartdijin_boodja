<script lang="ts" setup>
  import { computed, ComputedRef } from "vue";
  import { useCatalogueEntryStore } from "../../stores/CatalogueEntryStore";
  import Select from "./FormSelect.vue";
  import Input from "./FormInput.vue";
  import { storeToRefs } from "pinia";
  import { UserProvider } from "../../providers/userProvider";
  import { StatusProvider } from "../../providers/statusProvider";
  import { DateTime } from "luxon";
  import { CatalogueEntryStatus, RecordStatus } from "../../backend/backend.api";

  // get Stores and fetch with `storeToRef` to
  const catalogueEntryStore = useCatalogueEntryStore();
  const { filters, catalogueEntries } = storeToRefs(catalogueEntryStore);
  const { setFilter } = catalogueEntryStore;
  const custodians = computed(() => {
    const allCustodians = catalogueEntries.value.map(({ custodian }) => custodian);
    return UserProvider.getUniqueUsers(allCustodians);
  });
  const assignedTo = computed(() => {
    const allAssignedTo = catalogueEntries.value.map(({ assignedTo }) => assignedTo);
    return UserProvider.getUniqueUsers(allAssignedTo);
  });
  const statuses: ComputedRef<RecordStatus<CatalogueEntryStatus>[]> = computed(() => {
    const allStatuses = catalogueEntries.value.map(({ status }) => status);
    return StatusProvider.getUniqueStatuses(allStatuses);
  });

  function setDateFilter (field: string, dateString: string) {
    setFilter({
      field,
      value: DateTime.fromISO(dateString).toISO({ suppressMilliseconds: true, includeOffset: false })
    });
  }
</script>

<template>
  <Select field="custodian" name="Custodian" :values="custodians.map(custodian => [custodian.username, custodian.id])"
          :value="filters.custodian" @value-updated="(field, value) => setFilter({ field, value })"/>
  <Select field="status" name="Status" :values="statuses.map(status => [status.label, status.id])" :value="filters.status"
          @value-updated="(field, value) => setFilter({ field, value })"/>
  <Input field="updateFrom" name="Last Updated From" type="date" placeholder="DD/MM/YYYY" :value="filters.updateFrom"
         @value-updated="(field, value) => setDateFilter(field, value)"/>
  <Input field="updateTo" name="Last Updated To" type="date" placeholder="DD/MM/YYYY" :value="filters.updateTo"
         @value-updated="(field, value) => setDateFilter(field, value)"/>
  <Select field="assignedTo" name="Assigned to" :values="assignedTo.map(assigned => [assigned.username, assigned.id])"
          :value="filters.assignedTo" @value-updated="(field, value) => setFilter({ field, value })"/>
</template>
