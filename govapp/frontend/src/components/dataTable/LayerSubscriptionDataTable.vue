<script lang="ts" setup>
  import DataTable from "./DataTable.vue";
  import PlusCircleFill from "../icons/plusCircleFill.vue";
  import CollapsibleRow from "./CollapsibleRow.vue";
  import DataTablePagination from "./DataTablePagination.vue";
  import { onMounted } from "vue";
  import { useLayerSubscriptionStore } from "../../stores/LayerSubscriptionStore";
  import { storeToRefs } from "pinia";
  import { DateTime } from "luxon";
  import { useTableSortComposable } from "../../tools/sortComposable";
  import { RawCatalogueEntryFilter } from "../../backend/backend.api";
  import SortableHeader from "./SortableHeader.vue";
  import { CatalogueTab, CatalogueView, NavigationEmits } from "../viewState.api";

  // get Stores and fetch with `storeToRef` to
  const layerSubscriptionStore = useLayerSubscriptionStore();
  const { layerSubscriptions, numPages, currentPage, filters, pageSize } = storeToRefs(layerSubscriptionStore);
  const { getLayerSubscriptions } = layerSubscriptionStore;

  /**
   * Workaround for external typing. See https://vuejs.org/api/sfc-script-setup.html#type-only-props-emit-declarations
   */
    // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();

  function setPage (pageNumber: number) {
    filters.value.pageNumber = pageNumber;
  }

  const { sortDirection, onSort } = useTableSortComposable<RawCatalogueEntryFilter>(filters);

  onMounted(() => {
    getLayerSubscriptions();
  });
</script>

<template>
  <data-table>
    <template #headers>
      <tr>
        <th></th>
        <SortableHeader name="Number" column="number" alt-field="id" :direction="sortDirection('id')" @sort="onSort"/>
        <SortableHeader name="Name" column="name" :direction="sortDirection('name')" @sort="onSort"/>
        <SortableHeader name="Subscribed Date" column="subscribedDate" :direction="sortDirection('subscribedDate')" @sort="onSort"/>
        <th>Time</th>
        <SortableHeader name="Webservice Url" column="url" :direction="sortDirection('url')" @sort="onSort"/>
        <SortableHeader name="Status" column="status" :direction="sortDirection('status')" @sort="onSort"/>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <CollapsibleRow v-for="(row, index) in layerSubscriptions" :key="index" :id="index">
        <template #cells>
          <td>LS{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ DateTime.fromISO(row.subscribedDate).toFormat('dd/MM/yyyy')}}</td>
          <td>{{ DateTime.fromISO(row.subscribedDate).toFormat('HH:mm') }}</td>
          <td><a :href="row.url">{{ row.url }}</a></td>
          <td>{{ row.status.label }}</td>
          <td>
            <a href="#" class="me-2"
               @click="emit('navigate', CatalogueTab.LayerSubscriptions, CatalogueView.View, { recordId: row.id })">View</a>
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
