import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { LayerSubmissionStatus, PaginatedRecord, RawLayerSubmissionFilter } from "../backend/backend.api";
import { LayerSubmission, LayerSubmissionFilter } from "./layerSubmissionProvider.api";
import { statusProvider } from "./statusProvider";
import { SortDirection } from "../components/viewState.api";
import { toSnakeCase } from "../util/strings";
import { catalogueEntryProvider } from "./catalogueEntryProvider";

export class LayerSubmissionProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();

  public async fetchLayerSubmission (id: number): Promise<LayerSubmission> {
    const rawSubmission = await this.backend.getLayerSubmission(id);
    const submissionStatuses = await statusProvider
      .fetchStatuses<LayerSubmissionStatus>("layers/submissions");

    const submissionEntry = await catalogueEntryProvider.getOrFetch(rawSubmission.catalogue_entry);

    return {
      id: rawSubmission.id,
      name: rawSubmission.name,
      description: rawSubmission.description,
      file: rawSubmission.file,
      status: statusProvider.getRecordStatusFromId(rawSubmission.status, submissionStatuses),
      submittedDate: rawSubmission.submitted_at,
      catalogueEntry: { id: submissionEntry.id, name: submissionEntry?.name },
      attributes: rawSubmission.attributes,
      metadata: rawSubmission.metadata,
      symbology: rawSubmission.symbology
    } as LayerSubmission;
  }

  public async fetchLayerSubmissions ({ submittedFrom, submittedTo, status, sortBy }: LayerSubmissionFilter):
      Promise<PaginatedRecord<LayerSubmission>> {
    let sortString = "";
    if (sortBy && sortBy.column) {
      if (sortBy.direction === SortDirection.Descending) {
        sortString = "-";
      }
      sortString += toSnakeCase(sortBy.column);
    }

    const rawFilter = {
      status,
      submitted_before: submittedTo,
      submitted_after: submittedFrom,
      order_by: sortString
    } as RawLayerSubmissionFilter;

    const { previous, next, count, results } = await this.backend.getLayerSubmissions(rawFilter);
    const submissionStatuses = await statusProvider
      .fetchStatuses<LayerSubmissionStatus>("layers/submissions");
    const linkedEntries = await catalogueEntryProvider
      .getOrFetchList(results.map(entry => entry.catalogue_entry));

    const layerSubmissions = results.map(rawSubmission => {
      const linkedEntry = linkedEntries.find(record => record.id === rawSubmission.catalogue_entry);

      const layerSubmission = {
        id: rawSubmission.id,
        name: rawSubmission.name,
        description: rawSubmission.description,
        file: rawSubmission.file,
        status: statusProvider.getRecordStatusFromId(rawSubmission.status, submissionStatuses),
        submittedDate: rawSubmission.submitted_at,
        attributes: rawSubmission.attributes,
        metadata: rawSubmission.metadata,
        symbology: rawSubmission.symbology
      } as LayerSubmission;

      if(linkedEntry) {
        layerSubmission.catalogueEntry = { id: linkedEntry.id, name: linkedEntry.name };
      }

      return layerSubmission;
    }) as Array<LayerSubmission>;

    return { previous, next, count, results: layerSubmissions } as PaginatedRecord<LayerSubmission>;
  }
}

export const layerSubmissionProvider = new LayerSubmissionProvider();