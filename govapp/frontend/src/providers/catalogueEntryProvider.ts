import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { PaginatedRecord, RawCatalogueEntryFilter } from "../backend/backend.api";
import { CatalogueEntry, CatalogueEntryFilter } from "./catalogueEntryProvider.api";

export class CatalogueEntryProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === 'mock' ? new BackendServiceStub() : new BackendService();

  public async fetchCatalogueEntries ({ custodian, status, assignedTo, updateFrom, updateTo }: CatalogueEntryFilter):
    Promise<PaginatedRecord<CatalogueEntry>>{

    const rawFilter = {
      custodian,
      status,
      assigned_to: assignedTo,
      updated_before: updateTo,
      updated_after: updateFrom
    } as RawCatalogueEntryFilter;

    const { previous, next, count, results } = await this.backend.getCatalogueEntries(rawFilter);

    const catalogueEntries = results.map(entry => ({
      id: entry.id,
      name: entry.name,
      description: entry.description,
      status: entry.status,
      updatedAt: entry.updated_at,
      custodian: entry.custodian,
      assignedTo: entry.assigned_to,
      subscription: entry.subscription,
      activeLayer: entry.active_layer,
      layers: entry.layers,
      emailNotifications: entry.email_notifications,
      webhookNotifications: entry.webhook_notifications
    })) as Array<CatalogueEntry>;

   return { previous, next, count, results: catalogueEntries } as PaginatedRecord<CatalogueEntry>;
  }

}
