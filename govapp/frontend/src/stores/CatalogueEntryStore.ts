import { defineStore } from "pinia";
import { Ref, ref, computed, ComputedRef, toRefs } from "vue";
import { CatalogueEntry, CatalogueEntryFilter } from "../providers/catalogueEntryProvider.api";
import { CatalogueEntryStatus, RecordStatus } from "../backend/backend.api";
import { useTableFilterComposable } from "../tools/filterComposable";


export const useCatalogueEntryStore = defineStore("catalogueEntries", () => {
// Status shouldn't need to change so pass it as a static list
  const entryStatuses = ref<RecordStatus<CatalogueEntryStatus>[]>([]);
  const catalogueEntries = ref<CatalogueEntry[]>([]);
  const currentPage: Ref<number> = ref(1);
  const pageSize: Ref<number> = ref(10);
  const numPages: ComputedRef<number> = computed(() => Math.ceil(catalogueEntries.value.length / pageSize.value));
  const total: Ref<number> = ref(0);

  // Filters
  const tableFilterComposable = useTableFilterComposable<CatalogueEntryFilter>();
  const { filters } = toRefs(tableFilterComposable);
  const { setFilter, clearFilters } = tableFilterComposable;

  function updateEntry (patchedEntry: CatalogueEntry) {
    catalogueEntries.value = catalogueEntries.value
      .map((entry: CatalogueEntry) => entry.id === patchedEntry.id ? patchedEntry : entry);
  }

  return { catalogueEntries, currentPage, pageSize, numPages, total, filters, setFilter, clearFilters, entryStatuses,
    updateEntry };
});
