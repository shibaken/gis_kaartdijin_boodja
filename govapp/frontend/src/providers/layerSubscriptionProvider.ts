import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { LayerSubscriptionStatus, PaginatedRecord,
  RawLayerSubscriptionFilter } from "../backend/backend.api";
import { LayerSubscription, LayerSubscriptionFilter } from "./layerSubscriptionProvider.api";
import { StatusProvider } from "./statusProvider";

export class LayerSubscriptionProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();
  private statusProvider: StatusProvider = new StatusProvider();

  public async fetchLayerSubscription (id: number): Promise<LayerSubscription> {
    const rawSubscription = await this.backend.getLayerSubscription(id);
    const subscriptionStatuses = await this.statusProvider.fetchStatuses<LayerSubscriptionStatus>("layers/subscriptions");

    return {
      id: rawSubscription.id,
      name: rawSubscription.name,
      url: rawSubscription.url,
      status:  this.statusProvider.getRecordStatusFromId(rawSubscription.status, subscriptionStatuses),
      frequency: rawSubscription.frequency,
      subscribedDate: rawSubscription.subscribed_at,
      catalogueEntry: rawSubscription.catalogue_entry
    } as LayerSubscription;
  }

  public async fetchLayerSubscriptions (layerSubscriptionFilter: LayerSubscriptionFilter):
      Promise<PaginatedRecord<LayerSubscription>> {
    const { subscribedFrom, subscribedTo, status } = Object.fromEntries(layerSubscriptionFilter.entries());
    const rawFilter = {
      status,
      subscribed_before: subscribedTo,
      subscribed_after: subscribedFrom
    } as RawLayerSubscriptionFilter;

    const { previous, next, count, results } = await this.backend.getLayerSubscriptions(rawFilter);
    const subscriptionStatuses = await this.statusProvider.fetchStatuses("layers/subscriptions");

    const layerSubscriptions = results.map(rawSubscription => ({
      id: rawSubscription.id,
      name: rawSubscription.name,
      url: rawSubscription.url,
      status:  this.statusProvider.getRecordStatusFromId(rawSubscription.status, subscriptionStatuses),
      frequency: rawSubscription.frequency,
      subscribedDate: rawSubscription.subscribed_at,
      catalogueEntry: rawSubscription.catalogue_entry
    })) as Array<LayerSubscription>;

    return { previous, next, count, results: layerSubscriptions } as PaginatedRecord<LayerSubscription>;
  }
}
