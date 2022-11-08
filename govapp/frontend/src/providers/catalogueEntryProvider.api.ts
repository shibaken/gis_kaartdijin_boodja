import { PaginationFilter } from "./providerCommon.api";
import { CatalogueEntryStatus, RecordStatus, User } from "../backend/backend.api";

export interface CatalogueEntry {
  id: number;
  name: string;
  description: string;
  status: RecordStatus<CatalogueEntryStatus>;
  updatedAt: string;
  custodian: User;
  assignedTo: User;
  subscription: number;
  activeLayer: number;
  layers: Array<number>;
  emailNotifications: Array<number>;
  webhookNotifications: Array<number>;
}

export interface CatalogueEntryFilter extends PaginationFilter {
  ids?: Array<number>;
  custodian?: string;
  status?: string;
  assignedTo?: string;
  updateFrom?: string;
  updateTo?: string;
}
