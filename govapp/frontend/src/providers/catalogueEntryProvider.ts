import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { CatalogueEntryStatus, PaginatedRecord, RawCatalogueEntry, RawCatalogueEntryFilter, RecordStatus,
  User } from "../backend/backend.api";
import { CatalogueEntry, CatalogueEntryFilter } from "./catalogueEntryProvider.api";
import { statusProvider } from "./statusProvider";
import { userProvider } from "./userProvider";
import { SortDirection } from "../components/viewState.api";
import { toSnakeCase } from "../util/strings";
import { useCatalogueEntryStore } from "../stores/CatalogueEntryStore";

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

  private async rawToCatalogueEntry (entry: RawCatalogueEntry): Promise<CatalogueEntry> {
    const entryStatuses: RecordStatus<CatalogueEntryStatus>[] = useCatalogueEntryStore().entryStatuses;
    const users = await userProvider.users;
    let user: User | undefined;

    if (typeof entry.assigned_to === "number") {
      const matchUser = users.find(match => match.id === entry.assigned_to);
      user = matchUser ?? await userProvider.fetchUser(entry.assigned_to);
    }
    const editors: Array<User> = [];
    const toFetch: Array<number> = [];
    entry.editors.forEach(editorId => {
      const match = users.find(user => editorId === user.id);

      if (match) {
        editors.push(match);
      } else {
        toFetch.push(editorId);
      }
    });
    if (toFetch.length > 0) {
      const fetchedEditors = await userProvider.fetchUsers({ ids: toFetch });
      editors.concat(fetchedEditors);
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
      webhookNotifications: entry.webhook_notifications,
      editors
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

  public async fetchCatalogueEntries ({
    ids, custodian, status, assignedTo, updateFrom, updateTo, sortBy, limit, offset
  }: CatalogueEntryFilter):
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
      order_by: sortString,
      limit,
      offset
    } as RawCatalogueEntryFilter;

    const { previous, next, count, results } = await this.backend.getCatalogueEntries(rawFilter);
    const catalogueEntries = await Promise.all(results.map(this.rawToCatalogueEntry));
    const catalogueEntryMeta = {
      total: count,
      offset: (rawFilter.offset || 0) + (rawFilter.limit || 0),
      limit: rawFilter.limit
    };

    useCatalogueEntryStore().$patch({
      catalogueEntries: catalogueEntries,
      catalogueEntryMeta
    });

    return { previous, next, count, results: catalogueEntries } as PaginatedRecord<CatalogueEntry>;
  }

  public async assignUser (entryId: number, userId: number) {
    const statusCode = await this.backend.entryAssign(entryId, userId);
    if (statusCode >= 200 && statusCode < 300) {
      const entryStore = useCatalogueEntryStore();
      const updatedEntry = entryStore.catalogueEntries.find(entry => entry.id === entryId);
      const users = await userProvider.users;

      if (updatedEntry) {
        const updatedUser = users.find(user => user.id === userId);
        if (updatedUser) {
          updatedEntry.assignedTo = updatedUser;
          useCatalogueEntryStore().updateEntry(updatedEntry);
        } else {
          console.error(`Entry ${entryId} could not be assigned to user ${userId}. User not found`);
        }
      } else {
        console.error(`Entry ${entryId} was not found. Could not complete action (unassign user)`)
      }
    }
  }

  public async unassignUser (entryId: number) {
    const statusCode = await this.backend.entryUnassign(entryId);
    if (statusCode >= 200 && statusCode < 300) {
      const entryStore = useCatalogueEntryStore();
      const updatedEntry = entryStore.catalogueEntries.find(entry => entry.id === entryId);
      if (updatedEntry) {
        updatedEntry.assignedTo = undefined;
        entryStore.updateEntry(updatedEntry);
      } else {
        console.error(`Entry ${entryId} was not found. Could not complete action (unassign user)`);
      }
    } else {
      console.error(`Error while processing unassignUser request. Error code ${statusCode}`)
    }
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

  public async decline (entryId: number) {
    const statusCode = await this.backend.decline(entryId);

    if (statusCode === 204) {
      const updatedEntry = await this.fetchCatalogueEntry(entryId);
      useCatalogueEntryStore().updateEntry(updatedEntry);
      return updatedEntry;
    }
  }
}

export const catalogueEntryProvider = new CatalogueEntryProvider();