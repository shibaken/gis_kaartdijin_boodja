import { BackendService } from "./backend.service";
import { RawCatalogueEntry, RawLayerSubscription, PaginatedRecord, RecordStatus,
  User, StatusType, RawLayerSubmission, NotificationRequestType,
  RawNotification, NotificationType, RawWebhookNotification,
  RawEmailNotification } from "./backend.api";

function wrapPaginatedRecord<T> (results: Array<T>): PaginatedRecord<T> {
  return {
    previous: null,
    next: null,
    count: results.length,
    results
  };
}

const DUMMY_CATALOGUE_ENTRIES: Array<RawCatalogueEntry> = [
  {
    "id": 1,
    "name": "Catalogue Entry 1",
    "description": "This is the first example catalogue entry",
    "status": 1,
    "updated_at": "2022-10-13T04:26:24.629841Z",
    "custodian": 1,
    "assigned_to": 1,
    "subscription": 1,
    "active_layer": 1,
    "layers": [1],
    "email_notifications": [1],
    "webhook_notifications": [1]
  },
  {
    "id": 2,
    "name": "Catalogue Entry 2",
    "description": "This is the second example catalogue entry",
    "status": 2,
    "updated_at": "2022-10-12T21:05:32.325153Z",
    "custodian": 2,
    "assigned_to": 3,
    "subscription": 2,
    "active_layer": 2,
    "layers": [2],
    "email_notifications": [2],
    "webhook_notifications": [2]
  },
  {
    "id": 3,
    "name": "Catalogue Entry 3",
    "description": "This is the third example catalogue entry",
    "status": 3,
    "updated_at": "2022-10-11T12:44:15.562984Z",
    "custodian": 2,
    "assigned_to": null,
    "subscription": 3,
    "active_layer": 3,
    "layers": [3],
    "email_notifications": [3],
    "webhook_notifications": [3]
  }
];

const DUMMY_LAYER_SUBSCRIPTIONS: Array<RawLayerSubscription> = [
  {
    "id": 1,
    "name": "Layer Subscription 1",
    "url": "https://www.abc.net.au/",
    "frequency": "1 11:11:11",
    "status": 1,
    "subscribed_at": "2022-10-13T02:11:02.818232Z",
    "catalogue_entry": 1
  }, {
    "id": 2,
    "name": "Layer Subscription 2",
    "url": "https://www.sbs.com.au/",
    "frequency": "2 22:22:22",
    "status": 2,
    "subscribed_at": "2022-10-12T23:53:32.756754Z",
    "catalogue_entry": 2
  }, {
    "id": 3,
    "name": "Layer Subscription 3",
    "url": "https://www.nit.com.au/",
    "frequency": "4 09:33:33",
    "status": 3,
    "subscribed_at": "2022-10-11T13:27:12.345346Z",
    "catalogue_entry": 3
  }
];

const DUMMY_LAYER_SUBMISSIONS: Array<RawLayerSubmission> = [
  {
    "id": 1,
    "name": "Layer Submission 1",
    "description": "This is the first example layer submission",
    "file": "https://www.google.com/",
    "status": 1,
    "submitted_at": "2022-10-13T04:11:05.195734Z",
    "catalogue_entry": 1,
    "attributes": [
      1,
      2,
      3
    ],
    "metadata": 1,
    "symbology": 1
  },
  {
    "id": 2,
    "name": "Layer Submission 2",
    "description": "This is the second example layer submission",
    "file": "https://www.yahoo.com/",
    "status": 2,
    "submitted_at": "2022-10-12T07:56:15.665294Z",
    "catalogue_entry": 2,
    "attributes": [
      4,
      5,
      6
    ],
    "metadata": 2,
    "symbology": 2
  },
  {
    "id": 3,
    "name": "Layer Submission 3",
    "description": "This is the third example layer submission",
    "file": "https://www.bing.com/",
    "status": 3,
    "submitted_at": "2022-10-11T11:24:42.816585Z",
    "catalogue_entry": 3,
    "attributes": [
      7,
      8,
      9
    ],
    "metadata": 3,
    "symbology": 3
  }
];

