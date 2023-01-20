<script lang="ts" setup>
  import { ref } from "vue";
  import { CatalogueTab, CatalogueView, NavigationEmits, SubmissionDetailViewTabs } from "../viewState.api";
  import { LayerSubmission } from "../../providers/layerSubmissionProvider.api";
  import SubmissionViewDetailTab from "./SubmissionViewDetailTab.vue";
  import SubmissionViewMapTab from "./SubmissionViewMapTab.vue";

  const props = defineProps<{
    layerSubmission?: LayerSubmission
  }>();

  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();
  const activeTab = ref<SubmissionDetailViewTabs>(SubmissionDetailViewTabs.Details);

  function onTabClick (tab: SubmissionDetailViewTabs) {
    activeTab.value = tab;
  }
</script>

<template>
  <nav class="nav nav-tabs">
    <a class="nav-link" :class="{ active: activeTab === SubmissionDetailViewTabs.Details }" aria-current="page" href="#"
       @click="onTabClick(SubmissionDetailViewTabs.Details)">
      Details
    </a>
    <a class="nav-link" :class="{ active: activeTab === SubmissionDetailViewTabs.Map}" aria-current="page"
       href="#" @click="onTabClick(SubmissionDetailViewTabs.Map)">
      Map
    </a>
    <button class="btn btn-outline-secondary mb-1 mt-1 ms-auto"
      @click="emit('navigate', CatalogueTab.LayerSubmissions, CatalogueView.List)">
      Back
    </button>
  </nav>
  <submission-view-detail-tab
    v-if="activeTab === SubmissionDetailViewTabs.Details && layerSubmission" :submission="layerSubmission"
    @navigate="(tab, view, options) => emit('navigate', tab, view, options)"/>
  <submission-view-map-tab v-if="activeTab === SubmissionDetailViewTabs.Map && layerSubmission"
                           :submission="layerSubmission"/>
</template>
