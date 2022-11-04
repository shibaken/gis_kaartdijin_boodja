import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { RecordStatus, StatusType } from "../backend/backend.api";

export class StatusProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();

  public async fetchStatus<T> (statusType: StatusType, statusId: number): Promise<RecordStatus<T>> {
    return await this.backend.getStatus(statusType, statusId);
  }

  public async fetchStatuses<T> (statusType: StatusType): Promise<Array<RecordStatus<T>>> {
    const entryStatuses = await this.backend.getStatuses<T>(statusType);
    return entryStatuses.results;
  }

  // We don't need to paginate here so unwrap the results
  public getRecordStatusFromId<T> (statusId: number, statuses: Array<RecordStatus<T>>): RecordStatus<T> {
    const statusMatch = statuses.find(status => status.id === statusId);
    if (!statusMatch) {
      throw new Error("Status not found.");
    } else {
      return statusMatch;
    }
  }

  public static getUniqueStatuses<T> (statusList: Array<RecordStatus<T>>): Array<RecordStatus<T>> {
    return statusList
      .reduce((previous, current) => {
        return current && previous.findIndex(value => value.id === current.id) === -1 ? [...previous, current] : previous;
      }, [] as Array<RecordStatus<T>>);
  }
}
