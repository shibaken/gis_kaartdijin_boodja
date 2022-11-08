<script lang="ts" setup>
  import DataTable from "./DataTable.vue";
  import PlusCircleFill from "../icons/plusCircleFill.vue";
  import CollapsibleRow from "./CollapsibleRow.vue";
  import DataTablePagination from "./DataTablePagination.vue";
  import { onMounted } from "vue";
  import { useLayerSubmissionStore } from "../../stores/LayerSubmissionStore";
  import { storeToRefs } from "pinia";
  import { DateTime } from "luxon";

  // get Stores and fetch with `storeToRef` to
  const layerSubmissionStore = useLayerSubmissionStore();
  const { layerSubmissions, numPages, currentPage, filters, pageSize } = storeToRefs(layerSubmissionStore);
  const { getLayerSubmissions } = layerSubmissionStore;

  function setPage (pageNumber: number) {
    filters.value.set("pageNumber", pageNumber);
  }

  onMounted(() => {
    getLayerSubmissions();
  });
</script>

<template>
  <data-table>
    <template #headers>
      <tr>
        <th></th>
        <th>Number</th>
        <th>Name</th>
        <th>Submitted Date</th>
        <th>Time</th>
        <th>Catalogue</th>
        <th>Status</th>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <CollapsibleRow v-for="(row, index) in layerSubmissions" :key="index" :id="index">
        <template #cells>
          <td>{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ DateTime.fromISO(row.submittedDate).toFormat('dd/MM/yyyy')}}</td>
          <td>{{ DateTime.fromISO(row.submittedDate).toFormat('HH:mm') }}</td>
          <td>{{ row.catalogueEntry }}</td>
          <td>{{ row.status.label }}</td>
          <td>
            <a href="#">View</a>
          </td>
        </template>
        <template #content>
          <td colspan="9">
            <span class="fw-bold small">Catalogue layer description: </span>
          </td>
        </template>
      </CollapsibleRow>
      <tr>
        <td colspan="8"><PlusCircleFill colour="#4284BC"></PlusCircleFill></td>
      </tr>
    </template>
    <template #pagination>
      <DataTablePagination :current-page="currentPage" :num-pages="numPages" :page-size="pageSize"
                           :total="layerSubmissions.length" @setPage="setPage"/>
    </template>
  </data-table>
</template>
