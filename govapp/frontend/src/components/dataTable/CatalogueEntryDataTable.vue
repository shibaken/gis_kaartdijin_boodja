<script lang="ts" setup async>
  import DataTable from "./DataTable.vue";
  import CollapsibleRow from "./CollapsibleRow.vue";
  import { useCatalogueEntryStore } from "../../stores/CatalogueEntryStore";
  import { storeToRefs } from "pinia";
  import { onMounted } from "vue";
  import { DateTime } from "luxon";
  import { CatalogueTab, ViewMode, NavigationCatalogueEmits } from "../viewState.api";
  import SortableHeader from "./SortableHeader.vue";
  import { useTableSortComposable } from "../../tools/sortComposable";
  import { RawCatalogueEntryFilter } from "../../backend/backend.api";
  import { catalogueEntryProvider } from "../../providers/catalogueEntryProvider";
  import { usePermissionsComposable } from "../../tools/permissionsComposable";
  import { PermissionsComposable } from "../../tools/permissionsComposable.api";

  const props = withDefaults(defineProps<{
      view: ViewMode
    }>(),
    {
      view: ViewMode.View
    });

  // get Stores and fetch with `storeToRef`
  const catalogueEntryStore = useCatalogueEntryStore();
  const { catalogueEntries, filters, catalogueEntryMeta } = storeToRefs(catalogueEntryStore);
  const permissionsComposable: PermissionsComposable = usePermissionsComposable();

  /**
   * Workaround for external typing. See https://vuejs.org/api/sfc-script-setup.html#type-only-props-emit-declarations
   */
  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationCatalogueEmits {}
  const emit = defineEmits<NavEmits>();

  function setPage (pageNumber: number) {
    filters.value.pageNumber = pageNumber;
  }

  function setPageSize (size: number) {
    filters.value.limit = size;
  }

  const { sortDirection, onSort } = useTableSortComposable<RawCatalogueEntryFilter>(filters);

  onMounted(() => {
    filters.value.limit = 10;
    catalogueEntryProvider.fetchCatalogueEntries(filters.value);
  });
</script>

<template>
  <data-table :total="catalogueEntryMeta.total" @set-page="setPage" @set-page-size="setPageSize">
    <template #headers>
      <tr>
        <th></th>
        <SortableHeader name="Number" column="number" alt-field="id" :direction="sortDirection('id')" @sort="onSort"/>
        <SortableHeader name="Name" column="name" :direction="sortDirection('name')" @sort="onSort"/>
        <SortableHeader name="Custodian" column="custodian" :direction="sortDirection('custodian')" @sort="onSort"/>
        <SortableHeader name="Status" column="status" :direction="sortDirection('status')" @sort="onSort"/>
        <SortableHeader name="Last Updated" column="updatedAt" :direction="sortDirection('updatedAt')" @sort="onSort"/>
        <SortableHeader name="Assigned To" column="assignedTo" :direction="sortDirection('assignedTo')" @sort="onSort"/>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <CollapsibleRow v-for="(row, index) in catalogueEntries" :id="index" :key="index">
        <template #cells>
          <td>CE{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ row.custodian?.name }}</td>
          <td>{{ row.status.label }}</td>
          <td>{{ DateTime.fromISO(row.updatedAt).toFormat('dd/MM/yyyy HH:mm')}}</td>
          <td>{{ row.assignedTo?.username }}</td>
          <td>
            <a href="#" class="me-2"
               @click="emit('navigate', CatalogueTab.CatalogueEntries, ViewMode.View, { recordId: row.id })">
              {{ permissionsComposable.isEntryEditor(row) ? "Edit" : "View" }}
            </a>
          </td>
        </template>
        <template #content>
          <td colspan="9">
            <span class="fw-bold small">Catalogue layer description: </span>{{ row.description }}
          </td>
        </template>
      </CollapsibleRow>
    </template>
  </data-table>
</template>
