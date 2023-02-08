<script lang="ts" setup>
  import Card from "./Card.vue";
  import NotificationDatatable from "../dataTable/NotificationDatatable.vue";
  import { NotificationCrudType, NotificationStore } from "../../stores/NotificationStore.api";
  import { ModalTypes } from "../../stores/ModalStore.api";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import { useNotificationStore } from "../../stores/NotificationStore";
  import { Ref } from "vue";
  import { Notification } from "../../providers/notificationProvider.api";
  import { storeToRefs } from "pinia";
  import { useModalStore } from "../../stores/ModalStore";
  import { NavigationEmits } from "../viewState.api";
  import { notificationProvider } from "../../providers/notificationProvider";
  import { NotificationRequestType } from "../../backend/backend.api";
  import { usePermissionsComposable } from "../../tools/permissionsComposable";

  const props = defineProps<{
    entry: CatalogueEntry
  }>();

  const notificationStore = useNotificationStore();
  const { editingNotification, notificationCrudType,
    editingType }: NotificationStore = storeToRefs(notificationStore);
  const { getByType } = notificationStore;
  const { showModal } = useModalStore();
  const { isLoggedInUserEditor, isLoggedInUserAdmin } = usePermissionsComposable();

  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();

  async function onSave() {
    if (!editingType?.value) {
      throw new Error("onSave: attempted to save without a editing type set");
    }
    if (editingNotification.value) {
      const notificationsByType: Ref<Notification[]> = getByType(editingType.value);
      switch (notificationCrudType.value) {
        case NotificationCrudType.New:
          const createdNotification = await notificationProvider.createNotification(editingType.value, editingNotification.value);
          notificationsByType.value.push(createdNotification);
          editingNotification.value = undefined;
          editingType.value = undefined;
          break;
        case NotificationCrudType.Edit:
          const editedNotification = await notificationProvider.updateNotification(editingType.value, editingNotification.value);
          const match = notificationsByType.value.find(notification => notification.id === editingNotification.value?.id);
          if (match) {
            Object.assign(match, editedNotification);
          }
          editingNotification.value = undefined;
          break;
        case NotificationCrudType.Delete:
          if (editingNotification.value.id) {
            const success = await notificationProvider.removeNotification(editingType.value, editingNotification.value.id);
            if (success) {
              notificationsByType.value = notificationsByType.value.filter(notification => notification.id !== editingNotification.value?.id);
              editingNotification.value = undefined;
            }
          }
          break;
      }
      notificationCrudType.value = NotificationCrudType.None;
    }
  }

  function onNew (type: NotificationRequestType) {
    if (notificationCrudType.value !== NotificationCrudType.New) {
      editingNotification.value = { catalogueEntry: props.entry };
      notificationCrudType.value = NotificationCrudType.New;
    }
    editingType.value = type;
    showModal(ModalTypes.NotificationAdd);
  }
</script>

<template>
  <card class="mt-4">
    <template #header>
      <h4>Notifications</h4>
    </template>
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <div class="w-auto d-flex justify-content-end w-100">
          <button class="btn btn-outline-success" :disabled="!isLoggedInUserAdmin && !isLoggedInUserEditor"
                  @click="onNew(NotificationRequestType.Webhook)">
            Add IT System Notification
          </button>
          <button class="btn btn-outline-success ms-2" :disabled="!isLoggedInUserAdmin && !isLoggedInUserEditor"
                  @click="onNew(NotificationRequestType.Email)">
            Add User Notification
          </button>
        </div>
        <notification-datatable/>
        <button class="btn btn-success ms-auto" :disabled="!isLoggedInUserAdmin && !isLoggedInUserEditor"
                @click="onSave">Save Notification</button>
      </div>
    </template>
  </card>
</template>
