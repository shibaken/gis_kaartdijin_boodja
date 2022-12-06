import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { CatalogueEntryStatus, PaginatedRecord, RawCatalogueEntryFilter, User } from "../backend/backend.api";
import { CatalogueEntry, CatalogueEntryFilter } from "./catalogueEntryProvider.api";
import { StatusProvider } from "./statusProvider";
import { UserProvider } from "./userProvider";
import { UserFilter } from "./userProvider.api";
import { SortDirection } from "../components/viewState.api";
import { toSnakeCase } from "../util/strings";

export class CatalogueEntryProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();
  private statusProvider = new StatusProvider();
  private userProvider = new UserProvider();

  public async fetchCatalogueEntry (id: number): Promise<CatalogueEntry> {
    const entry = await this.backend.getCatalogueEntry(id);
    const entryStatuses = await this.statusProvider.fetchStatuses<CatalogueEntryStatus>("entries");
    let user: User | undefined;

    if (typeof entry.assigned_to === "number") {
      user = await this.userProvider.fetchUser(entry.assigned_to);
    }

    return {
      id: entry.id,
      name: entry.name,
      description: entry.description,
      status: this.statusProvider.getRecordStatusFromId(entry.status, entryStatuses),
      updatedAt: entry.updated_at,
      custodian: user, // TODO: update to work with new custodian API
      assignedTo: user,
      subscription: entry.subscription,
      activeLayer: entry.active_layer,
      layers: entry.layers,
      emailNotifications: entry.email_notifications,
      webhookNotifications: entry.webhook_notifications
    } as CatalogueEntry;
  }

  public async fetchCatalogueEntries ({ ids, custodian, status, assignedTo, updateFrom, updateTo, sortBy }: CatalogueEntryFilter):
      Promise<PaginatedRecord<CatalogueEntry>>{
    let sortString = "";
    if (sortBy && sortBy.column) {
      if (sortBy.direction === SortDirection.Descending) {
        sortString = "-";
      }
      sortString += toSnakeCase(sortBy.column);
    }

    const rawFilter = {
      id__in: ids,
      custodian,
      status,
      assigned_to: assignedTo,
      updated_before: updateTo,
      updated_after: updateFrom,
      order_by: sortString
    } as RawCatalogueEntryFilter;

    const { previous, next, count, results } = await this.backend.getCatalogueEntries(rawFilter);
    const entryStatuses = await this.statusProvider.fetchStatuses<CatalogueEntryStatus>("entries");

    const userFields: Record<string, number | undefined>[] = results
      .map(({ custodian, assigned_to }) => ({ custodian, assigned_to }));
    const userIds = UserProvider.getUniqueUserIds(userFields);
    const users = await this.userProvider.fetchUsers({ ids: userIds } as UserFilter);

    const catalogueEntries = results.map(entry => ({
      id: entry.id,
      name: entry.name,
      description: entry.description,
      status: this.statusProvider.getRecordStatusFromId(entry.status, entryStatuses),
      updatedAt: entry.updated_at,
      custodian: UserProvider.getUserFromId(entry.custodian, users),
      assignedTo: UserProvider.getUserFromId(entry.assigned_to, users),
      subscription: entry.subscription,
      activeLayer: entry.active_layer,
      layers: entry.layers,
      emailNotifications: entry.email_notifications,
      webhookNotifications: entry.webhook_notifications
    })) as Array<CatalogueEntry>;

   return { previous, next, count, results: catalogueEntries } as PaginatedRecord<CatalogueEntry>;
  }
}
