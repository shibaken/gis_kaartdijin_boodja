import { CatalogueEntryStatus, LayerSubscriptionStatus, RecordStatus } from "../backend/backend.api";

// Raw records, currently placeholders and subject to change
export interface LayerSubscription {
  id: number;
  name: string;
  url: string;
  frequency: string;
  status: RecordStatus<LayerSubscriptionStatus>;
  subscribedDate: string;
  subscribedTime: string;
  catalogueEntry: number;
}

export interface CatalogueEntry {
  number: string;
  name: string;
  custodian: string;
  status: RecordStatus<CatalogueEntryStatus>;
  lastUpdated: string;
  time: string;
  assignedTo: string;
  description: string;
}

export interface PaginationFilter extends Map<string, unknown> {
  offset?: number;
  limit?: number;
}

export interface LayerSubscriptionFilter extends PaginationFilter {
  status?: number;
  subscribedFrom?: string;
  subscribedTo?: string;
}

export interface CatalogueEntryFilter extends PaginationFilter {
  custodian?: string;
  status?: string;
  assignedTo?: string;
}
