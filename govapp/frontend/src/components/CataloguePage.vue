<script setup lang="ts">
  import { ref } from 'vue';
  import LayerSubscriptionDataTable from './dataTable/LayerSubscriptionDataTable.vue';
  import CatalogueEntryDataTable from './dataTable/CatalogueEntryDataTable.vue';
  import CatalogueEntryFilter from './widgets/CatalogueEntryFilter.vue';
  import LayerSubscriptionFilter from './widgets/LayerSubscriptionFilter.vue';
  import type { Ref } from 'vue';

  type SelectedTab = 'catalogueEntries'|'layerSubmissions'|'layerSubscriptions';

  const selectedTab: Ref<SelectedTab> = ref('catalogueEntries');

  function setSelectedTab (tab: SelectedTab) {
    selectedTab.value = tab;
  }
</script>

<template>
  <ul class="nav nav-pills mb-4">
    <li class="nav-item">
      <button class="nav-link" aria-current="page" href="#" :class='{ active: selectedTab === "catalogueEntries" }'
              @click='setSelectedTab("catalogueEntries")'>Catalogue Entries</button>
    </li>
    <li class="nav-item">
      <button class="nav-link" href="#" :class='{ active: selectedTab === "layerSubmissions" }'
              @click='setSelectedTab("layerSubmissions")'>Layer Submissions</button>
    </li>
    <li class="nav-item">
      <button class="nav-link" href="#" :class='{ active: selectedTab === "layerSubscriptions" }'
              @click='setSelectedTab("layerSubscriptions")'>Layer Subscriptions</button>
    </li>
  </ul>
  <div class="card">
    <div class="card-header">
      <h4>Layer Subscriptions</h4>
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
                <CatalogueEntryFilter v-if="selectedTab === 'catalogueEntries'"/>
                <LayerSubscriptionFilter v-if="selectedTab === 'layerSubscriptions'"/>
              </form>
            </div>
          </div>
        </div>
      </div>
      <catalogue-entry-data-table v-if='selectedTab === "catalogueEntries"'/>
      <layer-subscription-data-table v-if='selectedTab === "layerSubscriptions"'/>
    </div>
  </div>
</template>

<style lang="scss" scoped>
  #layerSubscriptionAccordion {
    .accordion-item {
      .accordion-body .form-floating {
        select, input {
          min-width: 15rem;
        }
      }
    }
  }
</style>
