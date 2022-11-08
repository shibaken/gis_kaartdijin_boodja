import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { PaginatedRecord, RawLayerSubmissionFilter } from "../backend/backend.api";
import { LayerSubmission, LayerSubmissionFilter } from "./layerSubmissionProvider.api";
import { StatusProvider } from "./statusProvider";
import { CatalogueEntryProvider } from "./catalogueEntryProvider";
import { useCatalogueEntryStore } from "../stores/CatalogueEntryStore";
import { CatalogueEntry, CatalogueEntryFilter } from "./catalogueEntryProvider.api";
import { unique } from "../util/filtering";

export class LayerSubmissionProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();
  private statusProvider: StatusProvider = new StatusProvider();
  private catalogueEntryProvider: CatalogueEntryProvider = new CatalogueEntryProvider();

  public async fetchLayerSubmissions (layerSubmissionFilter: LayerSubmissionFilter):
      Promise<PaginatedRecord<LayerSubmission>> {

    const { submittedFrom, submittedTo, status } = Object.fromEntries(layerSubmissionFilter.entries());
    const rawFilter = {
      status,
      submitted_before: submittedTo,
      submitted_after: submittedFrom
    } as RawLayerSubmissionFilter;

    const { previous, next, count, results } = await this.backend.getLayerSubmissions(rawFilter);
    const submissionStatuses = await this.statusProvider.fetchStatuses("layers/subscriptions");

    // TODO: cache this
    const fetchedEntries: Array<CatalogueEntry> = useCatalogueEntryStore().catalogueEntries;
    const entriesToFetch = results
      .map(rawSubmission => rawSubmission.catalogue_entry)
      .filter(entryId => fetchedEntries
        .map(entry => entry.id)
        .findIndex(fetchedId => fetchedId === entryId) === -1);
    const tableFilterMap: CatalogueEntryFilter = new Map();

    const requestedEntries: Array<CatalogueEntry> = fetchedEntries;
    if (entriesToFetch.length > 0) {
      tableFilterMap.set("ids", unique<number>(entriesToFetch));
      const { results: catalogueEntryResults } = await this.catalogueEntryProvider.fetchCatalogueEntries(tableFilterMap);
      requestedEntries.push(...catalogueEntryResults);
    }

    const layerSubmissions = results.map(rawSubmission => ({
      id: rawSubmission.id,
      name: rawSubmission.name,
      description: rawSubmission.description,
      file: rawSubmission.file,
      status: this.statusProvider.getRecordStatusFromId(rawSubmission.status, submissionStatuses),
      submittedDate: rawSubmission.submitted_at,
      catalogueEntry: requestedEntries.find(entry => entry.id === rawSubmission.catalogue_entry)?.name,
      attributes: rawSubmission.attributes,
      metadata: rawSubmission.metadata,
      symbology: rawSubmission.symbology
    })) as Array<LayerSubmission>;

    return { previous, next, count, results: layerSubmissions } as PaginatedRecord<LayerSubmission>;
  }
}
