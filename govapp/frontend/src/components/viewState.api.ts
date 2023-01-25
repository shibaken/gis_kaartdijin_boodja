export enum CatalogueTab {
  CatalogueEntries = "Catalogue Entries",
  LayerSubmissions = "Layer Submissions",
  LayerSubscriptions = "Layer Subscriptions"
}
export enum CatalogueDetailViewTabs {
  Details = "Details",
  AttributeTable = "Attribute Table",
  Symbology = "Symbology",
  Metadata = "Metadata"
}

export enum CatalogueView {
  List = "List",
  View = "View",
  Edit = "Edit"
}

export enum SubmissionDetailViewTabs {
  Details = "Details",
  Map = "Map"
}

export enum SubscriptionDetailViewTabs {
  Details = "Details",
  RelatedItems = "Related Items"
}

export type NavigateEmitsOptions = {
    viewTab?: CatalogueDetailViewTabs | SubmissionDetailViewTabs | SubscriptionDetailViewTabs,
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