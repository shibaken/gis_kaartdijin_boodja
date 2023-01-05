import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { Attribute } from "./relatedEntityProvider.api";
import {
  EntryPatch,
  Group,
  PaginatedRecord,
  RawAttribute,
  RawCustodian,
  RawMetadata,
  RawSymbology
} from "../backend/backend.api";
import { catalogueEntryProvider } from "./catalogueEntryProvider";

export class RelatedEntityProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();

  public async fetchAttributes (entryIds: Array<number>): Promise<Attribute[]> {
    const { results } = await this.backend.getRawAttributes({ catalogue_entry__in: entryIds });
    const { getOrFetchList } = catalogueEntryProvider;
    const linkedEntries = await getOrFetchList(results.map(({ id }) => id));

    return results.map((rawAttribute) => {
      const linkedEntry = linkedEntries.find(record => record.id === rawAttribute.catalogue_entry);
      return {
        id: rawAttribute.id,
        name: rawAttribute.name,
        description: rawAttribute.description,
        type: rawAttribute.type,
        order: rawAttribute.order,
        catalogueEntry: linkedEntry
      } as Attribute;
    }) as Array<Attribute>;
  }

  public async getRawSymbologies (): Promise<PaginatedRecord<RawSymbology>> {
    const response = await fetch("/api/catalogue/entry/symbologies/");
    return await response.json() as PaginatedRecord<RawSymbology>;
  }

  public async getRawAttributes (): Promise<PaginatedRecord<RawAttribute>> {
    const response = await fetch("/api/catalogue/layers/attribute/");
    return await response.json() as PaginatedRecord<RawAttribute>;
  }

  public async getRawMetadataList (): Promise<PaginatedRecord<RawMetadata>> {
    const response = await fetch("/api/catalogue/layers/metadata/");
    return await response.json() as PaginatedRecord<RawMetadata>;
  }

  public async getRawCustodians (): Promise<PaginatedRecord<RawCustodian>> {
    const response = await fetch("/api/catalogue/layers/custodians/");
    return await response.json() as PaginatedRecord<RawCustodian>;
  }

  public async getGroups (): Promise<PaginatedRecord<Group>> {
    const response = await fetch("/api/accounts/groups/");
    return await response.json() as PaginatedRecord<Group>;
  }

  public async updateCatalogueEntry (entryId: number, { description, custodian, assignedTo }: EntryPatch) {
    return await this.backend.patchCatalogueEntry(entryId, {
      description,
      custodian: custodian?.id,
      assigned_to: assignedTo?.id
    });
  }
}

export const relatedEntityProvider = new RelatedEntityProvider();
