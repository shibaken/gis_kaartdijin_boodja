<script lang="ts" setup async>
  import DataTable from "./DataTable.vue";
  import { storeToRefs } from "pinia";
  import { computed, ComputedRef, onMounted } from "vue";
  import { useNotificationStore } from "../../stores/NotificationStore";
  import { ModalTypes } from "../../stores/ModalStore.api";
  import { useModalStore } from "../../stores/ModalStore";
  import { Notification } from "../../providers/notificationProvider.api";
  import { NotificationCrudType } from "../../stores/NotificationStore.api";
  import { NotificationRequestType } from "../../backend/backend.api";

  const notificationStore = useNotificationStore();
  const modalStore = useModalStore();

  // get Stores and fetch with `storeToRef`
  const { getNotifications } = notificationStore;
  const { emailNotifications, webhookNotifications, editingNotification, editingType,
    notificationCrudType } = storeToRefs(notificationStore);
  const { showModal } = useModalStore();

  const filteredNotifications: ComputedRef<Notification[]> = computed(() => {
    const emails = emailNotifications?.value ?? [];
    const webhooks = webhookNotifications?.value ?? [];
    const filtered = [...emails, ...webhooks]
      .filter(notification => notification.id !== editingNotification.value?.id);
    if (editingNotification.value) {
      filtered.concat([editingNotification.value as Notification]);
    }
    return filtered;
  });

  function onEditClick (notification: Notification) {
    editingNotification.value = notification as Partial<Notification>;
    editingType.value = !!notification.email ? NotificationRequestType.Email : NotificationRequestType.Webhook;
    notificationCrudType.value = NotificationCrudType.Edit;
    showModal(ModalTypes.NotificationEdit);
  }

  function onEditEditingClick () {
    modalStore.showModal(ModalTypes.NotificationEdit);
    notificationCrudType.value = NotificationCrudType.Edit;
    editingType.value = !!editingNotification.value?.email ?
      NotificationRequestType.Email :
      NotificationRequestType.Webhook;
  }

  onMounted(() => {
    getNotifications();
  });
</script>

<template>
  <data-table :paginate="false">
    <template #headers>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>URL</th>
        <th>Type</th>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <tr v-if="filteredNotifications.length > 0" v-for="(row, index) in filteredNotifications" :key="index">
        <td>{{ row.name }}</td>
        <td>{{ row.email }}</td>
        <td>{{ row.url }}</td>
        <td>{{ row.type.label }}</td>
        <td>
          <a href="#" class="me-2" @click="onEditClick(row)">Edit</a>
        </td>
      </tr>
      <tr v-if="editingNotification" :class="{
        'table-info': notificationCrudType === NotificationCrudType.Edit,
        'table-danger': notificationCrudType === NotificationCrudType.Delete,
        'table-success': notificationCrudType === NotificationCrudType.New
        }">
        <td>{{ editingNotification.name }}</td>
        <td>{{ editingNotification.email }}</td>
        <td>{{ editingNotification.url }}</td>
        <td>{{ editingNotification.type?.label }}</td>
        <td>
          <a href="#" class="me-2" @click="onEditEditingClick">Edit</a>
        </td>
      </tr>
    </template>
  </data-table>
</template>
