<script lang="ts" setup async>
  import DataTable from "./DataTable.vue";
  import PlusCircleFill from "../icons/plusCircleFill.vue";
  import CollapsibleRow from "./CollapsibleRow.vue";
  import { useCatalogueEntryStore } from "../../stores/CatalogueEntryStore";
  import { storeToRefs } from "pinia";
  import DataTablePagination from "./DataTablePagination.vue";
  import { onMounted } from "vue";
  import { DateTime } from "luxon";
  import { CatalogueView } from "../viewState.api";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";

  // get Stores and fetch with `storeToRef` to
  const catalogueEntryStore = useCatalogueEntryStore();
  const { catalogueEntries, numPages, pageSize, currentPage, filters } = storeToRefs(catalogueEntryStore);
  const { getCatalogueEntries } = catalogueEntryStore;

  const emit = defineEmits<{
    (e: "show-view", view: CatalogueView, catalogueEntry: CatalogueEntry): void
  }>();

  function setPage (pageNumber: number) {
    filters.value.set("pageNumber", pageNumber);
  }

  onMounted(() => {
    getCatalogueEntries();
  });
</script>

<template>
  <data-table>
    <template #headers>
      <tr>
        <th></th>
        <th>Number</th>
        <th>Name</th>
        <th>Custodian</th>
        <th>Status</th>
        <th>Last Updated</th>
        <th>Time</th>
        <th>Assigned To</th>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <CollapsibleRow v-for="(row, index) in catalogueEntries" :id="index" :key="index">
        <template #cells>
          <td>{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ row.custodian?.username }}</td>
          <td>{{ row.status.label }}</td>
          <td>{{ DateTime.fromISO(row.updatedAt).toFormat('dd/MM/yyyy')}}</td>
          <td>{{ DateTime.fromISO(row.updatedAt).toFormat('HH:mm') }}</td>
          <td>{{ row.assignedTo?.username }}</td>
          <td>
            <a href="#" class="me-2" @click="emit('show-view', 'view', row)">View</a>
            <a href="#">History</a>
          </td>
        </template>
        <template #content>
          <td colspan="9">
            <span class="fw-bold small">Catalogue layer description: </span>{{ row.description }}
          </td>
        </template>
      </CollapsibleRow>
      <tr>
        <td colspan="9"><PlusCircleFill colour="#4284BC"></PlusCircleFill></td>
      </tr>
    </template>
    <template #pagination>
      <DataTablePagination :current-page="currentPage" :num-pages="numPages" :page-size="pageSize"
                           :total="catalogueEntries.length" @set-page="setPage"/>
    </template>
  </data-table>
</template>
