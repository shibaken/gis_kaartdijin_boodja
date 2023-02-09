import { Ref } from "vue";
import { Notification } from "../providers/notificationProvider.api";
import { NotificationRequestType } from "../backend/backend.api";

export enum NotificationCrudType {
  None,
  New,
  Edit,
  Delete
}

export type NotificationStore = {
  emailNotifications: Ref<Array<Notification>>,
  webhookNotifications: Ref<Array<Notification>>,
  editingNotification: Ref<Partial<Notification> | undefined>,
  notificationCrudType: Ref<NotificationCrudType>,
  editingType: Ref<NotificationRequestType | undefined>
};