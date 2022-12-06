import { LayerSubscriptionStatus, RecordStatus } from "../backend/backend.api";
import { PaginationFilter } from "./providerCommon.api";
import { CatalogueEntry } from "./catalogueEntryProvider.api";
import { SortDirection } from "../components/viewState.api";

// Raw records, currently placeholders and subject to change
export interface LayerSubscription {
  id: number;
  name: string;
  url: string;
  frequency: string;
  status: RecordStatus<LayerSubscriptionStatus>;
  subscribedDate: string;
  catalogueEntry: Pick<CatalogueEntry, "id" | "name">;
}

export interface LayerSubscriptionFilter extends PaginationFilter {
  status?: number;
  subscribedFrom?: string;
  subscribedTo?: string;
  sortBy?: { column: keyof CatalogueEntry, direction: SortDirection };
}
