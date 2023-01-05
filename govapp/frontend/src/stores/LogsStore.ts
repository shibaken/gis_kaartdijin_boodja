import { defineStore } from "pinia";
import { Ref, ref, toRefs } from "vue";
import { CommunicationLog, CommunicationLogType } from "../providers/logsProvider.api";
import { PaginationFilter, RecordMeta } from "../providers/providerCommon.api";
import { useTableFilterComposable } from "../tools/filterComposable";

export const useLogsStore = defineStore("logs", () => {
  const communicationLogs: Ref<CommunicationLog[]> = ref([]);
  const communicationLogsMeta: Ref<RecordMeta> = ref({ total: 0 });
  const communicationLogTypes: Ref<CommunicationLogType[]> = ref([]);
  const tableFilterComposable = useTableFilterComposable<PaginationFilter>();
  const { filters, setFilter, clearFilters } = toRefs(tableFilterComposable);

  return { communicationLogs, communicationLogsMeta, communicationLogTypes, filters, setFilter, clearFilters };
});