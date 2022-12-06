import { SortDirection } from "../components/viewState.api";
import { Ref } from "vue";
import { PaginationFilter } from "../providers/providerCommon.api";

export function useTableSortComposable<T extends PaginationFilter> (filters: Ref<T>) {
  function sortDirection (column: string) {
    return filters.value.sortBy?.column === column ?
      filters.value.sortBy?.direction :
      SortDirection.None;
  }

  function onSort (field: string) {
    const direction = filters.value.sortBy?.direction;
    let newDirection: SortDirection | undefined = undefined;

    if (filters.value.sortBy?.column !== field || !direction || direction === SortDirection.None) {
      newDirection = SortDirection.Ascending;
    } else if (direction === SortDirection.Ascending) {
      newDirection = SortDirection.Descending;
    } else if (direction === SortDirection.Descending) {
      newDirection = undefined;
    }

    filters.value.sortBy = newDirection ? { column: field as string, direction: newDirection } : undefined;
  }

  return { sortDirection, onSort };
}