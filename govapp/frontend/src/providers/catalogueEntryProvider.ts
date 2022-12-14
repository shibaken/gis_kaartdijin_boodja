import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { CatalogueEntryStatus, PaginatedRecord, RawCatalogueEntry, RawCatalogueEntryFilter, RawEntryPatch, RecordStatus,
  User } from "../backend/backend.api";
import { CatalogueEntry, CatalogueEntryFilter } from "./catalogueEntryProvider.api";
import { statusProvider } from "./statusProvider";
import { userProvider, UserProvider } from "./userProvider";
import { SortDirection } from "../components/viewState.api";
import { toSnakeCase } from "../util/strings";
import { useCatalogueEntryStore } from "../stores/CatalogueEntryStore";
import { useUserStore } from "../stores/UserStore";

export class CatalogueEntryProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();

  /**
   * Do initial fetching separate to instantiation of the class
   * Usage of stores can only occur after store has been created and application mounted.
   */
  public init () {
    statusProvider.fetchStatuses<CatalogueEntryStatus>("entries")
      .then(statuses => useCatalogueEntryStore().entryStatuses = statuses);
  }

  private async rawToCatalogueEntry(entry: RawCatalogueEntry): Promise<CatalogueEntry> {
    const entryStatuses: RecordStatus<CatalogueEntryStatus>[] = useCatalogueEntryStore().entryStatuses;
    const users = useUserStore().users;
    let user: User | undefined;

    if (typeof entry.assigned_to === "number") {
      const matchUser = users.find(match => match.id === entry.assigned_to);
      user = matchUser ?? await userProvider.fetchUser(entry.assigned_to);
    }

    return {
      id: entry.id,
      name: entry.name,
      description: entry.description,
      status: statusProvider.getRecordStatusFromId(entry.status, entryStatuses),
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

  public async getOrFetch (id: number): Promise<CatalogueEntry> {
    const storeMatch = useCatalogueEntryStore().catalogueEntries.find(entry => entry.id === id);
    return storeMatch ? Promise.resolve(storeMatch) : this.fetchCatalogueEntry(id);
  }

  public async getOrFetchList (ids: Array<number>): Promise<CatalogueEntry[]> {
    const extantRecords: Array<CatalogueEntry> = Array.from(useCatalogueEntryStore().catalogueEntries);
    const recordsToFetch: Array<number> = [];

    extantRecords.forEach(record => {
      if (ids.indexOf(record.id) >= 0) {
        extantRecords.push(record);
      } else {
        recordsToFetch.push(record.id);
      }
    });

    if (recordsToFetch.length > 0) {
      const filter: CatalogueEntryFilter = { ids: recordsToFetch };
      const recordsToFetchResponse = await this.fetchCatalogueEntries(filter);
      extantRecords.push(...recordsToFetchResponse.results);
    }

    return extantRecords;
  }

  public async fetchCatalogueEntry (id: number): Promise<CatalogueEntry> {
    const entry = await this.rawToCatalogueEntry(await this.backend.getCatalogueEntry(id));
    useCatalogueEntryStore().updateEntry(entry);

    return entry;
  }

  public async fetchCatalogueEntries ({ ids, custodian, status, assignedTo, updateFrom, updateTo, sortBy }: CatalogueEntryFilter):
      Promise<PaginatedRecord<CatalogueEntry>> {
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
    const entryStatuses = await statusProvider.fetchStatuses<CatalogueEntryStatus>("entries");

    const userFields: Record<string, number | undefined>[] = results
      .map(({ custodian, assigned_to }) => ({ custodian, assigned_to }));
    const userIds = UserProvider.getUniqueUserIds(userFields);
    const users = (await userProvider.users)
      .filter(user => userIds.indexOf(user.id) >= 0);

    const catalogueEntries = results.map(entry => ({
      id: entry.id,
      name: entry.name,
      description: entry.description,
      status: statusProvider.getRecordStatusFromId(entry.status, entryStatuses),
      updatedAt: entry.updated_at,
      custodian: UserProvider.getUserFromId(entry.custodian, users),
      assignedTo: UserProvider.getUserFromId(entry.assigned_to, users),
      subscription: entry.subscription,
      activeLayer: entry.active_layer,
      layers: entry.layers,
      emailNotifications: entry.email_notifications,
      webhookNotifications: entry.webhook_notifications
    })) as Array<CatalogueEntry>;

    useCatalogueEntryStore().$patch({ catalogueEntries: catalogueEntries });

   return { previous, next, count, results: catalogueEntries } as PaginatedRecord<CatalogueEntry>;
  }

  public async assignUser (entryId: number, userId: number) {
    const patchedEntry = await this.rawToCatalogueEntry(await this.backend.patchCatalogueEntry(entryId, {
      assigned_to: userId
    } as RawEntryPatch));
    useCatalogueEntryStore().updateEntry(patchedEntry);
  }

  public async lock (entryId: number) {
    const statusCode = await this.backend.lock(entryId);

    if (statusCode === 204) {
      const updatedEntry = await this.fetchCatalogueEntry(entryId);
      useCatalogueEntryStore().updateEntry(updatedEntry);
      return updatedEntry;
    }
  }

  public async unlock (entryId: number) {
    const statusCode = await this.backend.unlock(entryId);

    if (statusCode === 204) {
      const updatedEntry = await this.fetchCatalogueEntry(entryId);
      useCatalogueEntryStore().updateEntry(updatedEntry);
      return updatedEntry;
    }
  }
}

export const catalogueEntryProvider = new CatalogueEntryProvider();