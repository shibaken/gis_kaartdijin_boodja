import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { PaginatedRecord, RawLayerSubscriptionFilter } from "../backend/backend.api";
import { LayerSubscription, LayerSubscriptionFilter } from "./layerSubscriptionProvider.api";
import { StatusProvider } from "./statusProvider";

export class LayerSubscriptionProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();
  private statusProvider: StatusProvider = new StatusProvider();

  public async fetchLayerSubscriptions ({ subscribedFrom, subscribedTo, status }: LayerSubscriptionFilter):
    Promise<PaginatedRecord<LayerSubscription>> {
    // TODO: error handling for multiple
    const rawFilter = {
      status,
      subscribed_before: subscribedTo,
      subscribed_after: subscribedFrom
    } as RawLayerSubscriptionFilter;



    const { previous, next, count, results } = await this.backend.getLayerSubscriptions(rawFilter);
    const entryStatuses = await this.statusProvider.fetchStatuses("entries");

    const layerSubscriptions = results.map(rawSubscription => ({
      id: rawSubscription.id,
      name: rawSubscription.name,
      url: rawSubscription.url,
      status:  this.statusProvider.getRecordStatusFromId(rawSubscription.status, entryStatuses),
      frequency: rawSubscription.frequency,
      subscribedDate: rawSubscription.subscribed_at,
      subscribedTime: rawSubscription.subscribed_at,
      catalogueEntry: rawSubscription.catalogue_entry
    })) as Array<LayerSubscription>;

    return { previous, next, count, results: layerSubscriptions } as PaginatedRecord<LayerSubscription>;
  }
}
