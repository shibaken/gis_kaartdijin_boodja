<script setup lang="ts">
  import { ref } from "vue";
  import LayerSubscriptionDataTable from "./dataTable/LayerSubscriptionDataTable.vue";
  import CatalogueEntryDataTable from "./dataTable/CatalogueEntryDataTable.vue";
  import CatalogueEntryFilter from "./widgets/CatalogueEntryFilter.vue";
  import LayerSubscriptionFilter from "./widgets/LayerSubscriptionFilter.vue";
  import LayerSubmissionDataTable from "./dataTable/LayerSubmissionDataTable.vue";
  import LayerSubmissionFilter from "./widgets/LayerSubmissionFilter.vue";
  import CatalogueEntryDetails from "./detailViews/CatalogueEntryDetailView.vue";
  import { CatalogueTab, CatalogueView, NavigateEmitsOptions } from "./viewState.api";
  import Card from "./widgets/Card.vue";
  import Accordion from "./widgets/Accordion.vue";
  import SideBarLeft from "./SideBarLeft.vue";
  import { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
  import { LayerSubscription } from "../providers/layerSubscriptionProvider.api";
  import { LayerSubmission } from "../providers/layerSubmissionProvider.api";
  import { CatalogueEntryProvider } from "../providers/catalogueEntryProvider";
  import { LayerSubmissionProvider } from "../providers/layerSubmissionProvider";
  import { LayerSubscriptionProvider } from "../providers/layerSubscriptionProvider";

  const catalogueEntryProvider = new CatalogueEntryProvider();
  const layerSubscriptionProvider = new LayerSubscriptionProvider();
  const layerSubmissionProvider = new LayerSubmissionProvider();

  const selectedTab = ref<CatalogueTab>(CatalogueTab.CatalogueEntries);
  const selectedView = ref<CatalogueView>(CatalogueView.List);
  const selectedViewEntry = ref<CatalogueEntry | undefined>();
  const selectedViewSubmission = ref<LayerSubmission | undefined>();
  const selectedViewSubscription = ref<LayerSubscription | undefined>();

  async function navigate (tab: CatalogueTab, view: CatalogueView, options?: NavigateEmitsOptions) {
    selectedView.value = view;
    selectedViewEntry.value = undefined;
    selectedViewSubmission.value = undefined;
    selectedViewSubscription.value = undefined;

    selectedTab.value = tab;
    selectedView.value = view;

    if (typeof options?.recordId !== "number") {
      return;
    } else if (tab === CatalogueTab.CatalogueEntries) {
      selectedViewEntry.value = await catalogueEntryProvider.fetchCatalogueEntry(options.recordId);
    } else if (tab === CatalogueTab.LayerSubscriptions) {
      selectedViewSubscription.value = await layerSubscriptionProvider.fetchLayerSubscription(options.recordId);
    } else if (tab === CatalogueTab.LayerSubmissions) {
      selectedViewSubmission.value = await layerSubmissionProvider.fetchLayerSubmission(options.recordId);
    } else {
      console.warn("Selected view record was not a recognised type");
    }
  }
</script>

<template>
  <ul class="nav nav-pills mb-4" v-if="selectedView === CatalogueView.List">
    <li class="nav-item">
      <button class="nav-link" aria-current="page" href="#" :class='{ active: selectedTab === "Catalogue Entries" }'
              @click='navigate(CatalogueTab.CatalogueEntries, CatalogueView.List)'>Catalogue Entries</button>
    </li>
    <li class="nav-item">
      <button class="nav-link" href="#" :class='{ active: selectedTab === "Layer Submissions" }'
              @click='navigate(CatalogueTab.LayerSubmissions, CatalogueView.List)'>Layer Submissions</button>
    </li>
    <li class="nav-item">
      <button class="nav-link" href="#" :class='{ active: selectedTab === "Layer Subscriptions" }'
              @click='navigate(CatalogueTab.LayerSubscriptions, CatalogueView.List)'>Layer Subscriptions</button>
    </li>
  </ul>

  <div class="d-flex flex-row">
    <div id="side-bar-wrapper" v-if="selectedView === CatalogueView.View">
      <side-bar-left/>
    </div>
    <div class="w-100">
      <card v-if="selectedView === CatalogueView.List">
        <template #header>
          <h4>{{ selectedTab }}</h4>
        </template>
        <template #body>
          <accordion id-prefix="filter" header-text="Filters">
            <template #body>
              <form class="form d-flex gap-3">
                <catalogue-entry-filter v-if="selectedTab === 'Catalogue Entries'"/>
                <layer-subscription-filter v-if="selectedTab === 'Layer Subscriptions'"/>
                <layer-submission-filter v-if="selectedTab === 'Layer Submissions'"/>
              </form>

              <catalogue-entry-data-table v-if='selectedTab === "Catalogue Entries"'
                @navigate="navigate"/>
              <layer-subscription-data-table v-if='selectedTab === "Layer Subscriptions"'
                @navigate="navigate"/>
              <layer-submission-data-table v-if='selectedTab === "Layer Submissions"'
                @navigate="navigate"/>
            </template>
          </accordion>
        </template>
      </card>
      <catalogue-entry-details v-if="selectedView === CatalogueView.View" :catalogue-entry="selectedViewEntry"
      @navigate="navigate"/>
    </div>
  </div>
</template>

<style lang="scss">
  .accordion-collapse {
    .accordion-body {
      form {
        overflow-x: auto;
      }
    }
  }

  #side-bar-wrapper {
    width: 24rem;
  }
</style>
