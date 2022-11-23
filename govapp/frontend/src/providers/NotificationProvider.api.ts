import { NotificationType } from "../backend/backend.api";

export interface Notification {
  id: number;
  name: string;
  type: NotificationType;
  catalogueEntry?: string;
}

export type EmailNotification = Notification;
export type WebhookNotification = Notification;
