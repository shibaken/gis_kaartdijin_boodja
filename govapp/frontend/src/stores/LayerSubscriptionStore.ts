import { defineStore } from "pinia";
import { computed, ComputedRef, Ref, ref, toRefs, watch } from "vue";
import { LayerSubscription, LayerSubscriptionFilter } from "../providers/layerSubscriptionProvider.api";
import { LayerSubscriptionStatus, PaginatedRecord, RecordStatus } from "../backend/backend.api";
import { layerSubscriptionProvider } from "../providers/layerSubscriptionProvider";
import { useTableFilterComposable } from "../tools/filterComposable";
import { statusProvider } from "../providers/statusProvider";
import { Filter } from "../tools/filterComposable.api";

export type LayerSubscriptionStore = {
  numPages: ComputedRef<number>,
  getLayerSubscriptions: () => Promise<PaginatedRecord<LayerSubscription>>,
  layerSubscriptions: Ref<Array<LayerSubscription>>,
  pageSize: Ref<number>,
  filters: Ref<LayerSubscriptionFilter>,
  clearFilters: () => void,
  currentPage: Ref<number>,
  subscriptionStatuses: Promise<Array<RecordStatus<LayerSubscriptionStatus>>>,
  setFilter: ({field, value}: Filter<LayerSubscriptionFilter>) => void
}

// Status shouldn't need to change so pass it as a static list
export const subscriptionStatuses = statusProvider.fetchStatuses<LayerSubscriptionStatus>("catalogue/layers/subscriptions");

export const useLayerSubscriptionStore = defineStore("layerSubscription", () => {
  const layerSubscriptions: Ref<Array<LayerSubscription>> = ref([]);
  const currentPage: Ref<number> = ref(1);
  const pageSize: Ref<number> = ref(10);
  const total: Ref<number> = ref(0);
  const numPages: ComputedRef<number> = computed(() => Math.ceil(layerSubscriptions.value.length / pageSize.value));

  // Filters
  const tableFilterComposable = useTableFilterComposable<LayerSubscriptionFilter>();
  const { filters } = toRefs(tableFilterComposable);
  const { setFilter, clearFilters } = tableFilterComposable;

  watch(filters.value, () => getLayerSubscriptions());

  async function getLayerSubscriptions (): Promise<PaginatedRecord<LayerSubscription>> {
    const subscriptions = await layerSubscriptionProvider.fetchLayerSubscriptions(filters.value);
    layerSubscriptions.value = subscriptions.results;

    total.value = subscriptions.count;

    return subscriptions;
  }

  return { layerSubscriptions, currentPage, pageSize, numPages, filters, setFilter, clearFilters, subscriptionStatuses,
    getLayerSubscriptions };
});
