import { defineStore } from "pinia";
import { Ref, ref, computed, ComputedRef, watch, toRefs } from "vue";
import { CatalogueEntry, CatalogueEntryFilter } from "../providers/catalogueEntryProvider.api";
import { CatalogueEntryProvider } from "../providers/catalogueEntryProvider";
import { StatusProvider } from "../providers/statusProvider";
import { CatalogueEntryStatus, PaginatedRecord } from "../backend/backend.api";
import { useTableFilterComposable } from "../tools/filterComposable";

// Get the backend stub if the test flag is used.
const catalogueEntryProvider: CatalogueEntryProvider = new CatalogueEntryProvider();
const statusProvider = new StatusProvider();

// Status shouldn't need to change so pass it as a static list
export const entryStatuses = statusProvider.fetchStatuses<CatalogueEntryStatus>("entries");

export const useCatalogueEntryStore = defineStore("catalogueEntries", () => {
  const catalogueEntries: Ref<Array<CatalogueEntry>> = ref([]);
  const currentPage: Ref<number> = ref(1);
  const pageSize: Ref<number> = ref(10);
  const numPages: ComputedRef<number> = computed(() => Math.ceil(catalogueEntries.value.length / pageSize.value));
  const total: Ref<number> = ref(0);

  // Filters
  const tableFilterComposable = useTableFilterComposable<CatalogueEntryFilter>();
  const { filters } = toRefs(tableFilterComposable);
  const { setFilter, clearFilter } = tableFilterComposable;

  watch(filters.value, () => getCatalogueEntries());

  async function getCatalogueEntries (): Promise<PaginatedRecord<CatalogueEntry>> {
    const entries = await catalogueEntryProvider.fetchCatalogueEntries(filters.value);
    catalogueEntries.value = entries.results;
    total.value = entries.count;

    return entries;
  }

  async function getOrFetch(id: number): Promise<CatalogueEntry> {
    const storeMatch = catalogueEntries.value.find(entry => entry.id === id);
    return !!storeMatch ? Promise.resolve(storeMatch) : catalogueEntryProvider.fetchCatalogueEntry(id);
  }

  return { catalogueEntries, currentPage, pageSize, numPages, filters, setFilter, clearFilter, entryStatuses,
    getCatalogueEntries, getOrFetch };
});
