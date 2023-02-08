import { NotificationType } from "../backend/backend.api";
import { CatalogueEntry } from "./catalogueEntryProvider.api";

export interface Notification {
  id: number;
  name: string;
  type: NotificationType;
  catalogueEntry?: CatalogueEntry;
  email?: string;
  url?: string;
}

export type EmailNotification = Notification;
export type WebhookNotification = Notification;
