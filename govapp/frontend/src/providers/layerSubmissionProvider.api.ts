import { LayerSubmissionStatus, RecordStatus } from "../backend/backend.api";
import { PaginationFilter } from "./providerCommon.api";
import { CatalogueEntry } from "./catalogueEntryProvider.api";
import { SortDirection } from "../components/viewState.api";

// Raw records, currently placeholders and subject to change
export interface LayerSubmission {
  id: number;
  name: string;
  description: string;
  file: string;
  status: RecordStatus<LayerSubmissionStatus>;
  submittedDate: string;
  catalogueEntry: Pick<CatalogueEntry, "id" | "name">;
  attributes: Array<number>;
  metadata: number;
  symbology: number;
}

export interface LayerSubmissionFilter extends PaginationFilter {
  status?: number;
  submittedFrom?: string;
  submittedTo?: string;
  sortBy?: { column: keyof LayerSubmission, direction: SortDirection };
}
