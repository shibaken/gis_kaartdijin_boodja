import { Group, NotificationRequestType, NotificationType, RawAttribute, RawCatalogueEntry, RawCatalogueEntryFilter,
  RawCustodian, RawLayerSubmission, RawLayerSubmissionFilter, RawLayerSubscription, RawLayerSubscriptionFilter,
  RawMetadata, RawNotification, RawSymbology, RawUserFilter, RecordStatus, RawEntryPatch, RawUser
} from "./backend.api";
import type { PaginatedRecord, Params, StatusType } from "./backend.api";

function getCookie(name: string) {
  if (!document.cookie) {
    return null;
  }

  const xsrfCookies = document.cookie.split(';')
    .map(c => c.trim())
    .filter(c => c.startsWith(name + '='));

  if (xsrfCookies.length === 0) {
    return null;
  }
  return decodeURIComponent(xsrfCookies[0].split('=')[1]);
}

function fetcher (input: RequestInfo | URL, init: RequestInit = {}) {
  const csrf: string | null = getCookie("csrftoken");
  const request = new Request(input, init);
  if (csrf) {
    request.headers.append("X-CSRFToken", csrf);
    request.headers.set('Content-Type', 'application/json; charset=UTF-8');
  }
  return fetch(request);
}

export function stripNullParams<T extends object> (filter: T): Params {
  return Object.fromEntries(
    Object.entries(filter)
      .filter(([, value]) => {
        return value != null;
      })
  );
}

export class BackendService {
  public async getLayerSubscription (id: number): Promise<RawLayerSubscription> {
    const response = await fetch(`/api/catalogue/layers/subscriptions/${id}/`);
    return await response.json() as RawLayerSubscription;
  }

  public async getLayerSubscriptions (filter: RawLayerSubscriptionFilter): Promise<PaginatedRecord<RawLayerSubscription>> {
    const params = stripNullParams<RawLayerSubscriptionFilter>(filter);
    const response = await fetch("/api/catalogue/layers/subscriptions/?" + new URLSearchParams(params));
    return await response.json() as PaginatedRecord<RawLayerSubscription>;
  }

  public async getCatalogueEntry (id: number): Promise<RawCatalogueEntry> {
    const response = await fetch(`/api/catalogue/entries/${id}/`);
    return await response.json() as RawCatalogueEntry;
  }

  public async getCatalogueEntries (filter: RawCatalogueEntryFilter): Promise<PaginatedRecord<RawCatalogueEntry>> {
    const params = stripNullParams<RawCatalogueEntryFilter>(filter);
    const response = await fetch("/api/catalogue/entries/?" + new URLSearchParams(params) );
    return await response.json() as PaginatedRecord<RawCatalogueEntry>;
  }

  public async getLayerSubmission (id: number): Promise<RawLayerSubmission> {
    const response = await fetch(`/api/catalogue/entries/layers/submissions/${id}/`);
    return await response.json() as RawLayerSubmission;
  }

  public async getLayerSubmissions (filter: RawLayerSubmissionFilter): Promise<PaginatedRecord<RawLayerSubmission>> {
    const params = stripNullParams<RawCatalogueEntryFilter>(filter);
    const response = await fetch("/api/catalogue/layers/submissions/?" + new URLSearchParams(params) );
    return await response.json() as PaginatedRecord<RawLayerSubmission>;
  }

  public async getStatus<T> (statusType: StatusType, statusId: number): Promise<RecordStatus<T>> {
    const response = await fetch(`/api/catalogue/${statusType}/status/${statusId}`);
    return await response.json() as RecordStatus<T>;
  }

  public async getStatuses<T> (statusType: StatusType): Promise<PaginatedRecord<RecordStatus<T>>> {
    const response = await fetch(`/api/catalogue/${statusType}/status/`);
    return await response.json() as PaginatedRecord<RecordStatus<T>>;
  }

  public async getUser (userId: number): Promise<RawUser> {
    const response = await fetch(`/api/accounts/users/${userId}/`);
    return await response.json() as RawUser;
  }

  public async getUsers (filter: RawUserFilter): Promise<PaginatedRecord<RawUser>> {
    const params = stripNullParams<RawUserFilter>(filter);
    const response = await fetch("/api/accounts/users/?" + new URLSearchParams(params));
    return await response.json() as PaginatedRecord<RawUser>;
  }

