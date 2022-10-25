export type LayerSubscriptionStatus = 'active'|'disabled';

// Raw records, currently placeholders and subject to change
export interface LayerSubscription {
  id: number
  name: string
  url: string
  frequency: string
  status: number
  subscribedDate: string
  subscribedTime: string
  catalogueEntry: number
}

export interface CatalogueEntry {
  number: string
  name: string
  custodian: string
  status: LayerSubscriptionStatus
  lastUpdated: string
  time: string
  assignedTo: string
  description: string
}

export interface PaginationFilter extends Map<string, any> {
  offset?: number
  limit?: number
}

export interface LayerSubscriptionFilter extends PaginationFilter {
  status?: number
  subscribedFrom?: string
  subscribedTo?: string
}

export interface CatalogueEntryFilter extends PaginationFilter {
  custodian?: string
  status?: string
  assignedTo?: string
}
