import { defineStore } from "pinia";
import { NotificationRequestType, NotificationType } from "../backend/backend.api";
import { notificationProvider } from "../providers/notificationProvider";
import type { EmailNotification, Notification, WebhookNotification } from "../providers/notificationProvider.api";
import { Ref, ref } from "vue";
import { NotificationCrudType } from "./NotificationStore.api";

export const useNotificationStore = defineStore("notification",  () => {
  const emailNotifications = ref<Notification[]>([]);
  const webhookNotifications = ref<Notification[]>([]);
  const editingNotification: Ref<Partial<Notification> | undefined> = ref(undefined);
  const editingType: Ref<NotificationRequestType | undefined> = ref();
  const notificationCrudType: Ref<NotificationCrudType> = ref(NotificationCrudType.None);
  const emailNotificationTypes: Ref<NotificationType[]> = ref([]);
  const webhookNotificationTypes: Ref<NotificationType[]> = ref([]);

  async function getNotifications (ids?: Array<number>) {
    const emails = await notificationProvider
      .fetchNotifications(NotificationRequestType.Email, ids) as Array<EmailNotification>;
    const webhooks = await notificationProvider
      .fetchNotifications(NotificationRequestType.Webhook, ids) as Array<WebhookNotification>;
    setNotifications(NotificationRequestType.Email, emails);
    setNotifications(NotificationRequestType.Webhook, webhooks);
  }

  function getByType (type: NotificationRequestType): Ref<Notification[]> {
    if (type === NotificationRequestType.Email) {
      return emailNotifications;
    } else {
      return webhookNotifications;
    }
  }
  
  function setNotifications (type: NotificationRequestType, newNotifications: Array<Notification>) {
    getByType(type).value = newNotifications;
  }

  function setEditingNotification(notification: Partial<Notification>) {
    editingNotification.value = notification;
  }

  function updateNotification (type: NotificationRequestType, notification: Notification) {
    const notifications = getByType(type);
    if (!notifications.value.find(value => value.id === notification.id)) {
      throw new Error(`\`updateNotification\`: Tried to update non-existent notification: ${JSON.stringify(notification)}`);
    }

    notifications.value = notifications.value.map(value => value.id === notification.id ? notification : value);
  }

  function removeNotification (type: NotificationRequestType, id: number) {
    if (!getByType(type).value.find(value => value.id === id)) {
      throw new Error(`\`removeNotification (${type})\`: Tried to delete non-existent notification: ${id}`);
    }

    setNotifications(type, getByType(type).value.filter(value => value.id !== id));
  }

  function setNotificationTypes (type: NotificationRequestType, updatedNotificationTypes: Array<NotificationType>) {
    const notificationTypes = type === NotificationRequestType.Email ?
      emailNotificationTypes :
      webhookNotificationTypes;
    notificationTypes.value = updatedNotificationTypes;
  }

  return { emailNotifications, webhookNotifications, editingNotification, editingType, notificationCrudType,
    emailNotificationTypes, webhookNotificationTypes, setNotifications, setEditingNotification, getNotifications,
    setNotificationTypes, removeNotification, getByType };
});
