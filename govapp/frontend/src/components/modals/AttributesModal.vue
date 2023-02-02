<script lang="ts" setup>
  import Modal from "../../components/widgets/Modal.vue";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import { useModalStore } from "../../stores/ModalStore";
  import { computed, Ref, ref, watch } from "vue";
  import { ModalTypes } from "../../stores/ModalStore.api";
  import { Attribute } from "../../providers/relatedEntityProvider.api";
  import AttributesAddForm from "../detailViews/AttributesAddForm.vue";
  import { useAttributeStore } from "../../stores/AttributeStore";
  import { storeToRefs } from "pinia";
  import { MappingValidationError } from "../../tools/formValidationComposable";

  const props = defineProps<{
    show: boolean,
    catalogueEntry: CatalogueEntry,
    mode: ModalTypes
  }>();

  const modalStore = useModalStore();
  const attributeStore = useAttributeStore();
  const { editingAttribute } = storeToRefs(attributeStore);

  const formDirty = ref(false);
  const attributeModeText = computed(() => {
    switch (props.mode) {
      case ModalTypes.AttributeAdd:
        return "Add";
      case ModalTypes.AttributeEdit:
        return "Edit";
      case ModalTypes.AttributeDelete:
        return "Delete";
    }
  });
  const modalSize = computed(() => {
    switch (props.mode) {
      case ModalTypes.AttributeAdd:
        return "modal-lg";
      case ModalTypes.AttributeEdit:
        return "modal-xl";
      case ModalTypes.AttributeDelete:
        return "modal-md";
    }
  });
  const showForm = computed(() => [ModalTypes.AttributeAdd, ModalTypes.AttributeEdit].includes(props.mode));
  const validationErrors: Ref<MappingValidationError[] | undefined> = ref();

  async function onAcceptClick () {
    formDirty.value = true;
    if (validationErrors.value && validationErrors.value.length === 0 || props.mode === ModalTypes.AttributeDelete) {
      modalStore.hideModal();
    }
  }

  function valuesUpdated (values: Partial<Attribute>) {
    if (editingAttribute.value) {
      editingAttribute.value = values;
    }
  }

  function errorsUpdated (errors: Array<MappingValidationError>) {
    validationErrors.value = errors;
  }

  function onClose () {
    modalStore.hideModal();
    editingAttribute.value = undefined;
    formDirty.value = false;
  }

  watch(editingAttribute, () => {
    if (!editingAttribute.value) {
      formDirty.value = false;
    }
  });
</script>

<template>
  <modal :show="show" modal-id="attribute-log" :modal-size="modalSize" :show-save-button="true" save-button-text="OK"
         @close="onClose" @save="onAcceptClick">
    <template #header>
      <h1>{{ attributeModeText }} Attribute</h1>
    </template>
    <template #body v-if="catalogueEntry">
      <attributes-add-form v-if="showForm" :catalogue-entry="catalogueEntry" :form-dirty="formDirty"
                           @valid-value-updated="valuesUpdated" @field-errors-updated="errorsUpdated"/>
    </template>
  </modal>
</template>
