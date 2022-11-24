<script setup lang="ts">
  import { ref } from "vue";
  import LayerSubscriptionDataTable from "./dataTable/LayerSubscriptionDataTable.vue";
  import CatalogueEntryDataTable from "./dataTable/CatalogueEntryDataTable.vue";
  import CatalogueEntryFilter from "./widgets/CatalogueEntryFilter.vue";
  import LayerSubscriptionFilter from "./widgets/LayerSubscriptionFilter.vue";
  import LayerSubmissionDataTable from "./dataTable/LayerSubmissionDataTable.vue";
  import LayerSubmissionFilter from "./widgets/LayerSubmissionFilter.vue";
  import CatalogueEntryDetails from "./detailViews/CatalogueEntryDetailView.vue";
  import { CatalogueTab, CatalogueView } from "./viewState.api";
  import Card from "./widgets/Card.vue";
  import Accordion from "./widgets/Accordion.vue";
  import SideBarLeft from "./SideBarLeft.vue";
  import { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
  import { LayerSubscription } from "../providers/layerSubscriptionProvider.api";
  import { LayerSubmission } from "../providers/layerSubmissionProvider.api";

  const selectedTab = ref<CatalogueTab>("Catalogue Entries");
  const selectedView = ref<CatalogueView>("list");
  const selectedViewEntry = ref<CatalogueEntry | undefined>();
  const selectedViewSubmission = ref<LayerSubmission | undefined>();
  const selectedViewSubscription = ref<LayerSubscription | undefined>();

  function setSelectedTab (tab: CatalogueTab) {
    selectedTab.value = tab;
  }

  enum RecordType {
    CatalogueEntry,
    LayerSubscription,
    LayerSubmission
  }
  function setSelectedView<T> (view: CatalogueView, record: T, recordType: RecordType) {
    selectedView.value = view;
    selectedViewEntry.value = undefined;
    selectedViewSubmission.value = undefined;
    selectedViewSubscription.value = undefined;

    if (recordType === RecordType.CatalogueEntry) {
      selectedViewEntry.value = record as CatalogueEntry;
    } else if (recordType === RecordType.LayerSubscription) {
      selectedViewSubscription.value = record as LayerSubscription;
    } else if (recordType === RecordType.LayerSubmission) {
      selectedViewSubmission.value = record as LayerSubmission;
    } else if (!!record || !!recordType) {
      console.error("Selected view record was not a recognised type");
    }
  }
</script>

<template>
  <ul class="nav nav-pills mb-4" v-if="selectedView === 'list'">
    <li class="nav-item">
      <button class="nav-link" aria-current="page" href="#" :class='{ active: selectedTab === "Catalogue Entries" }'
              @click='setSelectedTab("Catalogue Entries")'>Catalogue Entries</button>
    </li>
    <li class="nav-item">
      <button class="nav-link" href="#" :class='{ active: selectedTab === "Layer Submissions" }'
              @click='setSelectedTab("Layer Submissions")'>Layer Submissions</button>
    </li>
    <li class="nav-item">
      <button class="nav-link" href="#" :class='{ active: selectedTab === "Layer Subscriptions" }'
              @click='setSelectedTab("Layer Subscriptions")'>Layer Subscriptions</button>
    </li>
  </ul>

  <div class="d-flex flex-row">
    <div id="side-bar-wrapper" v-if="selectedView === 'view'">
      <side-bar-left/>
    </div>
    <div class="w-100">
      <card v-if="selectedView === 'list'">
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
                @show-view="(view: CatalogueView, record: CatalogueEntry) => setSelectedView<CatalogueEntry>(view, record, RecordType.CatalogueEntry)"/>
              <layer-subscription-data-table v-if='selectedTab === "Layer Subscriptions"'
                @show-view="(view: CatalogueView, record: LayerSubmission) => setSelectedView<LayerSubmission>(view, record, RecordType.LayerSubscription)"/>
              <layer-submission-data-table v-if='selectedTab === "Layer Submissions"'
                @show-view="(view: CatalogueView, record: LayerSubscription) => setSelectedView<LayerSubscription>(view, record, selectedViewSubmission, RecordType.LayerSubmission)"/>
            </template>
          </accordion>
        </template>
      </card>
      <catalogue-entry-details v-if="selectedView === 'view'" :catalogue-entry="selectedViewEntry"
                               @exit-details="setSelectedView('list', undefined, undefined)"/>
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
