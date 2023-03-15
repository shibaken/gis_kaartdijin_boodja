<script lang="ts" setup>
  import DataTable from "./DataTable.vue";
  import CollapsibleRow from "./CollapsibleRow.vue";
  import DataTablePagination from "./DataTablePagination.vue";
  import { onMounted } from "vue";
  import { useLayerSubmissionStore } from "../../stores/LayerSubmissionStore";
  import { storeToRefs } from "pinia";
  import { DateTime } from "luxon";
  import { NavigationCatalogueEmits } from "../viewState.api";
  import { CatalogueTab, ViewMode } from "../viewState.api";
  import SortableHeader from "./SortableHeader.vue";
  import { useTableSortComposable } from "../../tools/sortComposable";
  import { RawLayerSubmissionFilter } from "../../backend/backend.api";

  // get Stores and fetch with `storeToRef` to
  const layerSubmissionStore = useLayerSubmissionStore();
  const { layerSubmissions, numPages, currentPage, filters, pageSize } = storeToRefs(layerSubmissionStore);
  const { getLayerSubmissions } = layerSubmissionStore;

  function setPage (pageNumber: number) {
    filters.value.pageNumber = pageNumber;
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationCatalogueEmits {}
  const emit = defineEmits<NavEmits>();

  const { sortDirection, onSort } = useTableSortComposable<RawLayerSubmissionFilter>(filters);

  onMounted(() => {
    getLayerSubmissions();
  });
</script>

<template>
  <data-table>
    <template #headers>
      <tr>
        <th></th>
        <SortableHeader name="Number" column="number" alt-field="id" :direction="sortDirection('id')" @sort="onSort"/>
        <SortableHeader name="Name" column="name" :direction="sortDirection('name')" @sort="onSort"/>
        <SortableHeader name="Submitted Date" column="submittedDate" :direction="sortDirection('submittedAt')"
                        alt-field="submittedAt" @sort="onSort"/>
        <SortableHeader name="Catalogue" column="catalogue" :direction="sortDirection('catalogue')"
                        alt-field="catalogue_entry__name" @sort="onSort"/>
        <SortableHeader name="Status" column="status" :direction="sortDirection('status')" @sort="onSort"/>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <CollapsibleRow v-for="(row, index) in layerSubmissions" :key="index" :id="index">
        <template #cells>
          <td>LM{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ DateTime.fromISO(row.submittedDate).toFormat('dd/MM/yyyy HH:mm')}}</td>
          <td>
            <a href="#" @click="emit('navigate', CatalogueTab.CatalogueEntries, ViewMode.View,
            { recordId: row.catalogueEntry?.id })">
              {{ row.catalogueEntry?.name }}
            </a>
          </td>
          <td>{{ row.status.label }}</td>
          <td>
            <a href="#" @click="emit('navigate', CatalogueTab.LayerSubmissions, ViewMode.View,
            { recordId: row.id })">
              View
            </a>
          </td>
        </template>
        <template #content>
          <td colspan="9">
            <span class="fw-bold small">Layer Submission description: </span> {{ row.description }}
          </td>
        </template>
      </CollapsibleRow>
    </template>
    <template #pagination>
      <DataTablePagination :current-page="currentPage" :num-pages="numPages" :page-size="pageSize"
                           :total="layerSubmissions.length" @setPage="setPage"/>
    </template>
  </data-table>
</template>
