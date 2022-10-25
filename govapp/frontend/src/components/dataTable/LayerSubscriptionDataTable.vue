<script lang="ts" setup>
  import DataTable from './DataTable.vue';
  import PlusCircleFill from '../icons/plusCircleFill.vue';
  import CollapsibleRow from './CollapsibleRow.vue';
  import DataTablePagination from './DataTablePagination.vue';
  import { onMounted } from 'vue';
  import { useLayerSubscriptionStore } from '../../stores/LayerSubscriptionStore';
  import { storeToRefs } from 'pinia';

  // get Stores and fetch with `storeToRef` to
  const layerSubscriptionStore = useLayerSubscriptionStore();
  const { layerSubscriptions, numPages, currentPage, filter, pageSize } = storeToRefs(layerSubscriptionStore);
  const { getLayerSubscriptions } = layerSubscriptionStore;

  function setPage (pageNumber: number) {
    filter.value.set('pageNumber', pageNumber);
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
      <CollapsibleRow v-for="(row, index) in layerSubscriptions" :id="index">
        <template #cells>
          <td>
            {{ row.id }}
          </td>
          <td>{{ row.name }}</td>
          <td>{{ row.subscribedDate }}</td>
          <td>{{ row.subscribedTime }}</td>
          <td>{{ row.url }}</td>
          <td>{{ row.status }}</td>
          <td>
            <a href="#">View</a>
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
      <DataTablePagination :currentPage="currentPage" :numPages="numPages" :pageSize="pageSize"
                           :total="layerSubscriptions.length" @setPage="setPage"/>
    </template>
  </data-table>
</template>
