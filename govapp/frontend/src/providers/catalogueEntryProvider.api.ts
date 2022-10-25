import { PaginationFilter } from "./providerCommon.api";

export type CatalogueStatus = 'Locked'|'Draft'|'Cancelled';

export interface CatalogueEntry {
  id: number
  name: string
  description: string
  status: number
  updatedAt: string
  custodian: number
  assignedTo: number
  subscription: number
  activeLayer: number
  layers: Array<number>
  emailNotifications: Array<number>
  webhookNotifications: Array<number>
}

export interface CatalogueEntryFilter extends PaginationFilter {
  custodian?: string
  status?: string
  assignedTo?: string
  updateFrom?: string
  updateTo?: string
}
