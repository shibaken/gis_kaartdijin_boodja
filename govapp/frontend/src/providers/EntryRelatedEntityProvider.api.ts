import { CatalogueEntry } from "./catalogueEntryProvider.api";

export interface Symbology {
  id: number;
  name: string;
  sld: string;
  catalogueEntry: CatalogueEntry;
}

export interface Attribute {
  id: number;
  name: string;
  description?: string;
  type: string;
  order: number;
  catalogueEntry: Pick<CatalogueEntry, "id" | "name">;
}

export interface Metadata {
  id:	number;
  name:	string;
  createdAt:	string;
  catalogueEntry: CatalogueEntry;
}
