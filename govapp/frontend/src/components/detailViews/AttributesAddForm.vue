<script lang="ts" setup>
  import FormInput from "../widgets/FormInput.vue";
  import { storeToRefs } from "pinia";
  import { computed, toRefs, watch } from "vue";
  import { useComputedValidation, ValidationConfig } from "../../tools/formValidationComposable";
  import { useAttributeStore } from "../../stores/AttributeStore";
  import { Attribute } from "../../providers/relatedEntityProvider.api";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";

  const props = defineProps<{
    formDirty: boolean,
    catalogueEntry: CatalogueEntry
  }>();
  const emit = defineEmits<{
    (e: "valid-value-updated", value: Omit<Attribute, "id">): void
  }>();

  const { attributes, editingAttribute } = storeToRefs(useAttributeStore());
  const attributeNewConfig: ValidationConfig<Attribute> = {
    fields: ["type", "name", "type", "order", "catalogueEntry"]
  };

  const computedValidation = useComputedValidation<Attribute>(attributeNewConfig, editingAttribute);
  const { validationErrors, dirtyFields } = toRefs(computedValidation);
  const { enfilthenField } = computedValidation;

  function updateValue (fieldName: string, value: string | number) {
    editingAttribute.value = { ...editingAttribute.value, [fieldName]: value };
    enfilthenField(fieldName as keyof Attribute);
  }

  const invalidFields = computed(() => Object.fromEntries(
    Object.entries(dirtyFields.value).map(([key, value]) => [
      key,
      (props.formDirty || value) && validationErrors.value.filter(error => error.id === key).length > 0
    ])
  ));

  watch(invalidFields, () => {
    if (props.formDirty && validationErrors.value.length === 0) {
      emit("valid-value-updated", editingAttribute.value as Omit<Attribute, "id">);
    }
  });
</script>

<template>
  <div class="d-flex flex-row">
    <div class="d-flex flex-column w-auto">
      <form-input field="name" name="Name" type="text" :value="editingAttribute?.name" :is-invalid="invalidFields.name" @value-updated="updateValue"/>
    </div>
    <div class="d-flex flex-column w-auto mx-3">
      <form-input field="type" name="Type" type="text" :value="editingAttribute?.type" :is-invalid="invalidFields.type" @value-updated="updateValue"/>
    </div>
    <div class="d-flex flex-column w-auto">
      <form-input field="order" name="Order" type="text" :value="editingAttribute?.order?.toString()" :is-invalid="invalidFields.order" @value-updated="updateValue"/>
    </div>
  </div>
</template>