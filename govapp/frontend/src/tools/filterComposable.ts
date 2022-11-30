import { Filter } from "./filterComposable.api";
import { ref, Ref } from "vue";
import { PaginationFilter } from "../providers/providerCommon.api";

export function useTableFilterComposable<T extends PaginationFilter> () {
  const filters = ref({}) as Ref<T>;

  function setFilter ({ field, value }: Filter<T>) {
    // @ts-ignore
    filters.value[field] = value;
  }

  function clearFilters () {
      Object
        .keys(filters.value)
        .forEach((key: keyof T) => {
          // @ts-ignore
          filters.value[key] = undefined;
        });
  }

  return { filters, setFilter, clearFilters };
}
