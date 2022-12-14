import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { LayerSubscriptionStatus, PaginatedRecord,
  RawLayerSubscriptionFilter } from "../backend/backend.api";
import { LayerSubscription, LayerSubscriptionFilter } from "./layerSubscriptionProvider.api";
import { StatusProvider } from "./statusProvider";
import { SortDirection } from "../components/viewState.api";
import { toSnakeCase } from "../util/strings";
import { catalogueEntryProvider } from "./catalogueEntryProvider";

export class LayerSubscriptionProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();
  private statusProvider: StatusProvider = new StatusProvider();

  public async fetchLayerSubscription (id: number): Promise<LayerSubscription> {
    const rawSubscription = await this.backend.getLayerSubscription(id);
    const subscriptionStatuses = await this.statusProvider.fetchStatuses<LayerSubscriptionStatus>("layers/subscriptions");
    const linkedEntry = await catalogueEntryProvider.getOrFetch(rawSubscription.catalogue_entry);

    const layerSubscription = {
      id: rawSubscription.id,
      name: rawSubscription.name,
      url: rawSubscription.url,
      status:  this.statusProvider.getRecordStatusFromId(rawSubscription.status, subscriptionStatuses),
      frequency: rawSubscription.frequency,
      subscribedDate: rawSubscription.subscribed_at
    } as LayerSubscription;

    if (linkedEntry) {
      layerSubscription.catalogueEntry = { id: linkedEntry.id, name: linkedEntry.name };
    }

    return layerSubscription;
  }

  public async fetchLayerSubscriptions ({ subscribedFrom, subscribedTo, status, sortBy }: LayerSubscriptionFilter):
      Promise<PaginatedRecord<LayerSubscription>> {
    let sortString = "";
    if (sortBy && sortBy.column) {
      if (sortBy.direction === SortDirection.Descending) {
        sortString = "-";
      }
      sortString += toSnakeCase(sortBy.column);
    }

    const rawFilter = {
      status,
      subscribed_before: subscribedTo,
      subscribed_after: subscribedFrom,
      order_by: sortString
    } as RawLayerSubscriptionFilter;

    const { previous, next, count, results } = await this.backend.getLayerSubscriptions(rawFilter);
    const subscriptionStatuses = await this.statusProvider.fetchStatuses("layers/subscriptions");
    const linkedCatalogueEntries = await catalogueEntryProvider
      .getOrFetchList(results.map(entry => entry.catalogue_entry));
    const layerSubscriptions = results.map(rawSubscription => {
      const linkedEntry = linkedCatalogueEntries.find(record => record.id === rawSubscription.catalogue_entry);

      const layerSubscription = {
        id: rawSubscription.id,
        name: rawSubscription.name,
        url: rawSubscription.url,
        status: this.statusProvider.getRecordStatusFromId(rawSubscription.status, subscriptionStatuses),
        frequency: rawSubscription.frequency,
        subscribedDate: rawSubscription.subscribed_at
      } as LayerSubscription;

      if(linkedEntry) {
        layerSubscription.catalogueEntry = { id: linkedEntry.id, name: linkedEntry.name };
      }

      return layerSubscription;
    }) as Array<LayerSubscription>;

    return { previous, next, count, results: layerSubscriptions } as PaginatedRecord<LayerSubscription>;
  }
}

export const layerSubscriptionProvider = new LayerSubscriptionProvider();
