import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { NotificationRequestType, NotificationType, PaginatedRecord } from "../backend/backend.api";
import { Notification } from "./notificationProvider.api";
import { CatalogueEntry, CatalogueEntryFilter } from "./catalogueEntryProvider.api";
import { unique } from "../util/filtering";
import { useCatalogueEntryStore } from "../stores/CatalogueEntryStore";
import { CatalogueEntryProvider } from "./catalogueEntryProvider";

export class NotificationProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();
  private catalogueEntryProvider: CatalogueEntryProvider = new CatalogueEntryProvider();
  private emailNotificationTypes = this.backend.getNotificationTypes(NotificationRequestType.Email);
  private webhookNotificationTypes = this.backend.getNotificationTypes(NotificationRequestType.Webhook);

  public async fetchNotifications (notificationType: NotificationRequestType): Promise<Notification[]> {
    const emailNotificationTypes = (await this.emailNotificationTypes).results;
    const webhookNotificationTypes = (await this.webhookNotificationTypes).results;

    const { results } = await this.backend.getNotifications(notificationType);
    const fetchedEntries: Array<CatalogueEntry> = await useCatalogueEntryStore().catalogueEntries;
    const entriesToFetch = results
      .map(notification => notification.catalogue_entry)
      .filter((entryId) => fetchedEntries
        .map(entry => entry.id)
        .findIndex(fetchedId => fetchedId === entryId) === -1);

    const tableFilterMap: CatalogueEntryFilter = new Map();
    const requestedEntries: Array<CatalogueEntry> = fetchedEntries;

    if (entriesToFetch.length > 0) {
      tableFilterMap.set("ids", unique<number>(entriesToFetch));
      const { results: catalogueEntryResults } = await this.catalogueEntryProvider.fetchCatalogueEntries(tableFilterMap);
      requestedEntries.push(...catalogueEntryResults);
    }

    return results
      .map(notification => {
        let notificationTypeMatch;

        if (notificationType === NotificationRequestType.Email) {
          notificationTypeMatch = emailNotificationTypes
            .find(notificationType => notificationType.id === notification.type);
        } else {
          notificationTypeMatch = webhookNotificationTypes
            .find(notificationType => notificationType.id === notification.type);
        }

        const notificationResult = {
          id: notification.id,
          name: notification.name,
          type: notificationTypeMatch,
          catalogueEntry: requestedEntries.find(entry => entry.id === notification.catalogue_entry)?.name,
          email: notification.email,
          url: notification.url
        } as Notification;

        return notificationResult as Notification;
      });
  }

  public async fetchNotificationTypes (notificationType: NotificationRequestType): Promise<PaginatedRecord<NotificationType>> {
    return this.backend.getNotificationTypes(notificationType);
  }
}
