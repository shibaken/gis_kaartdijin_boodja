import { Group, NotificationRequestType, NotificationType, RawAttribute, RawCatalogueEntry, RawCatalogueEntryFilter,
  RawCustodian, RawLayerSubmission, RawLayerSubmissionFilter, RawLayerSubscription, RawLayerSubscriptionFilter,
  RawMetadata, RawNotification, RawSymbology, RawUserFilter, RecordStatus, RawEntryPatch, RawUser, RawCommunicationLog,
  RawPaginationFilter, RawAttributeFilter, RawNotificationFilter, RawCddpPublishChannel, RawGeoserverPublishChannel,
  RawPublishEntry, RawPublishEntryFilter } from "./backend.api";
import { CommunicationLogType } from "../providers/logsProvider.api";
import type { PaginatedRecord, Params, StatusType } from "./backend.api";
import { Workspace } from "../providers/catalogueEntryProvider.api";
import { PaginationFilter } from "../providers/providerCommon.api";

const GEOSERVER_URL = import.meta.env.VITE_GEOSERVER_URL;

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

export function stripNullParams<T extends object> (params: T): Params {
  return Object.fromEntries(
    Object.entries(params)
      .filter(([_, value]) => {
        return value != null;
      })
  );
}

/*
 * Replaces nulls with empty strings in order to retain the values when patching
 */
