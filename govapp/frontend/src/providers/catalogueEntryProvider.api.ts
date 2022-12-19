import { PaginationFilter } from "./providerCommon.api";
import { CatalogueEntryStatus, RawCatalogueEntry, RecordStatus, User } from "../backend/backend.api";
import { SortDirection } from "../components/viewState.api";

export interface CatalogueEntry {
  id: number;
  name: string;
  description: string;
  status: RecordStatus<CatalogueEntryStatus>;
  updatedAt: string;
  custodian: User;
  assignedTo?: User;
  subscription: number;
  activeLayer: number;
  layers: Array<number>;
  emailNotifications: Array<number>;
  webhookNotifications: Array<number>;
  editors: Array<User>
}

export interface CatalogueEntryFilter extends PaginationFilter {
  ids?: Array<number>;
  custodian?: string;
  status?: number;
  assignedTo?: string;
  updateFrom?: string;
  updateTo?: string;
  sortBy?: { column: keyof RawCatalogueEntry, direction: SortDirection };
}
