<script lang="ts" setup>
  import { computed } from "vue";
  import { useCatalogueEntryStore, entryStatuses } from "../../stores/CatalogueEntryStore";
  import FormInput from "./FormInput.vue";
  import FormSelect from "./FormSelect.vue";
  import { storeToRefs } from "pinia";
  import { UserProvider } from "../../providers/userProvider";
  import { DateTime } from "luxon";

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

  function setDateFilter (field: string, dateString: string) {
    setFilter({
      field,
      value: DateTime.fromISO(dateString).toISO({ suppressMilliseconds: true, includeOffset: false })
    });
  }

  const statuses = await entryStatuses;
</script>

<template>
  <form-select field="custodian" name="Custodian" :values="custodians.map(custodian => [custodian.username, custodian.id])"
          :value="filters.custodian" @value-updated="(field, value) => setFilter({ field, value })"/>
  <form-select field="status" name="Status" :values="statuses.map(status => [status.label, status.id])" :value="filters.status"
          @value-updated="(field, value) => setFilter({ field, value })"/>
  <form-input field="updateFrom" name="Last Updated From" type="date" placeholder="DD/MM/YYYY" :value="filters.updateFrom"
         @value-updated="(field, value) => setDateFilter(field, value)"/>
  <form-input field="updateTo" name="Last Updated To" type="date" placeholder="DD/MM/YYYY" :value="filters.updateTo"
         @value-updated="(field, value) => setDateFilter(field, value)"/>
  <form-select field="assignedTo" name="Assigned to" :values="assignedTo.map(assigned => [assigned.username, assigned.id])"
          :value="filters.assignedTo" @value-updated="(field, value) => setFilter({ field, value })"/>
</template>
