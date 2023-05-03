<script lang="ts" setup>
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import { relatedEntityProvider } from "../../providers/relatedEntityProvider";
  import Accordion from "../widgets/Accordion.vue";
  import AttributeDatatable from "../dataTable/AttributeDatatable.vue";
  import { onMounted, Ref } from "vue";
  import { useAttributeStore } from "../../stores/AttributeStore";
  import { storeToRefs } from "pinia";
  import { CatalogueDetailViewTabs, CatalogueTab, ViewMode, NavigationCatalogueEmits } from "../viewState.api";
  import { Attribute } from "../../providers/relatedEntityProvider.api";
  import WorkflowFooter from "../widgets/WorkflowFooter.vue";
  import { AttributeCrudType } from "../../stores/AttributeStore.api";
  import { useModalStore } from "../../stores/ModalStore";
  import { ModalTypes } from "../../stores/ModalStore.api";

  const props = defineProps<{
    entry: CatalogueEntry
  }>();

  const attributeStore = useAttributeStore();
  type AttributeStore = {
    attributes: Ref<Array<Attribute>>,
    editingAttribute: Ref<Partial<Attribute> | undefined>,
    attributeCrudType: Ref<AttributeCrudType>
  };
  const { attributes, editingAttribute, attributeCrudType }: AttributeStore = storeToRefs(attributeStore);
  const { setAttributes } = attributeStore;

  const { showModal } = useModalStore();

  interface NavEmits extends NavigationCatalogueEmits {}
  const emit = defineEmits<NavEmits>();

  function onReset () {
    editingAttribute.value = undefined;
    attributeCrudType.value = AttributeCrudType.None;
  }

  async function onSave(exit: boolean) {
    if (editingAttribute.value) {
      switch (attributeCrudType.value) {
        case AttributeCrudType.New:
          const createdAttribute = await relatedEntityProvider.createAttribute(editingAttribute.value);
          attributes.value.push(createdAttribute);
          editingAttribute.value = undefined;
          break;
        case AttributeCrudType.Edit:
          const editedAttribute = await relatedEntityProvider.updateAttribute(editingAttribute.value);
          const match = attributes.value.find(attribute => attribute.id === editingAttribute.value?.id);
          if (match) {
            Object.assign(match, editedAttribute);
          }
          editingAttribute.value = undefined;
          break;
        case AttributeCrudType.Delete:
          if (editingAttribute.value.id) {
            const success = await relatedEntityProvider.removeAttribute(editingAttribute.value.id);
            if (success) {
              attributes.value = attributes.value.filter(attribute => attribute.id !== editingAttribute.value?.id);
              editingAttribute.value = undefined;
            }
          }
          break;
      }
      attributeCrudType.value = AttributeCrudType.None;
      if (exit) {
        emit('navigate', CatalogueTab.CatalogueEntries, ViewMode.List);
      } else {
        emit('navigate', CatalogueTab.CatalogueEntries, ViewMode.View, {
          viewTab: CatalogueDetailViewTabs.Symbology,
          recordId: props.entry.id
        });
      }
    }
  }

  function onNew () {
    editingAttribute.value = { catalogueEntry: props.entry };
    attributeCrudType.value = AttributeCrudType.New;
    showModal(ModalTypes.AttributeAdd);
  }

  onMounted(async () => {
    setAttributes(await relatedEntityProvider.fetchAttributes([props.entry.id]));
  });
</script>

<template>
  <accordion id-prefix="attributeTable" header-text="Attribute Table Definition" class="mt-4">
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <div class="w-auto d-flex justify-content-end w-100">
          <button class="btn btn-success" @click="onNew">New</button>
        </div>
        <attribute-datatable/>
      </div>
    </template>
  </accordion>
  <workflow-footer @reset="onReset" @save-continue="onSave(false)" @save-exit="onSave(true)"/>
</template>