export function replaceNullParams<T extends object> (params: T): Params {
  const updatedWithNulls = Object.fromEntries(
    Object.entries(params)
      .map(([key, value]) => {
        const mappedValue = typeof value === "undefined" ? "" : value;
        return [key, mappedValue];
      })
  );

  return updatedWithNulls as Params;
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
    const response = await fetch(`/api/catalogue/catalogue/layers/submissions/${id}/`);
    return await response.json() as RawLayerSubmission;
  }

  public async getLayerSubmissions (filter: RawLayerSubmissionFilter): Promise<PaginatedRecord<RawLayerSubmission>> {
    const params = stripNullParams<RawCatalogueEntryFilter>(filter);
    const response = await fetch("/api/catalogue/layers/submissions/?" + new URLSearchParams(params) );
    return await response.json() as PaginatedRecord<RawLayerSubmission>;
  }

  public async getStatus<T> (statusType: StatusType, statusId: number): Promise<RecordStatus<T>> {
    const response = await fetch(`/api/${statusType}/status/${statusId}`);
    return await response.json() as RecordStatus<T>;
  }

  public async getStatuses<T> (statusType: StatusType): Promise<PaginatedRecord<RecordStatus<T>>> {
    const response = await fetch(`/api/${statusType}/status/`);
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

  public async getNotifications (notificationType: NotificationRequestType, filter: RawNotificationFilter):
      Promise<PaginatedRecord<RawNotification>> {
    const notificationTypePath = notificationType === NotificationRequestType.Email ? "emails" : "webhooks";
    const params = stripNullParams<RawNotificationFilter>(filter);
    const response = await fetch(`/api/catalogue/notifications/${notificationTypePath}/`, params);
    return await response.json() as PaginatedRecord<RawNotification>;
  }

  public async getNotificationTypes (notificationType: NotificationRequestType): Promise<PaginatedRecord<NotificationType>> {
    const notificationTypePath = notificationType === NotificationRequestType.Email ? "emails" : "webhooks";
    const response = await fetch(`/api/catalogue/notifications/${notificationTypePath}/type/`);
    return await response.json() as PaginatedRecord<NotificationType>;
  }

  protected async modifyNotification(notificationType: NotificationRequestType,
      notification: Partial<Omit<RawNotification, "id">>, method: "patch" | "post", id?: number): Promise<RawNotification> {
    if (!id && method === "patch") {
      throw new Error("`patchRawNotification`: Tried to patch an notification without providing an ID");
    }

    const response = await fetcher(`/api/catalogue/notifications/${notificationType}/${id ? `${id}/` : ""}`, {
      method,
      body: JSON.stringify(notification)
    });
    return await response.json() as RawNotification;
  }

  public async patchRawNotification (notificationType: NotificationRequestType,
      notification: Partial<Omit<RawNotification, "id">>, id?: number): Promise<RawNotification> {
    return this.modifyNotification(notificationType, notification, "patch", id);
  }

  public async postRawNotification (notificationType: NotificationRequestType,
      notification: Omit<RawNotification, "id">): Promise<RawNotification> {
    return this.modifyNotification(notificationType, notification, "post");
  }

  public async deleteNotification (notificationType: NotificationRequestType, id: number): Promise<number> {
    const response = await fetcher(`/api/catalogue/notifications/${notificationType}/${id}`, {
      method: 'delete'
    });

    return response.status;
  }

  public async getRawSymbology (entryId: number): Promise<RawSymbology> {
    const params: Params = { catalogue_entry: entryId.toString() };
    const response = await fetch("/api/catalogue/layers/symbologies/?" + new URLSearchParams(params));
    return (await response.json()).results[0] as RawSymbology;
  }

  protected async modifyRawSymbology (body: string | Omit<RawSymbology, "id">, method: "patch" | "post", id?: number): Promise<RawSymbology> {
    if (!id && method === "patch") {
      throw new Error("`patchRawSymbology`: Tried to patch a symbology without providing an ID");
    }
    const response = await fetcher(`/api/catalogue/layers/symbologies/${id ? `${id}/` : ""}`, {
      method,
      body: JSON.stringify(typeof body === "string" ? { sld: body } : body)
    });
    return await response.json();
  }

  public async patchRawSymbology (id: number, sld: string): Promise<RawSymbology> {
    return this.modifyRawSymbology(sld, "patch", id);
  }

  public async getRawAttribute (id: number): Promise<RawAttribute> {
    const response = await fetch(`/api/catalogue/layers/attribute/${id}/`);
    return await response.json() as RawAttribute;
  }

  public async getRawAttributes (filter: RawAttributeFilter): Promise<PaginatedRecord<RawAttribute>> {
    const params = stripNullParams<RawCatalogueEntryFilter>(filter);
    const response = await fetch("/api/catalogue/layers/attributes/?" + new URLSearchParams(params));
    return await response.json() as PaginatedRecord<RawAttribute>;
  }

  protected async modifyAttribute(attribute: Partial<Omit<RawAttribute, "id">>, method: "patch" | "post", id?: number): Promise<RawAttribute> {
    if (!id && method === "patch") {
      throw new Error("`patchRawAttrute`: Tried to patch an attribute without providing an ID");
    }

    const response = await fetcher(`/api/catalogue/layers/attributes/${id ? `${id}/` : ""}`, {
      method,
      body: JSON.stringify(attribute)
    });
    return await response.json() as RawAttribute;
  }

  public async patchRawAttribute (attribute: Partial<Omit<RawAttribute, "id">>, id?: number): Promise<RawAttribute> {
    return this.modifyAttribute(attribute, "patch", id);
  }

  public async postRawAttribute (attribute: Omit<RawAttribute, "id">): Promise<RawAttribute> {
    return this.modifyAttribute(attribute, "post");
  }

  public async deleteAttribute (id: number): Promise<number> {
    const response = await fetcher(`/api/catalogue/layers/attributes/${id}`, {
      method: 'delete'
    });

    return response.status;
  }
  public async getRawMetadata (id: number): Promise<RawMetadata> {
    const response = await fetch(`/api/catalogue/layers/metadata/${id}/`);
    return await response.json() as RawMetadata;
  }

  public async getRawMetadataList (): Promise<PaginatedRecord<RawMetadata>> {
    const response = await fetch("/api/catalogue/layers/metadata/");
    return await response.json() as PaginatedRecord<RawMetadata>;
  }

  public async patchRawMetadata (metadata: Partial<Omit<RawMetadata, "id">>, id?: number): Promise<RawMetadata> {
    return this.modifyMetadata(metadata, "patch", id);
  }

  protected async modifyMetadata (metadata: Partial<Omit<RawMetadata, "id">>, method: "patch" | "post", id?: number): Promise<RawMetadata> {
    if (!id && method === "patch") {
      throw new Error("`patchRawMetadata`: Tried to patch a symbology without providing an ID");
    }
    const response = await fetcher(`/api/catalogue/layers/metadata/${id ? `${id}/` : ""}`, {
      method,
      body: JSON.stringify(metadata)
    });
    return await response.json();
  }

  public async getRawCustodian (id: number): Promise<RawCustodian> {
    const response = await fetch(`/api/catalogue/layers/custodians/${id}/`);
    return await response.json() as RawCustodian;
  }

  public async getRawCustodians (): Promise<PaginatedRecord<RawCustodian>> {
    const response = await fetch("/api/catalogue/custodians/");
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
    // Don't strip null params when patching potentially empty values
    const params = replaceNullParams(updatedEntry);

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

  public async decline (entryId: number) {
    const response = await fetcher(`/api/catalogue/entries/${entryId}/decline/`, {
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

  public async getCommunicationLogs (entryId: number, filter: RawPaginationFilter): Promise<PaginatedRecord<RawCommunicationLog>> {
    const params = stripNullParams(filter);
    const response = await fetch(`/api/catalogue/entries/${entryId}/logs/communications/?${new URLSearchParams(params)}`);
    return await response.json();
  }

  async createCommunicationLog(entryId: number, data: Omit<RawCommunicationLog, "id" | "documents">) {
    const response = await fetcher(`/api/catalogue/entries/${entryId}/logs/communications/`, {
      method: "post",
      body: JSON.stringify(data)
    });

    return response.status;
  }

  public async getActionsLogs (entryId: number) {
    const response = await fetch(`/api/catalogue/entries/${entryId}/logs/communications/`);
    return await response.json();
  }

  public async uploadCommunicationFile (entryId: number, logId: number, file: File) {
    const response = await fetcher(`/api/catalogue/entries/${entryId}/logs/communications/${logId}/file/`, {
      method: "post",
      body: file
    });
    return response.status;
  }

  public async getCommunicationTypes (): Promise<CommunicationLogType[]> {
    const response = await fetch("/api/logs/communications/type/");
    return (await response.json()).results;
  }

  public async getWorkspace(id: number): Promise<Workspace> {
    const response = await fetch(`/api/catalogue/workspaces/${id}`);
    return await response.json();
  }

  public async getWorkspaces(): Promise<PaginatedRecord<Workspace>> {
    const response = await fetch("/api/catalogue/workspaces/");
    return await response.json();
  }

  public async getWmtsCapabilities (): Promise<string> {
    const response = await fetch(`${GEOSERVER_URL}/geoserver/gwc/service/wmts?request=GetCapabilities`);
    return (await response.text());
  }

  public async getCddpPublishChannels (filter: PaginationFilter): Promise<PaginatedRecord<RawCddpPublishChannel>> {
    const params = stripNullParams<RawPublishEntryFilter>(filter);
    const response = await fetch(`/api/publish/channels/cddp/?` + new URLSearchParams(params));
    return await response.json();
  }

  public async getGeoserverPublishChannels (filter: PaginationFilter): Promise<PaginatedRecord<RawGeoserverPublishChannel>> {
    const params = stripNullParams<RawPublishEntryFilter>(filter);
    const response = await fetch(`/api/publish/channels/geoserver/?` + new URLSearchParams(params));
    return await response.json();
  }

  public async getPublishEntry (id: number): Promise<RawPublishEntry> {
    const response = await fetch(`/api/publish/entries/${id}/`);
    return await response.json();
  }

  public async getPublishEntries (filter: RawPublishEntryFilter): Promise<PaginatedRecord<RawPublishEntry>> {
    const params = stripNullParams<RawPublishEntryFilter>(filter);
    const response = await fetch(`/api/publish/entries/?` + new URLSearchParams(params));
    return await response.json();
  }
}
