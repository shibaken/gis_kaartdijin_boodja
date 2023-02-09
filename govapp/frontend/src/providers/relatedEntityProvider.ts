import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { Attribute, Symbology } from "./relatedEntityProvider.api";
import { Group, PaginatedRecord, RawAttribute, RawSymbology } from "../backend/backend.api";
import { catalogueEntryProvider } from "./catalogueEntryProvider";
import { WMTSCapabilities } from "ol/format";
import { optionsFromCapabilities } from "ol/source/WMTS";
import type { Options } from "ol/source/WMTS";
import { Workspace } from "./catalogueEntryProvider.api";

export class RelatedEntityProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();

  public async fetchAttributes (entryIds: Array<number>): Promise<Attribute[]> {
    const { results } = await this.backend.getRawAttributes({ catalogue_entry__in: entryIds });
    const linkedEntries = await catalogueEntryProvider.getOrFetchList(results.map(({ id }) => id));

    return results.map((rawAttribute) => {
      const linkedEntry = linkedEntries.find(record => record.id === rawAttribute.catalogue_entry);
      return {
        id: rawAttribute.id,
        name: rawAttribute.name,
        type: rawAttribute.type,
        order: rawAttribute.order,
        catalogueEntry: linkedEntry
      } as Attribute;
    }) as Array<Attribute>;
  }

  private toRawAttribute (attribute: Partial<Attribute>): Partial<RawAttribute> {
    const rawAttribute = {
      name: attribute.name,
      type: attribute.type,
      order: attribute.order,
      catalogue_entry: attribute.catalogueEntry?.id
    } as Partial<RawAttribute>;
    if (attribute.id) {
      rawAttribute.id = attribute.id;
    }

    return rawAttribute;
  };

  private toNewRawAttribute (attribute: Omit<Attribute, "id">): Omit<RawAttribute, "id"> {
    return this.toRawAttribute(attribute) as Omit<RawAttribute, "id">;
  }

  public async createAttribute (attribute: Partial<Attribute>): Promise<Attribute> {
    let preparedAttribute: Omit<Attribute, "id">;

    if (attribute.id) {
      preparedAttribute = Object.fromEntries(Object.entries(attribute)
        .filter(([_, value]) => value !== "id")) as Omit<Attribute, "id">;
    } else {
      preparedAttribute = attribute as Omit<Attribute, "id">;
    }

    const rawAttribute = await this.backend.postRawAttribute(this.toNewRawAttribute(preparedAttribute));
    return {
      id: rawAttribute.id,
      name: rawAttribute.name,
      type: rawAttribute.type,
      order: rawAttribute.order,
      catalogueEntry: preparedAttribute.catalogueEntry
    } as Attribute;
  }

  public async updateAttribute (attribute: Partial<Attribute>) {
    let preparedAttribute: Omit<Attribute, "id">;
    const id = attribute.id;

    if (id) {
      preparedAttribute = Object.fromEntries(Object.entries(attribute)
        .filter(([_, value]) => value !== "id")) as Omit<Attribute, "id">;
    } else {
      throw new Error("`updateAttribute`: Tried to update attribute without providing an ID");
    }

    const rawAttribute = await this.backend.patchRawAttribute(this.toNewRawAttribute(preparedAttribute), id);
    /* This should be the same as `preparedAttribute`, but for consistency and capturing possible errors, convert and
     * return what the API hands back.
     */
    return {
      id: rawAttribute.id,
      name: rawAttribute.name,
      type: rawAttribute.type,
      order: rawAttribute.order,
      catalogueEntry: preparedAttribute.catalogueEntry
    } as Attribute;
  }

  public async removeAttribute (id: number) {
    const responseCode = await this.backend.deleteAttribute(id);
    return responseCode >= 200 && responseCode < 300;
  }

  public async fetchSymbology (entryId: number): Promise<Symbology | undefined> {
    const rawSymbology: RawSymbology | undefined = await this.backend.getRawSymbology(entryId);
    return !rawSymbology ?
      undefined :
      {
        id: rawSymbology.id,
        name: rawSymbology.name,
        sld: rawSymbology.sld,
        catalogueEntry: await catalogueEntryProvider.getOrFetch(entryId)
      } as Symbology;
  }

  private async toSymbology(rawSymbology: RawSymbology): Promise<Symbology> {
    return {
      id: rawSymbology.id,
      name: rawSymbology.name,
      sld: rawSymbology.sld,
      catalogueEntry: await catalogueEntryProvider.getOrFetch(rawSymbology.catalogue_entry)
    } as Symbology;
  }

  public async updateSymbology (id: number, sld: string): Promise<Symbology> {
    return this.toSymbology(await this.backend.patchRawSymbology(id, sld));
  }

  public async fetchWmtsCapabilities (workspace: Workspace, layerName: string, styleName = "default"): Promise<Options | null> {
    const parser = new WMTSCapabilities();
    const text = await this.backend.getWmtsCapabilities();
    const result = parser.read(text);
    return optionsFromCapabilities(result, {
      layer: `${workspace.name}:` + layerName,
      style: `${workspace.name}:` + styleName
    });
  }

  public async getGroups (): Promise<PaginatedRecord<Group>> {
    const response = await fetch("/api/accounts/groups/");
    return await response.json() as PaginatedRecord<Group>;
  }
}

export const relatedEntityProvider = new RelatedEntityProvider();
