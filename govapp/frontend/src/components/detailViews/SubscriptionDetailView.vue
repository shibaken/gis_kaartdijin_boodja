<script lang="ts" setup>
  import { ref, watch } from "vue";
  import { CatalogueTab, CatalogueView, NavigationEmits, SubscriptionDetailViewTabs } from "../viewState.api";
  import { LayerSubscription } from "../../providers/layerSubscriptionProvider.api";
  import SubscriptionViewDetailTab from "./SubscriptionViewDetailTab.vue";

  const props = defineProps<{
    layerSubscription?: LayerSubscription,
    activeTab: SubscriptionDetailViewTabs
  }>();

  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();
  const activeTab = ref<SubscriptionDetailViewTabs>(SubscriptionDetailViewTabs.Details);
  watch(props, () => activeTab.value = props.activeTab);

  function onTabClick (tab: SubscriptionDetailViewTabs) {
    activeTab.value = tab;
  }
</script>

<template>
  <nav class="nav nav-tabs">
    <a class="nav-link" :class="{ active: activeTab === SubscriptionDetailViewTabs.Details }" aria-current="page" href="#"
       @click="onTabClick(SubscriptionDetailViewTabs.Details)">
      Details
    </a>
    <a class="nav-link" :class="{ active: activeTab === SubscriptionDetailViewTabs.RelatedItems}" aria-current="page"
       href="#" @click="onTabClick(SubscriptionDetailViewTabs.RelatedItems)">
      Attribute Table
    </a>
    <button class="btn btn-outline-secondary mb-1 mt-1 ms-auto"
      @click="emit('navigate', CatalogueTab.LayerSubscriptions, CatalogueView.List)">
      Back
    </button>
  </nav>
  <subscription-view-detail-tab v-if="layerSubscription" :subscription="layerSubscription"/>
</template>
