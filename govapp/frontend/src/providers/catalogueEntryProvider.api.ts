import { PaginationFilter } from "./providerCommon.api";
import { CatalogueEntryStatus, RawCatalogueEntry, RecordStatus, User } from "../backend/backend.api";
import { SortDirection } from "../components/viewState.api";
import { Custodian } from "./userProvider.api";
import { Metadata } from "./relatedEntityProvider.api";

export interface CatalogueEntry {
  id: number;
  name: string;
  description: string;
  status: RecordStatus<CatalogueEntryStatus>;
  createdAt: string;
  updatedAt: string;
  custodian: Custodian;
  assignedTo?: User;
  subscription: number;
  activeLayer: number;
  layers: Array<number>;
  emailNotifications: Array<number>;
  webhookNotifications: Array<number>;
  editors: Array<User>;
  workspace: Workspace;
  metadata: Metadata;
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

export interface Workspace {
  id: number,
  name: string
}