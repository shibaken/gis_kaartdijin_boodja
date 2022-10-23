<script lang="ts" setup>
  import DataTable from './DataTable.vue';
  import PlusCircleFill from '../icons/plusCircleFill.vue';
  import CollapsibleRow from './CollapsibleRow.vue';
  import { useCatalogueEntryStore } from '../../stores/CatalogueEntryStore';
  import { storeToRefs } from 'pinia';
  import DataTablePagination from './DataTablePagination.vue';
  import {onMounted} from "vue";

  // get Stores and fetch with `storeToRef` to
  const catalogueEntryStore = useCatalogueEntryStore();
  const { catalogueEntries, numPages, pageSize, currentPage, filter } = storeToRefs(catalogueEntryStore);
  const { getCatalogueEntries } = catalogueEntryStore;

  function setPage (pageNumber: number) {
    filter.value.set('pageNumber', pageNumber);
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
      <CollapsibleRow v-for="(row, index) in catalogueEntries" :id="index">
        <template #cells>
          <td>{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ row.custodian }}</td>
          <td>{{ row.status }}</td>
          <td>{{ row.updatedAt }}</td>
          <td>{{ row.updatedAt }}</td>
          <td>{{ row.assignedTo }}</td>
          <td><a href="#">View</a><a href="#">History</a></td>
        </template>
        <template #content>
          <td colspan="8">
            <span class="fw-bold small">Catalogue layer description: </span>{{ row.description }}
          </td>
        </template>
      </CollapsibleRow>
      <tr>
        <td colspan="9"><PlusCircleFill colour="#4284BC"></PlusCircleFill></td>
      </tr>
    </template>
    <template #pagination>
      <DataTablePagination :currentPage="currentPage" :numPages="numPages" :pageSize="pageSize"
                           :total="catalogueEntries.length" @setPage="setPage"/>
    </template>
  </data-table>
</template>
