<script lang="ts" setup>
  import { useComputedPaginationComposable } from "../../tools/paginationComposable";
  import { Ref, ref, watch } from "vue";

  const props = defineProps<{
    total: number,
    pageSize: number
  }>();

  const total: Ref<number> = ref(props.total);
  const { currentPage, pageSize, numPages, canPrevious, canNext, previousPage,
    nextPage, setPage, resultWindow } = useComputedPaginationComposable(total);

  watch(props, () => {
    total.value = props.total;
    pageSize.value = props.pageSize;
  });

  const emit = defineEmits<{
    (e: "set-page", pageNumber: number): void
  }>();

  function emitSetPage (pageNumber: number) {
    setPage(pageNumber);
    emit('set-page', pageNumber);
  }
</script>

<template>
  <span v-if="total > 0" class="ms-2 small fw-bold">
    Showing {{ resultWindow[0] }} to {{ resultWindow[1] }} of {{ total }} entries
  </span>
  <span v-else class="ms-2 small fw-bold">No results</span>
  <nav aria-label="Table navigation" class="d-flex justify-content-end">
    <ul class="pagination">
      <li class="page-item" :class="{ disabled: !canPrevious }">
        <a class="page-link" href="#" @click="canPrevious && emit('set-page', previousPage())">
          Previous
        </a>
      </li>
      <li v-for="pageNumber in numPages" :key="pageNumber" class="page-item" :class="{ active: pageNumber === currentPage }">
        <a class="page-link" href="#" @click="emitSetPage(pageNumber)">
          {{ pageNumber }}
        </a>
      </li>
      <li class="page-item" :class="{ disabled: !canNext }">
        <a class="page-link" href="#"
           @click="canNext && emit('set-page', nextPage())">
          Next
        </a>
      </li>
    </ul>
  </nav>
</template>
