import { computed, ComputedRef, ref, Ref, watch } from "vue";

export function useComputedPaginationComposable<T> (total: Ref<number>) {
  const paginationComposable: PaginationComposable = usePaginationComposable(total.value);

  watch(total, () => {
    paginationComposable.total.value = total.value;
  });

  (<PaginationComposable & { resultWindow: ComputedRef<[number, number]> }>paginationComposable).resultWindow = computed(() => {
    const start = paginationComposable.pageSize.value * (paginationComposable.currentPage.value - 1);
    return [start + 1, Math.min(start + paginationComposable.pageSize.value, total.value)];
  });

  return paginationComposable as PaginationComposable & { resultWindow: ComputedRef<[number, number]> };
}

interface PaginationComposable {
  numPages: ComputedRef<number>;
  canNext: ComputedRef<boolean>;
  total: Ref<number>;
  previousPage: () => number;
  nextPage: () => number;
  pageSize: Ref<number>;
  currentPage: Ref<number>;
  canPrevious: ComputedRef<boolean>;
  setPageSize: (size: number) => void;
  setPage: (pageNumber: number) => void;
}
export function usePaginationComposable (resultTotal: number) {
  const total: Ref<number> = ref(resultTotal);
  const currentPage: Ref<number> = ref(1);
  const pageSize: Ref<number> = ref(10);
  const numPages: ComputedRef<number> = computed(() => Math.ceil(total.value / pageSize.value));
  const canPrevious = computed(() => currentPage.value > 1);
  const canNext = computed(() => currentPage.value < numPages.value);

  function previousPage () {
    if (canPrevious.value) {
      currentPage.value--;
    }
    return currentPage.value;
  }

  function nextPage () {
    if (canNext.value) {
      currentPage.value++;
    }
    return currentPage.value;
  }

  function setPage (pageNumber: number) {
    if (currentPage.value < numPages.value && currentPage.value > 1 && currentPage.value !== pageNumber) {
      currentPage.value = pageNumber;
    }
    return currentPage.value;
  }

  function setPageSize (size: number) {
    pageSize.value = size;
  }

  return { currentPage, pageSize, numPages, total, canNext, canPrevious, nextPage, previousPage, setPage, setPageSize };
}