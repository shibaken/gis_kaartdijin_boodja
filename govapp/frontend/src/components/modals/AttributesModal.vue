<script lang="ts" setup>
  import Modal from "../../components/widgets/Modal.vue";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import { useModalStore } from "../../stores/ModalStore";
  import { computed, ref } from "vue";
  import { ModalTypes } from "../../stores/ModalStore.api";
  import { Attribute } from "../../providers/relatedEntityProvider.api";
  import AttributesAddForm from "../detailViews/AttributesAddForm.vue";
  import { useAttributeStore } from "../../stores/AttributeStore";
  import { storeToRefs } from "pinia";

  const props = defineProps<{
    show: boolean,
    catalogueEntry: CatalogueEntry,
    mode: ModalTypes
  }>();

  const modalStore = useModalStore();
  const attributeStore = useAttributeStore();
  const { editingAttribute } = storeToRefs(attributeStore);
  const { removeAttribute } = attributeStore;

  const formDirty = ref(false);
  const attributeModeText = computed(() => {
    switch (props.mode) {
      case ModalTypes.ATTRIBUTE_ADD:
        return "Add";
      case ModalTypes.ATTRIBUTE_EDIT:
        return "Edit";
      case ModalTypes.ATTRIBUTE_DELETE:
        return "Delete";
    }
  });
  const modalSize = computed(() => {
    switch (props.mode) {
      case ModalTypes.ATTRIBUTE_ADD:
        return "modal-lg";
      case ModalTypes.ATTRIBUTE_EDIT:
        return "modal-xl";
      case ModalTypes.ATTRIBUTE_DELETE:
        return "modal-md";
    }
  });
  const showForm = computed(() => [ModalTypes.ATTRIBUTE_ADD, ModalTypes.ATTRIBUTE_EDIT].includes(props.mode));

  async function onAcceptClick () {
    modalStore.hideModal();
  }

  function valuesUpdated (values: Partial<Attribute>) {
    if (editingAttribute.value) {
      editingAttribute.value = values;
    }
  }

  function onClose () {
    modalStore.hideModal();
    editingAttribute.value = undefined;
    formDirty.value = false;
  }
</script>

<template>
  <modal :show="show" modal-id="attribute-log" :modal-size="modalSize"
         :show-save-button="true" :enable-save-button="true" save-button-text="OK"
         @close="onClose" @save="onAcceptClick">
    <template #header>
      <h1>{{ attributeModeText }} Attribute</h1>
    </template>
    <template #body v-if="catalogueEntry">
      <attributes-add-form v-if="showForm" @valid-value-updated="valuesUpdated" :catalogue-entry="catalogueEntry"
                         :form-dirty="formDirty"/>
    </template>
  </modal>
</template>
