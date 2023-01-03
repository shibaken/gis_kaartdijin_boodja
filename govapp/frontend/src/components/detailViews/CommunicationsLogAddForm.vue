<script lang="ts" setup>
  import FormInput from "../widgets/FormInput.vue";
  import FormSelect from "../widgets/FormSelect.vue";
  import { useLogsStore } from "../../stores/LogsStore";
  import { storeToRefs } from "pinia";
  import { computed, ComputedRef, Ref, ref, toRefs, watch } from "vue";
  import { CommunicationLog } from "../../providers/logsProvider.api";
  import { DateTime } from "luxon";
  import { useComputedValidation, ValidationConfig } from "../../tools/formValidationComposable";

  const props = defineProps<{
    formDirty: boolean
  }>();
  const emit = defineEmits<{
    (e: "valid-value-updated", value: Omit<CommunicationLog, "id" | "documents">): void
  }>();

  const { communicationLogTypes } = storeToRefs(useLogsStore());

  const typeOptions: ComputedRef<Array<[string, string]>> = computed(() => communicationLogTypes.value
      .map(type => [type.label, type.id.toString()]));
  const formData: Ref<Partial<CommunicationLog>> = ref({ createdAt: DateTime.now().toISODate()});

  const logNewConfig: ValidationConfig<CommunicationLog> = {
    fields: ["type", "from"]
  };

  const computedValidation = useComputedValidation<CommunicationLog>(logNewConfig, formData);
  const { validationErrors, dirtyFields } = toRefs(computedValidation);
  const { enfilthenField } = computedValidation;

  function updateType (typeId: number) {
    const logType = communicationLogTypes.value.find(type => type.id === typeId);
    if (logType) {
      updateValue("type", logType.id.toString());
    }
  }

  function updateValue (fieldName: string, value: string | number) {
    formData.value = { ...formData.value, [fieldName]: value };
    enfilthenField(fieldName as keyof CommunicationLog);
  }

  const invalidFields = computed(() => Object.fromEntries(
    Object.entries(dirtyFields.value).map(([key, value]) => [
      key,
      (props.formDirty || value) && validationErrors.value.filter(error => error.id === key).length > 0
    ])
  ));

  watch(invalidFields, () => {
    if (props.formDirty && validationErrors.value.length === 0) {
      emit("valid-value-updated", formData.value as Omit<CommunicationLog, "id" | "documents">);
    }
  });
</script>

<template>
  <div class="d-flex flex-row">
    <div class="d-flex flex-column w-50">
      <form-select field="type" name="Type" :values="typeOptions" :value="formData.type?.id.toString()" :is-invalid="invalidFields.type"
                   :show-empty="true" @value-updated="(_, value) => updateType(parseInt(value))"/>
      <form-input field="from" name="From" type="text" :value="formData.from" :is-invalid="invalidFields.from" @value-updated="updateValue"/>
      <form-input field="to" name="To" type="text" :value="formData.to" :is-invalid="invalidFields.to" @value-updated="updateValue"/>
      <form-input field="cc" name="CC" type="text" :value="formData.cc" :is-invalid="invalidFields.cc" @value-updated="updateValue"/>
    </div>
    <div class="d-flex flex-column w-50">
      <form-input field="subject" name="Subject" type="text" :value="formData.subject" :is-invalid="invalidFields.subject" @value-updated="updateValue"/>
      <form-input field="text" name="Text" type="text" :value="formData.text" :is-invalid="invalidFields.text" @value-updated="updateValue"/>
    </div>
  </div>
</template>