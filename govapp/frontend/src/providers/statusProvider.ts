import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { PaginatedRecord, RecordStatus }  from "../backend/backend.api";

export class StatusProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === 'mock' ? new BackendServiceStub() : new BackendService();

  public async fetchStatuses (): Promise<PaginatedRecord<RecordStatus>> {
    return await this.backend.getStatuses();
  }

}
