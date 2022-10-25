import { RecordStatus, RawCatalogueEntryFilter, RawCatalogueEntry, RawLayerSubscription,
  RawLayerSubscriptionFilter } from './backend.api';
import type { PaginatedRecord, Params } from './backend.api';

export function stripNullParams<T extends object> (filter: T): Params {
  return Object.fromEntries(
    Object.entries(filter)
      .filter(([key, value]) => {
        return value != null;
      })
  );
}

export class BackendService {
  public async getLayerSubscriptions(filter: RawLayerSubscriptionFilter): Promise<PaginatedRecord<RawLayerSubscription>> {
    const params = stripNullParams<RawLayerSubscriptionFilter>(filter);
    const response = await fetch(`/api/catalogue/layers/subscriptions/?` + new URLSearchParams(params));
    return await response.json() as PaginatedRecord<RawLayerSubscription>;
  }

  public async getCatalogueEntries(filter: RawCatalogueEntryFilter): Promise<PaginatedRecord<RawCatalogueEntry>> {
    const params = stripNullParams<RawCatalogueEntryFilter>(filter);
    const response = await fetch(`/api/catalogue/entries/?` + new URLSearchParams(params) );
    return await response.json() as PaginatedRecord<RawCatalogueEntry>;
  }

  public async getStatuses(): Promise<PaginatedRecord<RecordStatus>> {
    const response = await fetch(`/api/catalogue/entries/status/`);
    return await response.json() as PaginatedRecord<RecordStatus>;
  }
}
