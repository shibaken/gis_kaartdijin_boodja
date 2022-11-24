<script lang="ts" setup>
  import { ref, defineEmits } from "vue";
  import { CatalogueDetailViewTabs } from "../viewState.api";
  import Accordion from "../widgets/Accordion.vue";
  import FormInput from "../widgets/FormInput.vue";
  import FormTextarea from "../widgets/FormTextarea.vue";
  import NotificationsCard from "../widgets/NotificationsCard.vue";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";

  defineProps<{
    catalogueEntry: CatalogueEntry
  }>();

  defineEmits<{
    (e: "exit-details"): void
  }>();

  const activeTab = ref<CatalogueDetailViewTabs>("details");

  function onTabClick (tab: CatalogueDetailViewTabs) {
    activeTab.value = tab;
  }
</script>

<template>
  <nav class="nav nav-tabs">
    <a class="nav-link" :class="{ active: activeTab === 'details' }" aria-current="page" href="#"
       @click="onTabClick('details')">
      Details
    </a>
    <a class="nav-link" :class="{ active: activeTab === 'attributeTable'}" aria-current="page" href="#"
       @click="onTabClick('attributeTable')">
      Attribute Table
    </a>
    <a class="nav-link" :class="{ active: activeTab === 'symbology'}" aria-current="page" href="#"
       @click="onTabClick('symbology')">
      Symbology
    </a>
    <a class="nav-link" :class="{ active: activeTab === 'metadata'}" aria-current="page" href="#"
       @click="onTabClick('symbology')">
      Metadata
    </a>
  </nav>
  <accordion id-prefix="details" header-text="Details" class="mt-4">
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <form-input field="name" name="Name" :value="catalogueEntry?.name" type="text" :readonly="true"/>
        <form-input field="name" name="Custodian" :value="catalogueEntry?.custodian?.username" type="text"
                    :readonly="true"/>
      </div>
    </template>
  </accordion>

  <accordion id-prefix="description" header-text="Details" class="mt-4">
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <form-textarea field="description" name="Description" :value="catalogueEntry?.description" :readonly="true"/>
      </div>
    </template>
  </accordion>

  <notifications-card/>
</template>
