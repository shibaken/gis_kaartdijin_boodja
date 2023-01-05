import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { PaginatedRecord, RawCommunicationLog, RawPaginationFilter } from "../backend/backend.api";
import { CommunicationLog, CommunicationLogType } from "./logsProvider.api";
import { userProvider } from "./userProvider";
import { useLogsStore } from "../stores/LogsStore";

export class LogsProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();

  /**
   * Do initial fetching separate to instantiation of the class
   * Usage of stores can only occur after store has been created and application mounted.
   */
  public init () {
    this.backend.getCommunicationTypes()
      .then(logTypes => useLogsStore().$patch({ communicationLogTypes: logTypes }));
  }

  public async fetchCommunicationLogs (entryId: number, filter: RawPaginationFilter): Promise<PaginatedRecord<CommunicationLog>> {
    const logsStore = useLogsStore();
    const [rawLogs, logTypes]: [PaginatedRecord<RawCommunicationLog>, Array<CommunicationLogType>] = await Promise.all([
      this.backend.getCommunicationLogs(entryId, filter),
      this.backend.getCommunicationTypes()
    ]);
    const users = await userProvider.users
    const communicationLogs: Array<CommunicationLog> = rawLogs.results.map((rawLog) => {
      const logUser = users.find(user => user.id === rawLog.user);
      const logType = logTypes.find(logType => logType.id === rawLog.type);

      if (!logUser) {
        throw new Error(`There was an error fetching the log's user: ${JSON.stringify(rawLog)}`);
      }

      if (!logType) {
        throw new Error(`There was an error fetching the log's type: ${JSON.stringify(rawLog)}`);
      }

      return {
        id: rawLog.id,
        createdAt: rawLog.created_at,
        type: logType,
        to: rawLog.to,
        cc: rawLog.cc,
        from: rawLog.from,
        subject: rawLog.subject,
        text: rawLog.text,
        user: logUser,
        documents: rawLog.documents.map(rawDocument => ({
          id: rawDocument.id,
          name: rawDocument.name,
          description: rawDocument.description,
          uploadedAt: rawDocument.uploaded_at,
          file: rawDocument.file,
        }))
      } as CommunicationLog;
    });

    const communicationLogsMeta = {
      total: rawLogs.count,
      offset: (filter.offset || 0) + (filter.limit || 0),
      limit: filter.limit
    };

    logsStore.$patch({
      communicationLogs: communicationLogs,
      communicationLogsMeta
    });

    return { count: rawLogs.count, results: communicationLogs };
  }

  async addCommunicationLog(entryId: number, data: Omit<CommunicationLog, "id" | "documents" | "user">) {
    return this.backend.createCommunicationLog(entryId, {
      created_at: data.createdAt,
      type: data.type.id,
      to: data.to,
      cc: data.cc,
      from: data.from,
      subject: data.subject,
      text: data.text
    });
  }

  public async fetchActionsLogs (entryId: number) {
    const response = await fetch(`/api/catalogue/entries/${entryId}/logs/communications`);
    return await response.json();
  }

  public async addCommunicationFile (entryId: number, logId: number, file: File) {
    return this.backend.uploadCommunicationFile(entryId, logId, file);
  }
}

export const logsProvider = new LogsProvider();