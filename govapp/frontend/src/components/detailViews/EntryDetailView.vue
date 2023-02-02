<script lang="ts" setup>
  import { ref, watch } from "vue";
  import { CatalogueDetailViewTabs, CatalogueTab, CatalogueView, NavigationEmits } from "../viewState.api";
  import type { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import EntryViewDetailTab from "./EntryViewDetailTab.vue";
  import EntryViewAttributeTab from "./EntryViewAttributeTab.vue";
  import EntryViewSymbologyTab from "./EntryViewSymbologyTab.vue";
  import EntryViewMetadataTab from "./EntryViewMetadataTab.vue";

  const props = defineProps<{
    catalogueEntry?: CatalogueEntry,
    activeTab: CatalogueDetailViewTabs
  }>();

  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();
  const activeTab = ref<CatalogueDetailViewTabs>(CatalogueDetailViewTabs.Details);
  watch(props, () => activeTab.value = props.activeTab);

  function onTabClick (viewTab: CatalogueDetailViewTabs) {
    if (viewTab !== props.activeTab) {
      // props.catalogueEntry is never undefined but typescript doesn't register v-if null checks inside the template
      emit('navigate', CatalogueTab.CatalogueEntries, CatalogueView.View, {
        viewTab,
        recordId: props.catalogueEntry!.id
      });
    }
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
                         :entry="catalogueEntry"
                         @navigate="(tab, view, options) => emit('navigate', tab, view, options)"/>
  <entry-view-attribute-tab v-if="activeTab === CatalogueDetailViewTabs.AttributeTable && catalogueEntry"
                            :entry="catalogueEntry"
                            @navigate="(tab, view, options) => emit('navigate', tab, view, options)"/>
  <entry-view-symbology-tab v-if="activeTab === CatalogueDetailViewTabs.Symbology && catalogueEntry"
                            :entry="catalogueEntry"/>
  <entry-view-metadata-tab v-if="activeTab === CatalogueDetailViewTabs.Metadata && catalogueEntry"
                            :entry="catalogueEntry"
                            @navigate="(tab, view, options) => emit('navigate', tab, view, options)"/>
</template>
