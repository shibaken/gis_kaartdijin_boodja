<script lang="ts" setup>
  import { LayerSubmission } from "../../providers/layerSubmissionProvider.api";
  import Accordion from "../widgets/Accordion.vue";
  import FormInput from "../widgets/FormInput.vue";
  import { CatalogueTab, CatalogueView, NavigationEmits } from "../viewState.api";

  defineProps<{
    submission: LayerSubmission
  }>();

  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();
</script>

<template>
  <accordion id-prefix="details" header-text="Details" class="mt-4">
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <form-input field="name" name="Name" :value="submission.name" type="text" :readonly="true"/>
        <form-input field="submittedDate" name="Submitted Date" :value="submission.submittedDate" type="text"
                    :readonly="true"/>
        <label>
          <small>Catalogue Entry</small><br/>
          <a href="#" @click="emit('navigate', CatalogueTab.CatalogueEntries, CatalogueView.View,
            { recordId: submission.catalogueEntry?.id })">
            {{ submission.catalogueEntry.name }}
          </a>
        </label>
      </div>
    </template>
  </accordion>
</template>