import { BackendService } from "./backend.service";
import { RawCatalogueEntry, RawLayerSubscription, PaginatedRecord, RecordStatus,
  User, StatusType } from "./backend.api";

function wrapPaginatedRecord<T> (results: Array<T>): PaginatedRecord<T> {
  return {
    previous: null,
    next: null,
    count: results.length,
    results
  };
}

const DUMMY_CATALOGUE_ENTRIES: Array<RawCatalogueEntry> = [
  {
    "id": 1,
    "name": "Catalogue Entry 1",
    "description": "This is the first example catalogue entry",
    "status": 1,
    "updated_at": "2022-10-13T04:26:24.629841Z",
    "custodian": 1,
    "assigned_to": 1,
    "subscription": 1,
    "active_layer": 1,
    "layers": [1],
    "email_notifications": [1],
    "webhook_notifications": [1]
  },
  {
    "id": 2,
    "name": "Catalogue Entry 2",
    "description": "This is the second example catalogue entry",
    "status": 2,
    "updated_at": "2022-10-12T21:05:32.325153Z",
    "custodian": 2,
    "assigned_to": 3,
    "subscription": 2,
    "active_layer": 2,
    "layers": [2],
    "email_notifications": [2],
    "webhook_notifications": [2]
  },
  {
    "id": 3,
    "name": "Catalogue Entry 3",
    "description": "This is the third example catalogue entry",
    "status": 3,
    "updated_at": "2022-10-11T12:44:15.562984Z",
    "custodian": 2,
    "assigned_to": null,
    "subscription": 3,
    "active_layer": 3,
    "layers": [3],
    "email_notifications": [3],
    "webhook_notifications": [3]
  }
];

const DUMMY_LAYER_SUBSCRIPTIONS: Array<RawLayerSubscription> = [
  {
    "id": 1,
    "name": "Layer Subscription 1",
    "url": "https://www.abc.net.au/",
    "frequency": "1 11:11:11",
    "status": 1,
    "subscribed_at": "2022-10-13T02:11:02.818232Z",
    "catalogue_entry": 1
  }, {
    "id": 2,
    "name": "Layer Subscription 2",
    "url": "https://www.sbs.com.au/",
    "frequency": "2 22:22:22",
    "status": 2,
    "subscribed_at": "2022-10-12T23:53:32.756754Z",
    "catalogue_entry": 2
  }, {
    "id": 3,
    "name": "Layer Subscription 3",
    "url": "https://www.nit.com.au/",
    "frequency": "4 09:33:33",
    "status": 3,
    "subscribed_at": "2022-10-11T13:27:12.345346Z",
    "catalogue_entry": 3
  }
];

const DUMMY_STATUSES: Array<RecordStatus<unknown>> = [
  { "id": 1, "label": "Draft" },
  { "id": 2, "label": "Locked" },
  { "id": 3, "label": "Cancelled" }
];

const DUMMY_USERS: Array<User> = [
  { "id": 1, "username": "Raoul Wallenberg", "groups": [] },
  { "id": 2, "username": "Carl Lutz", "groups": [] },
  { "id": 3, "username": "Chiune Sugihara", "groups": [] }
];

export class BackendServiceStub implements BackendService {
  public getLayerSubscriptions (): Promise<PaginatedRecord<RawLayerSubscription>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_LAYER_SUBSCRIPTIONS));
  }

  public getCatalogueEntries (): Promise<PaginatedRecord<RawCatalogueEntry>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_CATALOGUE_ENTRIES));
  }

  public async getStatuses<T> (): Promise<PaginatedRecord<RecordStatus<T>>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_STATUSES) as PaginatedRecord<RecordStatus<T>>);
  }

  async getStatus<T> (_statusType: StatusType, statusId: number): Promise<RecordStatus<T>> {
    return Promise.resolve(DUMMY_STATUSES.find(({ id }) => id === statusId) as RecordStatus<T>);
  }

  async getUser (userId: number): Promise<User> {
    return Promise.resolve(DUMMY_USERS.find(({ id }) => id === userId) as User);
  }

  async getUsers (): Promise<PaginatedRecord<User>> {
    return Promise.resolve(wrapPaginatedRecord(DUMMY_USERS));
  }
}
