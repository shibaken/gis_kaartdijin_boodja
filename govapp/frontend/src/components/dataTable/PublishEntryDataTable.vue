<script lang="ts" setup async>
  import DataTable from "./DataTable.vue";
  import CollapsibleRow from "./CollapsibleRow.vue";
  import { usePublishEntryStore } from "../../stores/PublishEntryStore";
  import { storeToRefs } from "pinia";
  import { onMounted } from "vue";
  import { DateTime } from "luxon";
  import { ViewMode, PublishTab, NavigationPublishEmits } from "../viewState.api";
  import SortableHeader from "./SortableHeader.vue";
  import { useTableSortComposable } from "../../tools/sortComposable";
  import { RawPublishEntryFilter } from "../../backend/backend.api";
  import { publisherProvider } from "../../providers/publisherProvider";
  import { usePermissionsComposable } from "../../tools/permissionsComposable";
  import { PermissionsComposable } from "../../tools/permissionsComposable.api";

  const props = withDefaults(defineProps<{
      view: ViewMode
    }>(),
    {
      view: ViewMode.View
    });

  // get Stores and fetch with `storeToRef`
  const publishEntryStore = usePublishEntryStore();
  const { publishEntries, filters, publishEntryMeta } = storeToRefs(publishEntryStore);
  const permissionsComposable: PermissionsComposable = usePermissionsComposable();

  /**
   * Workaround for external typing. See https://vuejs.org/api/sfc-script-setup.html#type-only-props-emit-declarations
   */
  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationPublishEmits {}
  const emit = defineEmits<NavEmits>();

  function setPage (pageNumber: number) {
    filters.value.pageNumber = pageNumber;
  }

  function setPageSize (size: number) {
    filters.value.limit = size;
  }

  const { sortDirection, onSort } = useTableSortComposable<RawPublishEntryFilter>(filters);

  onMounted(() => {
    filters.value.limit = 10;
    publisherProvider.fetchPublishEntries(filters.value);
  });
</script>

<template>
  <data-table :total="publishEntryMeta.total" @set-page="setPage" @set-page-size="setPageSize">
    <template #headers>
      <tr>
        <th></th>
        <SortableHeader name="Number" column="number" alt-field="id" :direction="sortDirection('id')" @sort="onSort"/>
        <SortableHeader name="Name" column="name" :direction="sortDirection('name')" @sort="onSort"/>
        <SortableHeader name="Status" column="status" :direction="sortDirection('status')" @sort="onSort"/>
        <SortableHeader name="Last Updated" column="updatedAt" :direction="sortDirection('updatedAt')" @sort="onSort"/>
        <SortableHeader name="Assigned To" column="assignedTo" :direction="sortDirection('assignedTo')" @sort="onSort"/>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <CollapsibleRow v-for="(row, index) in publishEntries" :id="index" :key="index">
        <template #cells>
          <td>CE{{ row.id }}</td>
          <td>{{ row.name }}</td>
          <td>{{ row.status.label }}</td>
          <td>{{ DateTime.fromISO(row.updatedAt).toFormat('dd/MM/yyyy HH:mm')}}</td>
          <td>{{ row.assignedTo?.username }}</td>
          <td>
            <a href="#" class="me-2"
               @click="emit('navigate', PublishTab.PublishEntries, ViewMode.View, { recordId: row.id })">
              {{ permissionsComposable.isEntryEditor(row) ? "Edit" : "View" }}
            </a>
          </td>
        </template>
        <template #content>
          <td colspan="9">
            <span class="fw-bold small">Publish layer description: </span>{{ row.description }}
          </td>
        </template>
      </CollapsibleRow>
    </template>
  </data-table>
</template>
