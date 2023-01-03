import { SortDirection } from "../components/viewState.api";

export interface PaginationFilter extends Record<string, unknown> {
  offset?: number;
  limit?: number;
  sortBy?: { column: string, direction: SortDirection };
}

export interface RecordMeta {
  total: number;
}