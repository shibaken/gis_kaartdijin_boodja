<script lang="ts" setup>
  import FormInput from "../widgets/FormInput.vue";
  import { storeToRefs } from "pinia";
  import { computed, ComputedRef, onMounted, toRefs, watch } from "vue";
  import { MappingValidationError, useComputedValidation, ValidationConfig } from "../../tools/formValidationComposable";
  import { useNotificationStore } from "../../stores/NotificationStore";
  import { notificationProvider } from "../../providers/notificationProvider";
  import { Notification } from "../../providers/notificationProvider.api";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import FormSelect from "../widgets/FormSelect.vue";
  import { NotificationRequestType, NotificationType } from "../../backend/backend.api";

  const props = defineProps<{
    formDirty: boolean,
    catalogueEntry: CatalogueEntry,
    notificationType: NotificationRequestType,
  }>();
  const emit = defineEmits<{
    (e: "valid-value-updated", value: Omit<Notification, "id">): void,
    (e: "field-errors-updated", value: Array<MappingValidationError>): void
  }>();

  const { editingNotification, emailNotificationTypes, webhookNotificationTypes } = storeToRefs(useNotificationStore());
  const notificationNewConfig: ValidationConfig<Notification> = {
    mandatory: ["name", "type"],
    oneOf: [
      ["email", "url"]
    ]
  };

  const computedValidation = useComputedValidation<Notification>(notificationNewConfig, editingNotification);
  const { validationErrors, dirtyFields } = toRefs(computedValidation);
  const { enfilthenField } = computedValidation;

  function updateValue (fieldName: string, value: string | number | NotificationType) {
    editingNotification.value = { ...editingNotification.value, [fieldName]: value };
    enfilthenField(fieldName as keyof Notification);
  }

  function updateNotificationType (_: string, key: string) {
    const notificationType = getNotificationTypes().find(type => type.id.toString() === key);
    if (notificationType) {
      updateValue("type", notificationType);
    }
  }

  function getNotificationTypes (): Array<NotificationType> {
    return props.notificationType === NotificationRequestType.Email ?
      emailNotificationTypes.value :
      webhookNotificationTypes.value;
  }

  const invalidFields = computed(() => Object.fromEntries(
    Object.entries(dirtyFields.value).map(([key, value]) => [
      key,
      (props.formDirty || value) && validationErrors.value
        .filter(error => error.id === key || error.id.split("-").includes(key)) // include check for `oneOf` ids
        .length > 0
    ])
  ));

  const notificationDropdownTypes: ComputedRef = computed(() => getNotificationTypes()
      .map(notificationType => [notificationType.label, notificationType.id]));

  watch(invalidFields, () => {
    emit("field-errors-updated", validationErrors.value);
    if (validationErrors.value.length === 0) {
      // Update the valid value, and whether the form is error free
      emit("valid-value-updated", editingNotification.value as Omit<Notification, "id">);
    }
  });

  onMounted(() => {
    notificationProvider.fetchNotificationTypes(props.notificationType);
  });
</script>

<template>
  <div class="d-flex flex-row">
    <div class="d-flex flex-column w-auto">
      <form-input field="name" :name="notificationType === NotificationRequestType.Email ? 'User name' : 'IT System'"
                  type="text" :value="editingNotification?.name" :is-invalid="invalidFields.name"
                  @value-updated="updateValue"/>
    </div>
    <div class="d-flex flex-column w-auto mx-3">
      <form-select field="type" name="Type" :value="editingNotification?.type?.id.toString()"
                   :is-invalid="invalidFields.type" :values="notificationDropdownTypes"
                   @value-updated="updateNotificationType"/>
    </div>
    <div v-if="notificationType === NotificationRequestType.Email" class="d-flex flex-column w-auto">
      <form-input field="email" name="Email" type="text" :value="editingNotification?.email?.toString()"
                  :is-invalid="invalidFields.email" @value-updated="updateValue"/>
    </div>
    <div v-if="notificationType === NotificationRequestType.Webhook" class="d-flex flex-column w-auto">
      <form-input field="url" name="Url" type="text" :value="editingNotification?.url?.toString()"
                  :is-invalid="invalidFields.email" @value-updated="updateValue"/>
    </div>
  </div>
</template>