  public async getMe (): Promise<RawUser> {
    const response = await fetch('/api/accounts/users/me/');
    return await response.json() as RawUser;
  }

  public async getNotifications (notificationType: NotificationRequestType): Promise<PaginatedRecord<RawNotification>> {
    const notificationTypePath = notificationType === NotificationRequestType.Email ? "emails" : "webhooks";
    const response = await fetch(`/api/catalogue/notifications/${notificationTypePath}/`);
    return await response.json() as PaginatedRecord<RawNotification>;
  }

  public async getNotificationTypes (notificationType: NotificationRequestType): Promise<PaginatedRecord<NotificationType>> {
    const notificationTypePath = notificationType === NotificationRequestType.Email ? "emails" : "webhooks";
    const response = await fetch(`/api/catalogue/notifications/${notificationTypePath}/type/`);
    return await response.json() as PaginatedRecord<NotificationType>;
  }

  public async getRawSymbology (id: number): Promise<RawSymbology> {
    const response = await fetch(`/api/catalogue/entry/symbologies/${id}`);
    return await response.json() as RawSymbology;
  }

  public async getRawSymbologies (): Promise<PaginatedRecord<RawSymbology>> {
    const response = await fetch("/api/catalogue/entry/symbologies/");
    return await response.json() as PaginatedRecord<RawSymbology>;
  }

  public async getRawAttribute (id: number): Promise<RawAttribute> {
    const response = await fetch(`/api/catalogue/layers/attribute/${id}/`);
    return await response.json() as RawAttribute;
  }

  public async getRawAttributes (): Promise<PaginatedRecord<RawAttribute>> {
    const response = await fetch("/api/catalogue/layers/attribute/");
    return await response.json() as PaginatedRecord<RawAttribute>;
  }

  public async getRawMetadata (id: number): Promise<RawMetadata> {
    const response = await fetch(`/api/catalogue/layers/metadata/${id}/`);
    return await response.json() as RawMetadata;
  }

  public async getRawMetadataList (): Promise<PaginatedRecord<RawMetadata>> {
    const response = await fetch("/api/catalogue/layers/metadata/");
    return await response.json() as PaginatedRecord<RawMetadata>;
  }

  public async getRawCustodian (id: number): Promise<RawCustodian> {
    const response = await fetch(`/api/catalogue/layers/custodians/${id}/`);
    return await response.json() as RawCustodian;
  }

  public async getRawCustodians (): Promise<PaginatedRecord<RawCustodian>> {
    const response = await fetch("/api/catalogue/layers/custodians/");
    return await response.json() as PaginatedRecord<RawCustodian>;
  }

  public async getGroup (id: number): Promise<Group> {
    const response = await fetch(`/api/accounts/groups/${id}/`);
    return await response.json() as Group;
  }

  public async getGroups (): Promise<PaginatedRecord<Group>> {
    const response = await fetch("/api/accounts/groups/");
    return await response.json() as PaginatedRecord<Group>;
  }

  public async patchCatalogueEntry (entryId: number, updatedEntry: RawEntryPatch): Promise<RawCatalogueEntry> {
    const params = stripNullParams(updatedEntry);
    const response = await fetcher(`/api/catalogue/entries/${entryId}/`, {
      method: "patch",
      body: JSON.stringify(params)
    });
    return await response.json() as RawCatalogueEntry;
  }

  public async lock (entryId: number) {
    const response = await fetcher(`/api/catalogue/entries/${entryId}/lock/`, {
      method: "post",
      body: JSON.stringify({ id: entryId })
    });
    return response.status;
  }

  public async unlock (entryId: number) {
    const response = await fetcher(`/api/catalogue/entries/${entryId}/unlock/`, {
      method: "post",
      body: JSON.stringify({ id: entryId })
    });
    return response.status;
  }

  public async entryAssign (entryId: number, userId: number) {
    const response = await fetcher(`/api/catalogue/entries/${entryId}/assign/${userId}/`, {
      method: "post"
    });
    return response.status;
  }

  public async entryUnassign (entryId: number) {
    const response = await fetcher(`/api/catalogue/entries/${entryId}/unassign/`, {
      method: "post"
    });
    return response.status;
  }
}
