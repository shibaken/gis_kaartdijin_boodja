<script lang="ts" setup>
  import { computed } from "vue";
  import { useCatalogueEntryStore } from "../../stores/CatalogueEntryStore";
  import FormInput from "./FormInput.vue";
  import FormSelect from "./FormSelect.vue";
  import { storeToRefs } from "pinia";
  import { UserProvider } from "../../providers/userProvider";
  import { DateTime } from "luxon";
  import { User } from "../../backend/backend.api";

  // get Stores and fetch with `storeToRef` to
  const catalogueEntryStore = useCatalogueEntryStore();
  const { filters, catalogueEntries, entryStatuses } = storeToRefs(catalogueEntryStore);
  const { setFilter } = catalogueEntryStore;

  const custodians = computed(() => {
    const allCustodians = catalogueEntries.value.map(({ custodian }) => custodian);
    return UserProvider.getUniqueUsers(allCustodians);
  });

  const assignedTo = computed(() => {
    const allAssignedTo = catalogueEntries.value
      .map(({ assignedTo }) => assignedTo as User)
      .filter(user => !!user);
    return UserProvider.getUniqueUsers(allAssignedTo);
  });

  function setDateFilter (field: string, dateString: string) {
    setFilter({
      field,
      value: DateTime.fromISO(dateString).toISO({ suppressMilliseconds: true, includeOffset: false })
    });
  }
</script>

<template>
  <form-select field="custodian" name="Custodian" :values="custodians.map(custodian => [custodian.username, custodian.id])"
               :value="filters.custodian" @value-updated="(field, value) => setFilter({ field, value })"
               :show-empty="true"/>
  <form-select field="status" name="Status" :values="entryStatuses.map(status => [status.label, status.id])"
               :value="filters.status?.toString()" @value-updated="(field, value) => setFilter({ field, value })"
               :show-empty="true"/>
  <form-input field="updateFrom" name="Last Updated From" type="date" placeholder="DD/MM/YYYY" :value="filters.updateFrom"
              @value-updated="(field, value) => setDateFilter(field, value.toString())"/>
  <form-input field="updateTo" name="Last Updated To" type="date" placeholder="DD/MM/YYYY"
              :value="filters.updateTo"
              @value-updated="(field, value) => setDateFilter(field, value.toString())"/>
  <form-select field="assignedTo" name="Assigned to" :values="assignedTo.map(assigned => [assigned.username, assigned.id])"
               :value="filters.assignedTo" @value-updated="(field, value) => setFilter({ field, value })"
               :show-empty="true"/>
</template>
