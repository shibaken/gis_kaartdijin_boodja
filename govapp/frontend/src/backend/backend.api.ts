export interface PaginatedRecord<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: Array<T>;
}

export type Params = Record<string, string>

// Raw records, currently placeholders and subject to change
export interface RawLayerSubscription {
  id: number;
  name: string;
  url: string;
  frequency: string;
  status: number;
  subscribed_at: string;
  catalogue_entry: number;
}

export interface RawCatalogueEntry {
  id: number;
  name: string;
  description: string;
  status: number;
  updated_at: string;
  custodian: number | null;
  assigned_to: number | null;
  subscription: number;
  active_layer: number;
  layers: Array<number>;
  email_notifications: Array<number>;
  webhook_notifications: Array<number>;
}

export interface RawLayerSubmission {
  id: number;
  name: string;
  description: string;
  file: string;
  status: number;
  submitted_at: string;
  catalogue_entry: number;
  attributes: Array<number>;
  metadata: number;
  symbology: number;
}

export interface RawPaginationFilter extends Record<string, unknown> {
  offset?: number;
  limit?: number;
}

export interface RawLayerSubscriptionFilter extends RawPaginationFilter {
  status?: string;
  subscribed_before?: string;
  subscribed_after?: string;
}

export interface RawCatalogueEntryFilter extends RawPaginationFilter {
  id__in?: Array<number>;
  status?: string;
  custodian?: string;
  assigned_to?: string;
  updated_before?: string;
  updated_after?: string;
}

export interface RawLayerSubmissionFilter extends RawPaginationFilter {
  status?: string;
  submitted_before?: string;
  submitted_after?: string;
}

export interface RawUserFilter extends RawPaginationFilter {
  username__in?: Array<string>;
  id__in?: Array<number>;
}

export interface PaginationState {
  currentPage: number;
  numPages: number;
  pageLength: number;
  total: number;
}

export interface RecordStatus<T> {
  id: number;
  label: T | "Status not found";
}

export type StatusType = "entries"|"layers/submissions"|"layers/subscriptions";
export type LayerSubscriptionStatus = "Active"|"Disabled";
export type CatalogueEntryStatus = "Draft"|"Locked"|"Cancelled";
export type LayerSubmissionStatus = "Submitted"|"Accepted"|"Declined";

export interface User {
  id: number;
  username: string;
  groups: Array<number>;
}
