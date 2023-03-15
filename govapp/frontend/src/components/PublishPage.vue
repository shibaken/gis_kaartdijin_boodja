<script setup lang="ts">
  import { computed, ref, watch } from "vue";
  import { PublishTab, ViewMode, PublishDetailViewTabs, PublishNavigateEmitsOptions } from "./viewState.api";
  import Card from "./widgets/Card.vue";
  import Accordion from "./widgets/Accordion.vue";
  import SideBarLeft from "./SideBarLeft.vue";
  import { storeToRefs } from "pinia";
  import { usePermissionsComposable } from "../tools/permissionsComposable";
  import { usePublishEntryStore } from "../stores/PublishEntryStore";
  import { PublishEntry } from "../providers/publisherProvider.api";
  import { publisherProvider } from "../providers/publisherProvider";
  import PublishEntryDataTable from "./dataTable/PublishEntryDataTable.vue";
  import PublishEntryFilter from "./widgets/PublishEntryFilter.vue";

  const { publishEntries } = storeToRefs(usePublishEntryStore())
  const selectedTab = ref<PublishTab>(PublishTab.PublishEntries);
  const selectedView = ref<ViewMode>(ViewMode.List);
  const selectedEntryDetailTab = ref<PublishDetailViewTabs>(PublishDetailViewTabs.Details);
  const selectedViewEntry = ref<PublishEntry | undefined>();
  const permissionsComposable = usePermissionsComposable(selectedViewEntry.value?.catalogueEntry);
  const currentEntryView = computed(() => {
    return permissionsComposable.isLoggedInUserAdmin.value || permissionsComposable.isLoggedInUserEditor.value ?
      ViewMode.Edit :
      ViewMode.View;
  })

  watch(publishEntries, () => {
    selectedViewEntry.value = publishEntries.value?.find((entry: PublishEntry) => entry.id === selectedViewEntry.value?.id);
    permissionsComposable.updateCurrentEntry(selectedViewEntry.value?.catalogueEntry);
  }, { deep: true });

  async function navigate (tab: PublishTab, view: ViewMode, options?: PublishNavigateEmitsOptions) {
    selectedView.value = view;
    selectedViewEntry.value = undefined;
    selectedTab.value = tab;
    selectedView.value = view;

    if (typeof options?.recordId !== "number") {
      return;
    } else if (tab === PublishTab.PublishEntries) {
      selectedViewEntry.value = await publisherProvider.fetchPublishEntry(options.recordId);
      if (options?.viewTab) {
        selectedEntryDetailTab.value = options.viewTab as PublishDetailViewTabs;
      }
    } else {
      console.warn("Selected view record was not a recognised type");
    }
  }

  const { clearFilters: clearEntryFilters } = usePublishEntryStore();

  function onClearClick() {
    clearEntryFilters();
  }
</script>

<template>
  <ul class="nav nav-pills mb-4" v-if="selectedView === ViewMode.List">
    <li class="nav-item">
      <button class="nav-link" aria-current="page" href="#"
              :class='{ active: selectedTab === PublishTab.PublishEntries }'
              @click='navigate(PublishTab.PublishEntries, ViewMode.List)'>Publish Entries</button>
    </li>
  </ul>

  <div class="d-flex flex-row">
    <div id="side-bar-wrapper" v-if="selectedView === ViewMode.View">
      <side-bar-left :entry="selectedViewEntry"/>
    </div>
    <div class="w-100">
      <card v-if="selectedView === ViewMode.List">
        <template #header>
          <h4>{{ selectedTab }}</h4>
        </template>
        <template #body>
          <accordion id="filter-accordion" id-prefix="filter" header-text="Filters" class="mb-2">
            <template #body>
              <form class="form d-flex gap-3">
                <publish-entry-filter v-if="selectedTab === PublishTab.PublishEntries"/>
              </form>
              <div class="d-flex">
                <button class="btn btn-sm btn-link link-info align-self-end ms-auto pt-0 mb-1" @click="onClearClick">
                  <small>Clear Filters</small>
                </button>
              </div>
            </template>
          </accordion>
          <publish-entry-data-table v-if='selectedTab === PublishTab.PublishEntries' :view="currentEntryView"
                                      @navigate="navigate"/>
        </template>
      </card>
    </div>
  </div>
</template>

<style lang="scss">
  #filter-accordion {
    .accordion-collapse .accordion-body {
      form {
        overflow-x: auto;
      }
      padding-bottom: 0;
    }
  }

  #side-bar-wrapper {
    width: 24rem;
  }
</style>
