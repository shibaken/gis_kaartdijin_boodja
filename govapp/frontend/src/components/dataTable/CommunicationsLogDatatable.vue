<script lang="ts" setup async>
  import DataTable from "./DataTable.vue";
  import { storeToRefs } from "pinia";
  import { onMounted, watch } from "vue";
  import { NavigationCatalogueEmits } from "../viewState.api";
  import SortableHeader from "./SortableHeader.vue";
  import { useTableSortComposable } from "../../tools/sortComposable";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import { logsProvider } from "../../providers/logsProvider";
  import { useLogsStore } from "../../stores/LogsStore";
  import { RawCatalogueEntryFilter } from "../../backend/backend.api";

  const { communicationLogs, communicationLogsMeta, filters, setFilter } = storeToRefs(useLogsStore());
  watch(filters.value, () => {
    logsProvider.fetchCommunicationLogs(props.catalogueEntry.id, filters.value)
  });

  const props = defineProps<{
    catalogueEntry: CatalogueEntry
  }>();
  // get Stores and fetch with `storeToRef` to


  /**
   * Workaround for external typing. See https://vuejs.org/api/sfc-script-setup.html#type-only-props-emit-declarations
   */
  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationCatalogueEmits {}
  const emit = defineEmits<NavEmits>();

  function setPage (pageNumber: number) {
    filters.value.offset = (pageNumber - 1) * (filters.value.limit || 10);
  }

  function setPageSize (size: number) {
    filters.value.limit = size;
  }

  const { sortDirection, onSort } = useTableSortComposable<RawCatalogueEntryFilter>(filters);

  onMounted(() => {
    filters.value.limit = 10;
    logsProvider.fetchCommunicationLogs(props.catalogueEntry.id, filters.value);
  });
</script>

<template>
  <data-table @set-page="setPage" @set-page-size="setPageSize" :total="communicationLogsMeta.total" :paginate="true">
    <template #headers>
      <tr>
        <SortableHeader name="Date" column="createdAt" :direction="sortDirection('createdAt')" @sort="onSort"/>
        <SortableHeader name="Type" column="type" :direction="sortDirection('type')" @sort="onSort"/>
        <SortableHeader name="To" column="to" :direction="sortDirection('to')" @sort="onSort"/>
        <SortableHeader name="CC" column="cc" :direction="sortDirection('cc')" @sort="onSort"/>
        <SortableHeader name="From" column="from" :direction="sortDirection('from')" @sort="onSort"/>
        <SortableHeader name="Subject/Desc." column="subject" :direction="sortDirection('subject')" @sort="onSort"/>
        <SortableHeader name="Text" column="text" :direction="sortDirection('text')" @sort="onSort"/>
        <SortableHeader name="Documents" column="user" :direction="sortDirection('user')" @sort="onSort"/>
      </tr>
    </template>
    <template #data>
      <tr v-for="(row, index) in communicationLogs" :key="index" :class="{ 'table-active': index % 2 === 0 }">
        <td>{{ row.createdAt }}</td>
        <td>{{ row.type.label }}</td>
        <td>{{ row.to }}</td>
        <td>{{ row.cc }}</td>
        <td>{{ row.from }}</td>
        <td>{{ row.subject }}</td>
        <td>{{ row.text }}</td>
        <td></td>
      </tr>
    </template>
  </data-table>
</template>
