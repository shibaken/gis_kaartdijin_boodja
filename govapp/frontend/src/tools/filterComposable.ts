import { Filter } from "./filterComposable.api";
import { ref, Ref, UnwrapRef } from "vue";
import { PaginationFilter } from "../providers/providerCommon.api";

export function useTableFilterComposable<T extends PaginationFilter> () {
  const filters: Ref<UnwrapRef<T>> = ref(new Map() as T);

  function setFilter ({ field, value }: Filter) {
    if (typeof value === "undefined" || value === "") {
      filters.value.delete(field);
    } else {
      filters.value.set(field, value);
    }
  }

  function clearFilter (name: string) {
    setFilter({ field: name });
  }

  return { filters, setFilter, clearFilter };
}
