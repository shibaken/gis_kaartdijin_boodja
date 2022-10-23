import { defineStore } from "pinia";
import { Ref, ref, computed, ComputedRef, watch } from 'vue';
import { CatalogueEntry, CatalogueEntryFilter } from '../providers/catalogueEntryProvider.api';
import { CatalogueEntryProvider } from "../providers/catalogueEntryProvider";
import { PaginatedRecord } from "../backend/backend.api";

// Get the backend stub if the test flag is used.
const catalogueEntryProvider: CatalogueEntryProvider = new CatalogueEntryProvider();

export const useCatalogueEntryStore = defineStore('catalogueEntries', () => {
  const catalogueEntries: Ref<Array<CatalogueEntry>> = ref([]);
  const currentPage: Ref<number> = ref(1);
  const pageSize: Ref<number> = ref(10);
  const numPages: ComputedRef<number> = computed(() => Math.ceil(catalogueEntries.value.length / pageSize.value));
  const total: Ref<number> = ref(0);
  const filter: Ref<CatalogueEntryFilter> = ref(new Map() as CatalogueEntryFilter);

  watch(filter, () => getCatalogueEntries());

  async function getCatalogueEntries (): Promise<PaginatedRecord<CatalogueEntry>> {
    const entries = await catalogueEntryProvider.fetchCatalogueEntries(filter.value);
    catalogueEntries.value = entries.results
    total.value = entries.count;

    return entries;
  }

  return { catalogueEntries, currentPage, pageSize, numPages, filter, getCatalogueEntries };
});
