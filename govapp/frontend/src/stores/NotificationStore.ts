import { defineStore } from "pinia";
import { NotificationRequestType } from "../backend/backend.api";
import { notificationProvider } from "../providers/notificationProvider";
import type { EmailNotification, Notification, WebhookNotification } from "../providers/notificationProvider.api";
import { computed, ref } from "vue";

export const useNotificationStore = defineStore("notification",  () => {
  const emailNotifications = ref<EmailNotification[]>([]);
  const webhookNotifications = ref<WebhookNotification[]>([]);
  const allNotifications = computed<Notification[]>(() => {
    return ([...emailNotifications.value, ...webhookNotifications.value]);
  });

  async function getNotifications (): Promise<[EmailNotification[], WebhookNotification[]]> {
    const emailNotificationResults = await notificationProvider
      .fetchNotifications(NotificationRequestType.Email) as Array<EmailNotification>;
    const webhookNotificationResults = await notificationProvider
      .fetchNotifications(NotificationRequestType.Webhook) as Array<WebhookNotification>;


    emailNotifications.value = emailNotificationResults;
    webhookNotifications.value = webhookNotificationResults;

    return [emailNotificationResults, webhookNotificationResults];
  }

  return { emailNotifications, webhookNotifications, allNotifications, getNotifications };
});
