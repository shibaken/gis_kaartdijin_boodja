import { defineStore } from "pinia";
import { Ref, ref, toRefs, watch } from "vue";
import { PublishEntryStatus, RecordStatus } from "../backend/backend.api";
import { useTableFilterComposable } from "../tools/filterComposable";
import { publisherProvider } from "../providers/publisherProvider";
import { RecordMeta } from "../providers/providerCommon.api";
import { PublishEntry, PublishEntryFilter } from "../providers/publisherProvider.api";
import { Workspace } from "../providers/catalogueEntryProvider.api";

export const usePublishEntryStore = defineStore("publishEntries", () => {
  const publishEntriesCache: Ref<PublishEntry[]> = ref([]);
  const publishEntries: Ref<PublishEntry[]> = ref([]);
  const publishEntryMeta: Ref<RecordMeta> = ref({ total: 0 });
  const workspaces: Ref<Workspace[]> = ref([]);
  const publishEntryStatuses: Ref<RecordStatus<PublishEntryStatus>[]> = ref([]);

  // Filters
  const tableFilterComposable = useTableFilterComposable<PublishEntryFilter>();
  const { filters } = toRefs(tableFilterComposable);
  const { setFilter, clearFilters } = tableFilterComposable;

  watch(filters.value, () => publisherProvider.fetchPublishEntries(filters.value));

  function updateEntry (patchedEntry: PublishEntry) {
    // Update entry and propagate changes
    if (publishEntries.value.find(entry => entry.id === patchedEntry.id)) {
      publishEntries.value = publishEntries.value
        .map((entry: PublishEntry) => entry.id === patchedEntry.id ? patchedEntry : entry);
    }
    // Update cache
    publishEntriesCache.value = publishEntriesCache.value
      .map((entry: PublishEntry) => entry.id === patchedEntry.id ? patchedEntry : entry);
  }

  return { publishEntries, publishEntryMeta, publishEntriesCache, filters, setFilter, clearFilters,
    workspaces, publishEntryStatuses, updateEntry };
});
