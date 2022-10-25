import { defineStore } from "pinia";
import { computed, ComputedRef, Ref, ref, watch } from "vue";
import {LayerSubscription, LayerSubscriptionFilter} from "../providers/layerSubscriptionProvider.api";
import { PaginatedRecord } from "../backend/backend.api";
import { LayerSubscriptionProvider } from "../providers/layerSubscriptionProvider";


// Get the backend stub if the test flag is used.
const layerSubscriptionProvider: LayerSubscriptionProvider = new LayerSubscriptionProvider();

export const useLayerSubscriptionStore = defineStore('layerSubscription', () => {
  const layerSubscriptions: Ref<Array<LayerSubscription>> = ref([]);
  const currentPage: Ref<number> = ref(1);
  const pageSize: Ref<number> = ref(10);
  const total: Ref<number> = ref(0);
  const numPages: ComputedRef<number> = computed(() => Math.ceil(layerSubscriptions.value.length / pageSize.value));
  const filter: Ref<LayerSubscriptionFilter> = ref(new Map() as LayerSubscriptionFilter);

  watch(filter, () => getLayerSubscriptions());

  async function getLayerSubscriptions(): Promise<PaginatedRecord<LayerSubscription>> {
    const subscriptions = await layerSubscriptionProvider.fetchLayerSubscriptions(filter.value);
    layerSubscriptions.value = subscriptions.results;

    total.value = subscriptions.count;

    return subscriptions;
  }

  return { layerSubscriptions, currentPage, pageSize, numPages, filter, getLayerSubscriptions };
});
