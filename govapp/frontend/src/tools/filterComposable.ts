import { Filter } from './filterComposable.api';
import { ref, Ref, UnwrapRef } from 'vue';
import { PaginationFilter } from '../backend/backend.api';

export function useTableFilterComposable<T extends PaginationFilter> () {
  const tableFilters: Ref<UnwrapRef<T>> = ref(new Map() as T);

  function setFilter ({ name, value }: Filter) {
    if (typeof value === 'undefined') {
      tableFilters.value.delete(name);
    } else {
      tableFilters.value.set(name, value);
    }
  }

  function clearFilter (name: string) {
    setFilter({ name });
  }

  return { tableFilters, setFilter, clearFilter };
}
