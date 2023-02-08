<script lang="ts" setup>
  import { onMounted, Ref, ref } from "vue";
  import { useCatalogueEntryStore } from "../../stores/CatalogueEntryStore";
  import FormInput from "./FormInput.vue";
  import FormSelect from "./FormSelect.vue";
  import { storeToRefs } from "pinia";
  import { userProvider } from "../../providers/userProvider";
  import { DateTime } from "luxon";
  import { User } from "../../backend/backend.api";
  import { LayerSubmissionFilter } from "../../providers/layerSubmissionProvider.api";
  import type { Custodian } from "../../providers/userProvider.api";

  // get Stores and fetch with `storeToRef` to
  const catalogueEntryStore = useCatalogueEntryStore();
  const { filters, entryStatuses } = storeToRefs(catalogueEntryStore);
  const { setFilter } = catalogueEntryStore;

  const custodians: Ref<Custodian[]> = ref([]);
  const assignedTo: Ref<User[]> = ref([]);

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

  function formatShortDate(date: unknown) {
    const dateObject = DateTime.fromISO(date as string);
    // Ensure user has finished typing the date. (0001 is a valid date!)
    return dateObject.isValid && dateObject.year.toString().length === 4 ? dateObject.toFormat('yyyy-MM-dd') : "";
  }

  // Catch input clear button
  function clearFilter (field: string, value: unknown) {
    const parsedValue: string = Number.isInteger(value) ? (value as number).toString() : value as string;
    if (parsedValue === "") {
      setDateFilter(field, parsedValue);
    }
  }

  onMounted(async () => {
    custodians.value = await userProvider.fetchCustodians();
    assignedTo.value = await userProvider.fetchUsers()
  });
</script>

<template>
  <form-select field="custodian" name="Custodian" :values="custodians.map(cust => [cust.name, cust.id])"
               :value="filters.custodian" @value-updated="(field, value) => setFilter({ field, value })"
               :show-empty="true"/>
  <form-select field="status" name="Status" :values="entryStatuses.map(status => [status.label, status.id])"
               :value="filters.status?.toString()" @value-updated="(field, value) => setFilter({ field, value })"
               :show-empty="true"/>
  <form-input field="updateFrom" name="Last Updated From" type="date" placeholder="DD/MM/YYYY"
              :value="formatShortDate(filters.updateFrom)"
              @value-blurred="(name, value) => setDateFilter(name, value.toString())"
              @value-updated="clearFilter"/>
  <form-input field="updateTo" name="Last Updated To" type="date" placeholder="DD/MM/YYYY"
              :value="formatShortDate(filters.updateTo)"
              @value-blurred="(name, value) => setDateFilter(name, value.toString())"
              @value-updated="clearFilter"/>
  <form-select field="assignedTo" name="Assigned to" :values="assignedTo.map(assigned => [assigned.username, assigned.id])"
               :value="filters.assignedTo" @value-updated="(field, value) => setFilter({ field, value })"
               :show-empty="true"/>
</template>
