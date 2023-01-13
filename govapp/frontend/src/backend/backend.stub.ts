/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { BackendService } from "./backend.service";
import { RawCatalogueEntry, RawLayerSubscription, PaginatedRecord, RecordStatus, StatusType, RawLayerSubmission,
  NotificationRequestType, RawNotification, NotificationType, RawMetadata,
  RawCustodian, Group, RawSymbology, RawAttribute, RawEntryPatch, RawUser, RawPaginationFilter, RawCommunicationLog
} from "./backend.api";
import { CommunicationLogType } from "../providers/logsProvider.api";
import { DUMMY_CATALOGUE_ENTRIES, DUMMY_LAYER_SUBSCRIPTIONS, DUMMY_LAYER_SUBMISSIONS, DUMMY_STATUSES, DUMMY_USERS,
  DUMMY_EMAIL_NOTIFICATIONS, DUMMY_WEBHOOK_NOTIFICATIONS, DUMMY_EMAIL_NOTIFICATION_TYPES,
  DUMMY_WEBHOOK_NOTIFICATION_TYPES, DUMMY_SYMBOLOGIES, DUMMY_ATTRIBUTES, DUMMY_METADATA_LIST, DUMMY_CUSTODIANS,
  DUMMY_GROUPS, DUMMY_COMM_LOGS, DUMMY_COMM_LOG_TYPES } from "./backend.data";

let EDITABLE_CATALOGUE_ENTRIES = DUMMY_CATALOGUE_ENTRIES;

function wrapPaginatedRecord<T> (results: Array<T>): PaginatedRecord<T> {
  return {
    previous: null,
    next: null,
    count: results.length,
    results
  };
}

export class BackendServiceStub extends BackendService {
  public getLayerSubscription (id: number): Promise<RawLayerSubscription> {
    return Promise.resolve(DUMMY_LAYER_SUBSCRIPTIONS.find(dummy => dummy.id === id)!);
  }

  public getLayerSubscriptions (): Promise<PaginatedRecord<RawLayerSubscription>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_LAYER_SUBSCRIPTIONS));
  }

  public getCatalogueEntry (id: number): Promise<RawCatalogueEntry> {
    return Promise.resolve(EDITABLE_CATALOGUE_ENTRIES.find(dummy => dummy.id === id)!);
  }

  public getCatalogueEntries (): Promise<PaginatedRecord<RawCatalogueEntry>> {
    return Promise.resolve(wrapPaginatedRecord(EDITABLE_CATALOGUE_ENTRIES));
  }

  public async getLayerSubmission (id: number): Promise<RawLayerSubmission> {
    return Promise.resolve(DUMMY_LAYER_SUBMISSIONS.find(dummy => dummy.id === id)!);
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

  public async getUser (userId: number): Promise<RawUser> {
    return Promise.resolve(DUMMY_USERS.find(({ id }) => id === userId) as RawUser);
  }

  public async getUsers (): Promise<PaginatedRecord<RawUser>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_USERS));
  }

  public async getMe (): Promise<RawUser> {
    return Promise.resolve(DUMMY_USERS[0]);
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

  public async getRawSymbology (id: number): Promise<RawSymbology> {
    return Promise.resolve(DUMMY_SYMBOLOGIES.find(dummy => dummy.id === id)!);
  }

  public async getRawSymbologies (): Promise<PaginatedRecord<RawSymbology>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_SYMBOLOGIES));
  }

  public async getRawAttribute (id: number): Promise<RawAttribute> {
    return Promise.resolve(DUMMY_ATTRIBUTES.find(dummy => dummy.id === id)!);
  }

  public async getRawAttributes (): Promise<PaginatedRecord<RawAttribute>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_ATTRIBUTES));
  }

  public async getRawMetadata (id: number): Promise<RawMetadata> {
    return Promise.resolve(DUMMY_METADATA_LIST.find(dummy => dummy.id === id)!);
  }

  public async getRawMetadataList (): Promise<PaginatedRecord<RawMetadata>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_METADATA_LIST));
  }

  public async getRawCustodian (id: number): Promise<RawCustodian> {
    return Promise.resolve(DUMMY_CUSTODIANS.find(dummy => dummy.id === id)!);
  }

  public async getRawCustodians (): Promise<PaginatedRecord<RawCustodian>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_CUSTODIANS));
  }

  public async getGroup (id: number): Promise<Group> {
    return Promise.resolve(DUMMY_GROUPS.find(dummy => dummy.id === id)!);
  }

  public async getGroups (): Promise<PaginatedRecord<Group>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_GROUPS));
  }

  public async patchCatalogueEntry (entryId: number, updatedEntry: RawEntryPatch): Promise<RawCatalogueEntry> {
    EDITABLE_CATALOGUE_ENTRIES = EDITABLE_CATALOGUE_ENTRIES.map(entry => entry.id === entryId ? { ...entry, ...updatedEntry } : entry);
    return Promise.resolve(EDITABLE_CATALOGUE_ENTRIES.find(entry => entry.id === entryId)!);
  }

  public async lock (entryId: number): Promise<number> {
    return Promise.resolve(204);
  }

  public async unlock (entryId: number): Promise<number> {
    return Promise.resolve(204);
  }

  public async decline (entryId: number): Promise<number> {
    return Promise.resolve(204);
  }

  public async entryAssign (entryId: number, userId: number): Promise<number> {
    return Promise.resolve(204);
  }

  public async entryUnassign (entryId: number): Promise<number> {
    return Promise.resolve(204);
  }

  async createCommunicationLog(entryId: number, data: Omit<RawCommunicationLog, "id" | "documents">): Promise<number> {
    return Promise.resolve(1);
  }

  async getActionsLogs(entryId: number): Promise<any> {
    return Promise.resolve(undefined);
  }

  async getCommunicationLogs(entryId: number, filter: RawPaginationFilter): Promise<PaginatedRecord<RawCommunicationLog>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_COMM_LOGS));
  }

  async getCommunicationTypes(): Promise<CommunicationLogType[]> {
    return Promise.resolve(DUMMY_COMM_LOG_TYPES);
  }

  async uploadCommunicationFile(entryId: number, logId: number, file: File): Promise<number> {
    return Promise.resolve(1);
  }

  async getWmtsCapabilities(): Promise<string> {
    return Promise.resolve("");
  }

  // Unused method
  protected async modifyAttribute(attribute: Partial<Omit<RawAttribute, "id">>, method: "patch" | "post", id?: number): Promise<RawAttribute> {
    return Promise.resolve({} as RawAttribute);
  }

  async deleteAttribute(id: number): Promise<number> {
    return Promise.resolve(0);
  }

  async patchRawAttribute(attribute: Partial<Omit<RawAttribute, "id">>, id?: number): Promise<RawAttribute> {
    return Promise.resolve(DUMMY_ATTRIBUTES.find(value => value.id === id)!);
  }

  async postRawAttribute(attribute: Omit<RawAttribute, "id">): Promise<RawAttribute> {
    return Promise.resolve({ ...attribute, id: Math.random() });
  }
}
