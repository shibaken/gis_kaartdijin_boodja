<script lang="ts" setup>
  import { ref } from "vue";
  import { CatalogueTab, CatalogueView, NavigationEmits, SubscriptionDetailViewTabs } from "../viewState.api";
  import Accordion from "../widgets/Accordion.vue";
  import FormInput from "../widgets/FormInput.vue";
  import { LayerSubscription } from "../../providers/layerSubscriptionProvider.api";

  const props = defineProps<{
    layerSubscription?: LayerSubscription
  }>();

  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();
  const activeTab = ref<SubscriptionDetailViewTabs>(SubscriptionDetailViewTabs.Details);
  const layerSubscription = props.layerSubscription; // Resolve build error TS2322

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
  <accordion id-prefix="details" header-text="Details" class="mt-4">
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <form-input field="name" name="Name" :value="props.layerSubscription?.name" type="text" :readonly="true"/>
        <form-input field="url" name="Webservice URL" :value="layerSubscription?.url" type="text"
                    :readonly="true"/>
        <form-input field="frequency" name="Refresh Frequency" :value="layerSubscription?.frequency" type="text"
                    :readonly="true"/>
      </div>
    </template>
  </accordion>
</template>
