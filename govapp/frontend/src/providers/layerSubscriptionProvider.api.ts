import { LayerSubscriptionStatus, RecordStatus } from "../backend/backend.api";
import { PaginationFilter } from "./providerCommon.api";

// Raw records, currently placeholders and subject to change
export interface LayerSubscription {
  id: number;
  name: string;
  url: string;
  frequency: string;
  status: RecordStatus<LayerSubscriptionStatus>;
  subscribedDate: string;
  subscribedTime: string;
  catalogueEntry: number;
}

export interface LayerSubscriptionFilter extends PaginationFilter {
  status?: number;
  subscribedFrom?: string;
  subscribedTo?: string;
}
