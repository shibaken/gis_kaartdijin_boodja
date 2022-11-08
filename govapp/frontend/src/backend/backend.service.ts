import { RecordStatus, RawCatalogueEntryFilter, RawCatalogueEntry, RawLayerSubscription,
  RawLayerSubscriptionFilter, RawUserFilter, RawLayerSubmissionFilter, RawLayerSubmission } from "./backend.api";
import type { PaginatedRecord, Params, StatusType, User } from "./backend.api";

export function stripNullParams<T extends object> (filter: T): Params {
  return Object.fromEntries(
    Object.entries(filter)
      .filter(([, value]) => {
        return value != null;
      })
  );
}

export class BackendService {
  public async getLayerSubscriptions (filter: RawLayerSubscriptionFilter): Promise<PaginatedRecord<RawLayerSubscription>> {
    const params = stripNullParams<RawLayerSubscriptionFilter>(filter);
    const response = await fetch("/api/catalogue/layers/subscriptions/?" + new URLSearchParams(params));
    return await response.json() as PaginatedRecord<RawLayerSubscription>;
  }

  public async getCatalogueEntries (filter: RawCatalogueEntryFilter): Promise<PaginatedRecord<RawCatalogueEntry>> {
    const params = stripNullParams<RawCatalogueEntryFilter>(filter);
    const response = await fetch("/api/catalogue/entries/?" + new URLSearchParams(params) );
    return await response.json() as PaginatedRecord<RawCatalogueEntry>;
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

  public async getUser (userId: number): Promise<User> {
    const response = await fetch(`/api/accounts/users/${userId}/`);
    return await response.json() as User;
  }

  public async getUsers (filter: RawUserFilter): Promise<PaginatedRecord<User>> {
    const params = stripNullParams<RawUserFilter>(filter);
    const response = await fetch("/api/accounts/users/?" + new URLSearchParams(params));
    return await response.json() as PaginatedRecord<User>;
  }
}
