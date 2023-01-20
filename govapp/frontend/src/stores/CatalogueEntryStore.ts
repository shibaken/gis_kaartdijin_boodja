import { defineStore } from "pinia";
import { Ref, ref, toRefs, watch } from "vue";
import { CatalogueEntry, CatalogueEntryFilter } from "../providers/catalogueEntryProvider.api";
import { CatalogueEntryStatus, RecordStatus } from "../backend/backend.api";
import { useTableFilterComposable } from "../tools/filterComposable";
import { catalogueEntryProvider } from "../providers/catalogueEntryProvider";
import { RecordMeta } from "../providers/providerCommon.api";

export const useCatalogueEntryStore = defineStore("catalogueEntries", () => {
  // Status shouldn't need to change so pass it as a static list
  const entryStatuses = ref<RecordStatus<CatalogueEntryStatus>[]>([]);
  const catalogueEntries = ref<CatalogueEntry[]>([]);
  const catalogueEntryMeta: Ref<RecordMeta> = ref({ total: 0 });

  // Filters
  const tableFilterComposable = useTableFilterComposable<CatalogueEntryFilter>();
  const { filters } = toRefs(tableFilterComposable);
  const { setFilter, clearFilters } = tableFilterComposable;

  watch(filters.value, () => catalogueEntryProvider.fetchCatalogueEntries(filters.value));

  function updateEntry (patchedEntry: CatalogueEntry) {
    catalogueEntries.value = catalogueEntries.value
      .map((entry: CatalogueEntry) => entry.id === patchedEntry.id ? patchedEntry : entry);
  }

  return { catalogueEntries, catalogueEntryMeta, filters, setFilter,
    clearFilters, entryStatuses, updateEntry };
});
