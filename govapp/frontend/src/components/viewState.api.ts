export enum CatalogueTab {
  CatalogueEntries = "Catalogue Entries",
  LayerSubmissions = "Layer Submissions",
  LayerSubscriptions = "Layer Subscriptions"
}
export enum CatalogueDetailViewTabs {
  Details,
  AttributeTable,
  Symbology,
  Metadata
}
export enum CatalogueView {
  List,
  View,
  History
}

export enum SubscriptionDetailViewTabs {
  Details,
  RelatedItems
}

export type NavigateEmitsOptions = {
    viewTab?: CatalogueDetailViewTabs,
    recordId: number
}
export type NavigationEmits = (
  e: "navigate",
  tab: CatalogueTab,
  view: CatalogueView,
  options?: NavigateEmitsOptions
) => void;

export enum SortDirection {
  Ascending = "ascending",
  Descending = "descending",
  None = "none"
}