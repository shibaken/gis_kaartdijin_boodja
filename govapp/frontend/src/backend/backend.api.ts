export interface PaginatedRecord<T> {
  count: number
  next: string | null
  previous: string | null
  results: Array<T>
}

export type Params = Record<string, string>

// Raw records, currently placeholders and subject to change
export interface RawLayerSubscription {
  id: number
  name: string
  url: string
  frequency: string
  status: number
  subscribed_at: string
  catalogue_entry: number
}

export interface RawCatalogueEntry {
  id: number
  name: string
  description: string
  status: number
  updated_at: string
  custodian: number | null
  assigned_to: number | null
  subscription: number
  active_layer: number
  layers: Array<number>
  email_notifications: Array<number>
  webhook_notifications: Array<number>
}

export interface PaginationFilter extends Map<string, any> {
  offset?: number
  limit?: number
}

export interface RawLayerSubscriptionFilter extends PaginationFilter {
  status?: string
  subscribed_before?: string
  subscribed_after?: string
}

export interface RawCatalogueEntryFilter extends PaginationFilter {
  status?: string
  custodian?: string
  assigned_to?: string
  updated_before?: string
  updated_after?: string
}

export interface PaginationState {
  currentPage: number
  numPages: number
  pageLength: number
  total: number
}

export interface RecordStatus {
  id: number
  label: 'Draft'|'Locked'|'Cancelled'
}
