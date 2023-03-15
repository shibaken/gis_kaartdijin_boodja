<script lang="ts" setup>
  import { onMounted, Ref, ref } from "vue";
  import { usePublishEntryStore } from "../../stores/PublishEntryStore";
  import FormInput from "./FormInput.vue";
  import FormSelect from "./FormSelect.vue";
  import { storeToRefs } from "pinia";
  import { userProvider } from "../../providers/userProvider";
  import { DateTime } from "luxon";
  import { PublishEntryStatus, RecordStatus, User } from "../../backend/backend.api";
  import { PublishEntryFilter } from "../../providers/publisherProvider.api";

  // get Stores and fetch with `storeToRef` to
  const publishEntryStore = usePublishEntryStore();
  type EntryStore = {
    filters: Ref<PublishEntryFilter>,
    publishEntryStatuses: Ref<RecordStatus<PublishEntryStatus>[]>
  }
  const { filters, publishEntryStatuses }: EntryStore = storeToRefs(publishEntryStore);
  const { setFilter } = publishEntryStore;
  const assignedTo: Ref<User[]> = ref([]);

  function setDateFilter (field: keyof PublishEntryFilter, dateString: string) {
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
  function clearFilter (field: keyof PublishEntryFilter, value: unknown) {
    const parsedValue: string = Number.isInteger(value) ? (value as number).toString() : value as string;
    if (parsedValue === "") {
      setDateFilter(field, parsedValue);
    }
  }

  onMounted(async () => {
    assignedTo.value = await userProvider.fetchUsers();

  });
</script>

<template>
  <form-input field="search" name="Search" type="text" :value="filters.search"
              @value-blurred="(name, value) => setFilter({ field: name, value })"
              @value-updated="clearFilter"/>
  <form-select field="status" name="Status" :values="publishEntryStatuses.map(status => [status.label, status.id])"
               :value="filters.status?.toString()" :show-empty="true"
               @value-updated="(field, value) => setFilter({ field, value })"/>
  <form-input field="updatedAfter" name="Last Updated From" type="date" placeholder="DD/MM/YYYY"
              :value="formatShortDate(filters.updatedAfter)"
              @value-blurred="(name, value) => setDateFilter(name, value.toString())"
              @value-updated="clearFilter"/>
  <form-input field="updatedBefore" name="Last Updated To" type="date" placeholder="DD/MM/YYYY"
              :value="formatShortDate(filters.updatedBefore)"
              @value-blurred="(name, value) => setDateFilter(name, value.toString())"
              @value-updated="clearFilter"/>
  <form-select field="assignedTo" name="Assigned to" :values="assignedTo.map(assigned => [assigned.username, assigned.id])"
               :value="filters.assignedTo" @value-updated="(field, value) => setFilter({ field, value })"
               :show-empty="true"/>
</template>
