import { NotificationType } from "../backend/backend.api";

export interface Notification {
  id: number;
  name: string;
  type: NotificationType;
  catalogueEntry?: string;
  email?: string;
  url?: string;
}

export type EmailNotification = Notification;
export type WebhookNotification = Notification;
