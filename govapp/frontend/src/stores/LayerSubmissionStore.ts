import { defineStore } from "pinia";
import { computed, ComputedRef, Ref, ref, toRefs, watch } from "vue";
import { LayerSubmission, LayerSubmissionFilter } from "../providers/layerSubmissionProvider.api";
import { LayerSubmissionStatus, PaginatedRecord, RecordStatus } from "../backend/backend.api";
import { layerSubmissionProvider } from "../providers/layerSubmissionProvider";
import { useTableFilterComposable } from "../tools/filterComposable";
import { statusProvider } from "../providers/statusProvider";
import { Filter } from "../tools/filterComposable.api";

export type LayerSubmissionStore = {
  numPages: ComputedRef<number>,
  pageSize: Ref<number>,
  filters: Ref<LayerSubmissionFilter>,
  clearFilters: () => void,
  currentPage: Ref<number>,
  submissionStatuses: Promise<Array<RecordStatus<LayerSubmissionStatus>>>,
  getLayerSubmissions: () => Promise<PaginatedRecord<LayerSubmission>>,
  layerSubmissions: Ref<Array<LayerSubmission>>,
  setFilter: ({field, value}: Filter<LayerSubmissionFilter>) => void
}

// Status shouldn't need to change so pass it as a static list
export const submissionStatuses = statusProvider.fetchStatuses<LayerSubmissionStatus>("catalogue/layers/submissions");

export const useLayerSubmissionStore = defineStore("layerSubmission", () => {
  const layerSubmissions: Ref<Array<LayerSubmission>> = ref([]);
  const currentPage: Ref<number> = ref(1);
  const pageSize: Ref<number> = ref(10);
  const total: Ref<number> = ref(0);
  const numPages: ComputedRef<number> = computed(() => Math.ceil(layerSubmissions.value.length / pageSize.value));

  // Filters
  const tableFilterComposable = useTableFilterComposable<LayerSubmissionFilter>();
  const { filters } = toRefs(tableFilterComposable);
  const { setFilter, clearFilters } = tableFilterComposable;

  watch(filters.value, () => getLayerSubmissions());

  async function getLayerSubmissions (): Promise<PaginatedRecord<LayerSubmission>> {
    const submissions = await layerSubmissionProvider.fetchLayerSubmissions(filters.value);
    layerSubmissions.value = submissions.results;

    total.value = submissions.count;

    return submissions;
  }

  return { layerSubmissions, currentPage, pageSize, numPages, filters, setFilter, clearFilters, submissionStatuses,
    getLayerSubmissions };
});