const DUMMY_STATUSES: Array<RecordStatus<unknown>> = [
  { "id": 1, "label": "Draft" },
  { "id": 2, "label": "Locked" },
  { "id": 3, "label": "Cancelled" }
];

const DUMMY_USERS: Array<User> = [
  { "id": 1, "username": "Raoul Wallenberg", "groups": [] },
  { "id": 2, "username": "Carl Lutz", "groups": [] },
  { "id": 3, "username": "Chiune Sugihara", "groups": [] }
];

const DUMMY_EMAIL_NOTIFICATIONS: Array<RawEmailNotification> = [
  {
    "id": 1,
    "name": "Email Notification 1",
    "type": 1,
    "email": "cat@example.com",
    "catalogue_entry": 1
  },
  {
    "id": 2,
    "name": "Email Notification 2",
    "type": 2,
    "email": "dog@example.com",
    "catalogue_entry": 2
  },
  {
    "id": 3,
    "name": "Email Notification 3",
    "type": 3,
    "email": "bird@example.com",
    "catalogue_entry": 3
  }
];

const DUMMY_WEBHOOK_NOTIFICATIONS: Array<RawWebhookNotification> = [
  {
    "id": 1,
    "name": "Webhook Notification 1",
    "type": 1,
    "url": "https://www.dbca.wa.gov.au/",
    "catalogue_entry": 1
  },
  {
    "id": 2,
    "name": "Webhook Notification 2",
    "type": 2,
    "url": "https://www.dpaw.wa.gov.au/",
    "catalogue_entry": 2
  },
  {
    "id": 3,
    "name": "Webhook Notification 3",
    "type": 3,
    "url": "https://www.dcceew.gov.au/",
    "catalogue_entry": 3
  }
];

const DUMMY_EMAIL_NOTIFICATION_TYPES: Array<NotificationType> = [
  {
    "id": 1,
    "label": "On Approve"
  },
  {
    "id": 2,
    "label": "On Lock"
  },
  {
    "id": 3,
    "label": "Both"
  }
];

const DUMMY_WEBHOOK_NOTIFICATION_TYPES: Array<NotificationType> = [
  {
    "id": 1,
    "label": "On Approve"
  },
  {
    "id": 2,
    "label": "On Lock"
  },
  {
    "id": 3,
    "label": "Both"
  }
];

export class BackendServiceStub implements BackendService {
  public getLayerSubscriptions (): Promise<PaginatedRecord<RawLayerSubscription>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_LAYER_SUBSCRIPTIONS));
  }

  public getCatalogueEntries (): Promise<PaginatedRecord<RawCatalogueEntry>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_CATALOGUE_ENTRIES));
  }

  public async getLayerSubmissions (): Promise<PaginatedRecord<RawLayerSubmission>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_LAYER_SUBMISSIONS));
  }

  public async getStatuses<T> (): Promise<PaginatedRecord<RecordStatus<T>>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_STATUSES) as PaginatedRecord<RecordStatus<T>>);
  }

  async getStatus<T> (_statusType: StatusType, statusId: number): Promise<RecordStatus<T>> {
    return Promise.resolve(DUMMY_STATUSES.find(({ id }) => id === statusId) as RecordStatus<T>);
  }

  async getUser (userId: number): Promise<User> {
    return Promise.resolve(DUMMY_USERS.find(({ id }) => id === userId) as User);
  }

  async getUsers (): Promise<PaginatedRecord<User>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_USERS));
  }

  public async getNotifications (notificationType: NotificationRequestType): Promise<PaginatedRecord<RawNotification>> {
    const notifications = notificationType === NotificationRequestType.Email ?
      DUMMY_EMAIL_NOTIFICATIONS :
      DUMMY_WEBHOOK_NOTIFICATIONS;
    return Promise.resolve(wrapPaginatedRecord(notifications));
  }

  public async getNotificationTypes (notificationType: NotificationRequestType): Promise<PaginatedRecord<NotificationType>> {
    const notifications = notificationType === NotificationRequestType.Email ?
      DUMMY_EMAIL_NOTIFICATION_TYPES :
      DUMMY_WEBHOOK_NOTIFICATION_TYPES;
    return Promise.resolve(wrapPaginatedRecord(notifications));
  }
}
