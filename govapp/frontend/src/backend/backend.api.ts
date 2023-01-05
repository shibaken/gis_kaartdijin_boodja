import { CatalogueEntry } from "../providers/catalogueEntryProvider.api";

export interface PaginatedRecord<T> {
  count: number;
  next?: string | null;
  previous?: string | null;
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
  custodian?: number;
  assigned_to?: number;
  subscription: number;
  active_layer: number;
  layers: Array<number>;
  email_notifications: Array<number>;
  webhook_notifications: Array<number>;
  editors: Array<number>;
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

export interface RawUser {
  id: number;
  username: string;
  groups: Array<number>;
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
  status?: number;
  custodian?: string;
  assigned_to?: string;
  updated_before?: string;
  updated_after?: string;
}

export interface RawLayerSubmissionFilter extends RawPaginationFilter {
  status?: number;
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
  groups: Array<Group>;
}

export enum NotificationRequestType {
  Email,
  Webhook,
}

export interface RawNotification {
  id: number;
  name: string;
  type: number;
  catalogue_entry: number;
  email?: string
  url?: string
}

export type RawEmailNotification = RawNotification;
export type RawWebhookNotification = RawNotification;

export interface NotificationType {
  id: number;
  label: string;
}

export interface RawSymbology {
  id: number;
  name: string;
  sld: string;
  catalogue_entry: number;
}

export interface RawAttribute {
  id: number;
  name: string;
  description?: string;
  type: string;
  order: number;
  catalogue_entry: number;
}

export interface RawMetadata {
  id:	number;
  name:	string;
  created_at:	string;
  catalogue_entry: number;
}

export interface RawCustodian {
  id:	number;
  name:	string;
  description?: string;
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface Group {
  id: number;
  name: string;
}

export interface RawCommunicationLogDocument {
  id: number;
  name?: string;
  description?: string;
  uploaded_at: string
  file: string;
}

export interface RawCommunicationLog {
  id: number;
  created_at: string;
  type: number;
  to?: string;
  cc?: string;
  from: string;
  subject?: string;
  text?: string;
  documents: Array<RawCommunicationLogDocument>;
  user?: number;
}

/**
 * Update types
 */
export type RawEntryPatch = Pick<RawCatalogueEntry, "description" | "custodian" | "assigned_to">;
export type EntryPatch = Pick<CatalogueEntry, "description" | "custodian" | "assignedTo">;