import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { NotificationRequestType, NotificationType, PaginatedRecord, RawNotification,
  RawNotificationFilter } from "../backend/backend.api";
import { Notification } from "./notificationProvider.api";
import { CatalogueEntry, CatalogueEntryFilter } from "./catalogueEntryProvider.api";
import { unique } from "../util/filtering";
import { useCatalogueEntryStore } from "../stores/CatalogueEntryStore";
import { catalogueEntryProvider } from "./catalogueEntryProvider";
import { useNotificationStore } from "../stores/NotificationStore";

export class NotificationProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();
  private emailNotificationTypes = this.backend.getNotificationTypes(NotificationRequestType.Email);
  private webhookNotificationTypes = this.backend.getNotificationTypes(NotificationRequestType.Webhook);

  private toRawNotification (notification: Partial<Notification>): Partial<RawNotification> {
    const rawNotification = {
      id: notification.id,
      name: notification.name,
      type: notification.type?.id,
      catalogue_entry: notification.catalogueEntry?.id,
      email: notification.email,
      url: notification.url
    } as Partial<RawNotification>;

    if (notification.id) {
      rawNotification.id = notification.id;
    }

    return rawNotification;
  };

  private toNewRawNotification (notification: Omit<Notification, "id">): Omit<RawNotification, "id"> {
    return this.toRawNotification(notification) as Omit<RawNotification, "id">;
  }

  public async createNotification (notificationRequestType: NotificationRequestType,
                                   notification: Partial<Notification>): Promise<Notification> {
    let preparedNotification: Omit<Notification, "id">;

    if (notification.id) {
      preparedNotification = Object.fromEntries(Object.entries(notification)
        .filter(([_, value]) => value !== "id")) as Omit<Notification, "id">;
    } else {
      preparedNotification = notification as Omit<Notification, "id">;
    }

    const rawNotification = await this.backend.postRawNotification(notificationRequestType, this.toNewRawNotification(preparedNotification));
    const notificationType = await this.getOrFetchNotificationType(notificationRequestType, rawNotification.type);

    return {
      id: rawNotification.id,
      name: rawNotification.name,
      type: notificationType,
      email: rawNotification.email,
      url: rawNotification.url,
      catalogueEntry: await catalogueEntryProvider.getOrFetch(rawNotification.catalogue_entry)
    } as Notification;
  }

  public async updateNotification (type: NotificationRequestType, notification: Partial<Notification>) {
    let preparedNotification: Omit<Notification, "id">;
    const id = notification.id;

    if (id) {
      preparedNotification = Object.fromEntries(Object.entries(notification)
        .filter(([_, value]) => value !== "id")) as Omit<Notification, "id">;
    } else {
      throw new Error("`updateNotification`: Tried to update notification without providing an ID");
    }

    const rawNotification = await this.backend
      .patchRawNotification(type, this.toNewRawNotification(preparedNotification), id);
    /* This should be the same as `preparedNotification`, but for consistency and capturing possible errors, convert and
     * return what the API hands back.
     */
    return {
      id: rawNotification.id,
      name: rawNotification.name,
      type: await this.getOrFetchNotificationType(type, rawNotification.type),
      email: rawNotification.email,
      webhook: rawNotification.url,
      catalogueEntry: preparedNotification.catalogueEntry
    } as Notification;
  }

  public async removeNotification (notificationType: NotificationRequestType, id: number) {
    const responseCode = await this.backend.deleteNotification(notificationType, id);
    return responseCode >= 200 && responseCode < 300;
  }
  
  public async fetchNotifications (notificationType: NotificationRequestType, ids?: Array<number>): Promise<Notification[]> {
    const emailNotificationTypes = (await this.emailNotificationTypes).results;
    const webhookNotificationTypes = (await this.webhookNotificationTypes).results;

    const { results } = await this.backend.getNotifications(notificationType, { id__in: ids } as RawNotificationFilter);
    const fetchedEntries: Array<CatalogueEntry> = useCatalogueEntryStore().catalogueEntries;
    const entriesToFetch = results
      .map(notification => notification.catalogue_entry)
      .filter((entryId) => fetchedEntries
        .map(entry => entry.id)
        .findIndex(fetchedId => fetchedId === entryId) === -1);

    const tableFilterMap = {} as CatalogueEntryFilter;
    const requestedEntries: Array<CatalogueEntry> = fetchedEntries;

    if (entriesToFetch.length > 0) {
      tableFilterMap.ids = unique<number>(entriesToFetch);
      const { results: catalogueEntryResults } = await catalogueEntryProvider.fetchCatalogueEntries(tableFilterMap);
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

  public async getOrFetchNotificationType(notificationRequestType: NotificationRequestType, id: number): Promise<NotificationType> {
    const notificationTypes = notificationRequestType === NotificationRequestType.Email ?
      useNotificationStore().emailNotificationTypes :
      useNotificationStore().webhookNotificationTypes;

    const notificationType = notificationTypes
        .find(notificationType => notificationType.id === id) ??
      (await this.fetchNotificationTypes(notificationRequestType)).results
        .find(notificationType => notificationType.id === id);

    if (!notificationType) {
      throw new Error(`The requested ${notificationRequestType} notification \`${id}\` was not found from the store or the API.`);
    }

    return notificationType as NotificationType;
  }

  public async fetchNotificationTypes (notificationType: NotificationRequestType): Promise<PaginatedRecord<NotificationType>> {
    const newNotificationTypes = await this.backend.getNotificationTypes(notificationType);
    useNotificationStore().setNotificationTypes(notificationType, newNotificationTypes.results);

    return newNotificationTypes
  }
}

export const notificationProvider = new NotificationProvider();
