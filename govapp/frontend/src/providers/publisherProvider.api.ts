// Publish

import { CatalogueEntry } from "./catalogueEntryProvider.api";
import { PaginationFilter } from "./providerCommon.api";
import { PublishEntryStatus, RawPublishEntry, RecordStatus, User } from "../backend/backend.api";
import { SortDirection } from "../components/viewState.api";

export interface CddpPublishChannel {
  id: string;
  name: string;
  description: string;
  format: number;
  mode: number;
  frequency: number;
  path: string;
  publishEntryId: number;
}

export interface GeoserverPublishChannel {
  id: number;
  name: number;
  description: number;
  mode: number;
  frequency: number;
  workspace: number;
  publishEntryId: number;
}


export interface PublishEntry {
  id: number;
  name: string;
  description: string;
  status: RecordStatus<PublishEntryStatus>;
  updatedAt: string;
  publishedAt: string;
  editors: Array<User>;
  assignedTo: User;
  catalogueEntry: CatalogueEntry;
  cddpChannel: CddpPublishChannel;
  geoserverChannel: GeoserverPublishChannel;
}

export interface PublishEntryFilter extends PaginationFilter {
  ids?: Array<number>;
  search?: string;
  status?: string;
  updatedBefore?: string;
  updatedAfter?: string;
  assignedTo?: string;
  sortBy?: { column: keyof RawPublishEntry, direction: SortDirection };
}
