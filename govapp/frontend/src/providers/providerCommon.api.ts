export interface PaginationFilter extends Map<string, unknown> {
  offset?: number
  limit?: number
}

export type SelectedTab = "Catalogue Entries" | "Layer Submissions" | "Layer Subscriptions";