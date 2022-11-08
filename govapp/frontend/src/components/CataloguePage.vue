<script setup lang="ts">
  import { ref } from "vue";
  import LayerSubscriptionDataTable from "./dataTable/LayerSubscriptionDataTable.vue";
  import CatalogueEntryDataTable from "./dataTable/CatalogueEntryDataTable.vue";
  import CatalogueEntryFilter from "./widgets/CatalogueEntryFilter.vue";
  import LayerSubscriptionFilter from "./widgets/LayerSubscriptionFilter.vue";
  import LayerSubmissionDataTable from "./dataTable/LayerSubmissionDataTable.vue";
  import LayerSubmissionFilter from "./widgets/LayerSubmissionFilter.vue";
  import type { Ref } from "vue";

  type SelectedTab = "Catalogue Entries" | "Layer Submissions" | "Layer Subscriptions";

  const selectedTab: Ref<SelectedTab> = ref("Catalogue Entries");

  function setSelectedTab (tab: SelectedTab) {
    selectedTab.value = tab;
  }
</script>

<template>
  <ul class="nav nav-pills mb-4">
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
  <div class="card">
    <div class="card-header">
      <h4>{{ selectedTab }}</h4>
    </div>
    <div class="card-body">
      <div id="layerSubscriptionAccordion" class="accordion">
        <div class="accordion-item">
          <h2 id="headingFilter" class="accordion-header">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFilters" aria-expanded="true" aria-controls="collapseFilters">
              Filters
            </button>
          </h2>
          <div id="collapseFilters" class="accordion-collapse collapse show" aria-labelledby="headingFilter" data-bs-parent="#layerSubscriptionAccordion">
            <div class="accordion-body">
              <form class="form d-flex gap-3">
                <catalogue-entry-filter v-if="selectedTab === 'Catalogue Entries'"/>
                <layer-subscription-filter v-if="selectedTab === 'Layer Subscriptions'"/>
                <layer-submission-filter v-if="selectedTab === 'Layer Submissions'"/>
              </form>
            </div>
          </div>
        </div>
      </div>
      <catalogue-entry-data-table v-if='selectedTab === "Catalogue Entries"'/>
      <layer-subscription-data-table v-if='selectedTab === "Layer Subscriptions"'/>
      <layer-submission-data-table v-if='selectedTab === "Layer Submissions"'/>
    </div>
  </div>
</template>

<style lang="scss" scoped>
  #collapseFilters {
    .accordion-body {
      form {
        overflow-x: auto;
      }
    }
  }
</style>
