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

export enum ViewMode {
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

export type CatalogueNavigateEmitsOptions = {
    viewTab?: CatalogueDetailViewTabs | SubmissionDetailViewTabs | SubscriptionDetailViewTabs,
    recordId: number
}

export type NavigationCatalogueEmits = (
  e: "navigate",
  tab: CatalogueTab,
  view: ViewMode,
  options?: CatalogueNavigateEmitsOptions
) => void;

export type NavigationPublishEmits = (
  e: "navigate",
  tab: PublishTab,
  view: ViewMode,
  options?: PublishNavigateEmitsOptions
) => void;

export enum SortDirection {
  Ascending = "ascending",
  Descending = "descending",
  None = "none"
}

// Publish

export enum PublishTab {
  PublishEntries = "Publish Entries"
}

export enum PublishDetailViewTabs {
  Details = "Details"
}

export type PublishNavigateEmitsOptions = {
  viewTab?: PublishDetailViewTabs,
  recordId: number
}
