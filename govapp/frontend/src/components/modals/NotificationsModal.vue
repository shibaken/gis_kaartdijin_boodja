<script lang="ts" setup>
  import Modal from "../../components/widgets/Modal.vue";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import { useModalStore } from "../../stores/ModalStore";
  import { computed, Ref, ref, watch } from "vue";
  import { ModalTypes } from "../../stores/ModalStore.api";
  import { Notification } from "../../providers/notificationProvider.api";
  import NotificationsAddForm from "../detailViews/NotificationsAddForm.vue";
  import { useNotificationStore } from "../../stores/NotificationStore";
  import { storeToRefs } from "pinia";
  import { MappingValidationError } from "../../tools/formValidationComposable";

  const props = defineProps<{
    show: boolean,
    catalogueEntry: CatalogueEntry,
    mode: ModalTypes
  }>();

  const modalStore = useModalStore();
  const notificationStore = useNotificationStore();
  const { editingNotification, editingType } = storeToRefs(notificationStore);

  const formDirty = ref(false);
  const notificationModeText = computed(() => {
    switch (props.mode) {
      case ModalTypes.NotificationAdd:
        return "Add";
      case ModalTypes.NotificationEdit:
        return "Edit";
      case ModalTypes.NotificationDelete:
        return "Delete";
    }
  });
  const modalSize = computed(() => {
    switch (props.mode) {
      case ModalTypes.NotificationAdd:
        return "modal-lg";
      case ModalTypes.NotificationEdit:
        return "modal-xl";
      case ModalTypes.NotificationDelete:
        return "modal-md";
    }
  });
  const showForm = computed(() => [ModalTypes.NotificationAdd, ModalTypes.NotificationEdit].includes(props.mode));
  const validationErrors: Ref<MappingValidationError[] | undefined> = ref();

  async function onAcceptClick () {
    formDirty.value = true;
    if (validationErrors.value && validationErrors.value.length === 0 || props.mode === ModalTypes.NotificationDelete) {
      modalStore.hideModal();
    }
  }

  function valuesUpdated (values: Partial<Notification>) {
    if (editingNotification.value) {
      editingNotification.value = values;
    }
  }

  function errorsUpdated (errors: Array<MappingValidationError>) {
    validationErrors.value = errors;
  }

  function onClose () {
    modalStore.hideModal();
    editingNotification.value = undefined;
    formDirty.value = false;
  }

  watch(editingNotification, () => {
    if (!editingNotification.value) {
      formDirty.value = false;
    }
  });
</script>

<template>
  <modal :show="show" modal-id="notification-log" :modal-size="modalSize"
         :show-save-button="true" save-button-text="OK"
         @close="onClose" @save="onAcceptClick">
    <template #header>
      <h1>{{ notificationModeText }} Notification</h1>
    </template>
    <template #body v-if="catalogueEntry">
      <notifications-add-form v-if="showForm && editingType" :catalogue-entry="catalogueEntry" :form-dirty="formDirty"
        :notification-type="editingType" @valid-value-updated="valuesUpdated" @field-errors-updated="errorsUpdated"/>
    </template>
  </modal>
</template>
