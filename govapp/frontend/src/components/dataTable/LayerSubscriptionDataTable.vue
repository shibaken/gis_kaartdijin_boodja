<script lang="ts" setup>
  import DataTable from "./DataTable.vue";
  import PlusCircleFill from "../icons/plusCircleFill.vue";
  import CollapsibleRow from "./CollapsibleRow.vue";
  import DataTablePagination from "./DataTablePagination.vue";
  import { onMounted } from "vue";
  import { useLayerSubscriptionStore } from "../../stores/LayerSubscriptionStore";
  import { storeToRefs } from "pinia";
  import { DateTime } from "luxon";

  // get Stores and fetch with `storeToRef` to
  const layerSubscriptionStore = useLayerSubscriptionStore();
  const { layerSubscriptions, numPages, currentPage, filters, pageSize } = storeToRefs(layerSubscriptionStore);
  const { getLayerSubscriptions } = layerSubscriptionStore;

  function setPage (pageNumber: number) {
    filters.value.set("pageNumber", pageNumber);
  }

  onMounted(() => {
    getLayerSubscriptions();
  });
</script>

<template>
  <data-table>
    <template #headers>
      <tr>
        <th></th>
        <th>Number</th>
        <th>Name</th>
        <th>Subscribed Date</th>
        <th>Time</th>
        <th>Webservice Url</th>
        <th>Status</th>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <CollapsibleRow v-for="(row, index) in layerSubscriptions" :key="index" :id="index">
        <template #cells>
          <td>{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ DateTime.fromISO(row.subscribedDate).toFormat('dd/MM/yyyy')}}</td>
          <td>{{ DateTime.fromISO(row.subscribedDate).toFormat('HH:mm') }}</td>
          <td><a :href="row.url">{{ row.url }}</a></td>
          <td>{{ row.status.label }}</td>
          <td>
            <a href="#" class="me-2">View</a>
            <a href="#">History</a>
          </td>
        </template>
        <template #content>
          <td colspan="8">
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
                           :total="layerSubscriptions.length" @setPage="setPage"/>
    </template>
  </data-table>
</template>
