import { defineStore } from "pinia";
import { Ref, ref, toRefs, watch } from "vue";
import { CatalogueEntry, CatalogueEntryFilter, Workspace } from "../providers/catalogueEntryProvider.api";
import { CatalogueEntryStatus, RecordStatus } from "../backend/backend.api";
import { useTableFilterComposable } from "../tools/filterComposable";
import { catalogueEntryProvider } from "../providers/catalogueEntryProvider";
import { RecordMeta } from "../providers/providerCommon.api";
import { Metadata } from "../providers/relatedEntityProvider.api";

export const useCatalogueEntryStore = defineStore("catalogueEntries", () => {
  // Status shouldn't need to change so pass it as a static list
  const entryStatuses = ref<RecordStatus<CatalogueEntryStatus>[]>([]);
  const catalogueEntries = ref<CatalogueEntry[]>([]);
  const catalogueEntriesCache = ref<CatalogueEntry[]>([]);
  const catalogueEntryMeta: Ref<RecordMeta> = ref({ total: 0 });
  const workspaces: Ref<Workspace[]> = ref([]);
  const metadataList: Ref<Metadata[]> = ref([]);

  // Filters
  const tableFilterComposable = useTableFilterComposable<CatalogueEntryFilter>();
  const { filters } = toRefs(tableFilterComposable);
  const { setFilter, clearFilters } = tableFilterComposable;

  watch(filters.value, () => catalogueEntryProvider.fetchCatalogueEntries(filters.value));

  function updateEntry (patchedEntry: CatalogueEntry) {
    if (catalogueEntries.value.find(entry => entry.id === patchedEntry.id)) {
      catalogueEntries.value = catalogueEntries.value
        .map((entry: CatalogueEntry) => entry.id === patchedEntry.id ? patchedEntry : entry);
    }
    catalogueEntriesCache.value = catalogueEntriesCache.value
      .map((entry: CatalogueEntry) => entry.id === patchedEntry.id ? patchedEntry : entry);
  }

  return { catalogueEntries, catalogueEntryMeta, catalogueEntriesCache, filters, setFilter, clearFilters, entryStatuses,
    workspaces, metadataList, updateEntry };
});
