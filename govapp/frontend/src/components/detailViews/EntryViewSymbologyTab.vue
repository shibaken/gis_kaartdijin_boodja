<script lang="ts" setup>
  import { onMounted, ref, Ref } from "vue";
  import Card from "../widgets/Card.vue";
  import { Symbology } from "../../providers/relatedEntityProvider.api";
  import { relatedEntityProvider } from "../../providers/relatedEntityProvider";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import FormTextarea from "../widgets/FormTextarea.vue";
  import { CatalogueDetailViewTabs, CatalogueTab, CatalogueView, NavigationEmits } from "../viewState.api";
  import WorkflowFooter from "../widgets/WorkflowFooter.vue";

  const props = defineProps<{
    entry: CatalogueEntry
  }>();

  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();

  const symbology: Ref<Symbology | undefined> = ref();
  const editingSymbology: Ref<Symbology | undefined> = ref();

  function updateValue (fieldName: string, value: string) {
    editingSymbology.value = { ...editingSymbology.value, sld: value } as Symbology;
  }

  function onReset () {
    editingSymbology.value = symbology.value;
  }

  function onSave (exit: boolean) {
    if (editingSymbology.value) {
      relatedEntityProvider.updateSymbology(editingSymbology.value.id, editingSymbology.value?.sld);

      if (exit) {
        emit('navigate', CatalogueTab.CatalogueEntries, CatalogueView.List);
      } else {
        emit('navigate', CatalogueTab.CatalogueEntries, CatalogueView.View, {
          viewTab: CatalogueDetailViewTabs.Metadata,
          recordId: props.entry.id
        });
      }
    }
  }

  onMounted(async () => {
    editingSymbology.value = symbology.value = await relatedEntityProvider.fetchSymbology(props.entry.id);
  });
</script>

<template>
  <card>
    <template #header>
      <h4>Symbology Definition - {{ symbology?.id ? "Edit" : "Add" }}</h4>
    </template>
    <template #body>
        <form-textarea field="sld" name="SLD" :value="editingSymbology?.sld"
                       @value-updated="updateValue"/>
    </template>
    <template #footer>
      <WorkflowFooter @reset="onReset" @save-continue="onSave(false)" @save-exit="onSave(true)"/>
    </template>
  </card>
</template>
