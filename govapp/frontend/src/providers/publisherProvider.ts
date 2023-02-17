import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { CddpPublishChannel, GeoserverPublishChannel, PublishEntry, PublishEntryFilter } from "./publisherProvider.api";
import { PaginatedRecord, PublishEntryStatus, RawCddpPublishChannel, RawGeoserverPublishChannel, RawPublishEntry,
  RawPublishEntryFilter, User } from "../backend/backend.api";
import { usePublishEntryStore } from "../stores/PublishEntryStore";
import { PaginationFilter } from "./providerCommon.api";
import { catalogueEntryProvider } from "./catalogueEntryProvider";
import { SortDirection } from "../components/viewState.api";
import { toSnakeCase } from "../util/strings";
import { statusProvider } from "./statusProvider";
import { userProvider } from "./userProvider";
import { storeToRefs } from "pinia";

export class PublisherProvider {
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();

  /**
   * Do initial fetching separate to instantiation of the class
   * Usage of stores can only occur after store has been created and application mounted.
   */
  public init () {
    statusProvider.fetchStatuses<PublishEntryStatus>("publish/entries")
      .then(statuses => {
        storeToRefs(usePublishEntryStore()).publishEntryStatuses.value = statuses;
      })
  }

  public rawToCddpChannel (raw: RawCddpPublishChannel): CddpPublishChannel {
    return {
      id: raw.id,
      name: raw.name,
      description: raw.description,
      format: raw.format,
      mode: raw.mode,
      frequency: raw.frequency,
      path: raw.path,
      publishEntryId: raw.publish_entry,
    }
  }

  public rawToGeoChannel (raw: RawGeoserverPublishChannel): GeoserverPublishChannel {
    return {
      id: raw.id,
      name: raw.name,
      description: raw.description,
      mode: raw.mode,
      frequency: raw.frequency,
      workspace: raw.workspace,
      publishEntryId: raw.publish_entry
    }
  }

  public async rawToPublishEntry (raw: RawPublishEntry): Promise<PublishEntry> {
    const publishEntryStatuses = usePublishEntryStore().publishEntryStatuses;
    const catalogueEntry = catalogueEntryProvider.getOrFetch(raw.catalogue_entry);
    const users = await userProvider.users;
    const editors: Array<User> = [];
    const toFetch: Array<number> = [];
    let user: User | undefined;

    const matchUser = users.find(match => match.id === raw.assigned_to);
    user = matchUser ?? await userProvider.fetchUser(raw.assigned_to);

    if (toFetch.length > 0) {
      const fetchedEditors = await userProvider.fetchUsers({ ids: toFetch });
      editors.concat(fetchedEditors);
    }

    raw.editors.forEach(editorId => {
      const match = users.find(user => editorId === user.id);

      if (match) {
        editors.push(match);
      } else {
        toFetch.push(editorId);
      }
    });

    return {
      id: raw.id,
      name: raw.name,
      description: raw.description,
      status: await statusProvider.getRecordStatusFromId<PublishEntryStatus>(raw.status, await publishEntryStatuses),
      updatedAt: raw.updated_at,
      publishedAt: raw.published_at,
      editors: editors,
      assignedTo: user,
      catalogueEntry: await catalogueEntry,
      // cddpChannel: raw.cddp_channel, TODO
      // geoserverChannel: raw.geoserver_channel TODO
    } as PublishEntry;
  }

  public async fetchPublishEntry (id: number): Promise<PublishEntry> {
    const entry = await this.rawToPublishEntry(await this.backend.getPublishEntry(id));
    usePublishEntryStore().updateEntry(entry);

    return entry;
  }

  public async fetchPublishEntries ({ limit, offset, ids, sortBy, status, updatedBefore, updatedAfter, assignedTo,
                                    search }:
                                      PublishEntryFilter): Promise<PaginatedRecord<PublishEntry>> {
    const publishStore = usePublishEntryStore();
    let sortString = "";
    if (sortBy && sortBy.column) {
      if (sortBy.direction === SortDirection.Descending) {
        sortString = "-";
      }
      sortString += toSnakeCase(sortBy.column);
    }

    const rawFilter = {
      id__in: ids,
      order_by: sortString,
      limit,
      offset,
      status,
      updated_before: updatedBefore,
      updated_after: updatedAfter,
      assigned_to: assignedTo,
      search
    } as RawPublishEntryFilter;

    const { previous, next, count, results } = await this.backend.getPublishEntries(rawFilter);
    await publisherProvider.getOrFetchList(results.map(({ catalogue_entry }) => catalogue_entry));
    const publishEntries: Array<PublishEntry> = await Promise.all(results.map(this.rawToPublishEntry));
    const publishEntryMeta = {
      total: count,
      offset: (rawFilter.offset || 0) + (rawFilter.limit || 0),
      limit: rawFilter.limit
    };

    let updatedCache: PublishEntry[] = publishStore.publishEntriesCache;

    // Add new and update existing entries
    publishEntries.forEach((entry) => {
      const indexMatch = publishStore.publishEntriesCache.findIndex(cacheEntry => cacheEntry.id === entry.id);
      if (indexMatch) {
        updatedCache[indexMatch] = entry;
      } else {
        updatedCache.push(entry);
      }
    });

    publishStore.$patch({
      publishEntries,
      publishEntryMeta,
      publishEntriesCache: updatedCache
    });

    return { previous, next, count, results: publishEntries } as PaginatedRecord<PublishEntry>;
  }

  public async fetchCddpPublishChannels (filter: PaginationFilter): Promise<CddpPublishChannel[]> {
    return (await this.backend.getCddpPublishChannels(filter))
      .results.map(this.rawToCddpChannel);
  }

  public async fetchGeoserverPublishChannels (filter: PaginationFilter): Promise<GeoserverPublishChannel[]> {
    return (await this.backend.getGeoserverPublishChannels(filter))
      .results.map(this.rawToGeoChannel);
  }

  public async fetchCddpPublishEntries (filter: PaginationFilter = {}): Promise<PublishEntry[]> {
    return Promise.all((await this.backend.getPublishEntries(filter))
      .results.map(result => this.rawToPublishEntry(result)));
  }

  public async getOrFetch (id: number): Promise<PublishEntry> {
    const entryStore = usePublishEntryStore();
    let entry = entryStore.publishEntriesCache.find(entry => entry.id === id);
    if (!entry) {
      entry = await this.getOrFetch(id);
      entryStore.$patch({
        publishEntries: [...entryStore.publishEntries, await entry]
      });
    }

    if (!entry) {
      throw new Error(`No catalogue entry found for id: ${id}`);
    }

    return entry;
  }

  public async getOrFetchList (ids: Array<number>): Promise<PublishEntry[]> {
    const extantRecords: Array<PublishEntry> = Array.from(usePublishEntryStore().publishEntriesCache);
    const recordsToFetch: Array<number> = [];

    extantRecords.forEach(record => {
      if (ids.indexOf(record.id) >= 0) {
        extantRecords.push(record);
      } else {
        recordsToFetch.push(record.id);
      }
    });

    if (recordsToFetch.length > 0) {
      const filter: PublishEntryFilter = { ids: recordsToFetch };
      const recordsToFetchResponse = await this.fetchPublishEntries(filter);
      extantRecords.push(...recordsToFetchResponse.results);
    }

    return extantRecords;
  }
}

export const publisherProvider = new PublisherProvider();
