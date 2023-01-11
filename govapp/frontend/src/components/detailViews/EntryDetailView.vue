<script lang="ts" setup>
  import { ref } from "vue";
  import { CatalogueTab, CatalogueView, CatalogueDetailViewTabs, NavigationEmits } from "../viewState.api";
  import type { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import EntryViewDetailTab from "./EntryViewDetailTab.vue";
  import EntryViewAttributeTab from "./EntryViewAttributeTab.vue";

  const props = defineProps<{
    catalogueEntry?: CatalogueEntry
  }>();

  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();
  const activeTab = ref<CatalogueDetailViewTabs>(CatalogueDetailViewTabs.Details);

  function onTabClick (tab: CatalogueDetailViewTabs) {
    activeTab.value = tab;
  }
</script>

<template>
  <nav class="nav nav-tabs">
    <a class="nav-link" :class="{ active: activeTab === CatalogueDetailViewTabs.Details }" aria-current="page" href="#"
       @click="onTabClick(CatalogueDetailViewTabs.Details)">
      Details
    </a>
    <a class="nav-link" :class="{ active: activeTab === CatalogueDetailViewTabs.AttributeTable}" aria-current="page"
       href="#" @click="onTabClick(CatalogueDetailViewTabs.AttributeTable)">
      Attribute Table
    </a>
    <a class="nav-link" :class="{ active: activeTab === CatalogueDetailViewTabs.Symbology}" aria-current="page" href="#"
       @click="onTabClick(CatalogueDetailViewTabs.Symbology)">
      Symbology
    </a>
    <a class="nav-link" :class="{ active: activeTab === CatalogueDetailViewTabs.Metadata}" aria-current="page" href="#"
       @click="onTabClick(CatalogueDetailViewTabs.Metadata)">
      Metadata
    </a>
    <button class="btn btn-outline-secondary mb-1 mt-1 ms-auto"
            @click="emit('navigate', CatalogueTab.CatalogueEntries, CatalogueView.List)">
      Back
    </button>
  </nav>
  <entry-view-detail-tab v-if="activeTab === CatalogueDetailViewTabs.Details && catalogueEntry"
                         :entry="catalogueEntry"/>
  <entry-view-attribute-tab v-if="activeTab === CatalogueDetailViewTabs.AttributeTable && catalogueEntry"
                            :entry="catalogueEntry"/>
</template>
