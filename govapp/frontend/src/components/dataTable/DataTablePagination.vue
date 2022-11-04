<script lang="ts" setup>
  const props = defineProps<{
    currentPage: number,
    numPages: number,
    pageSize: number,
    total: number
  }>();
  const { total } = $(props);

  const emit = defineEmits<{
    (e: "set-page", pageNumber: number): void
  }>();
</script>

<template>
  <span v-if="total > 0" class="ms-2 small fw-bold">
    Showing {{ ( currentPage - 1 ) * pageSize + 1 }} to {{ (currentPage) * pageSize }} of {{ total }} entries
  </span>
  <span v-else class="ms-2 small fw-bold">No results</span>
  <nav aria-label="Table navigation" class="d-flex justify-content-end">
    <ul class="pagination">
      <li class="page-item">
        <a class="page-link" href="#" @click="currentPage > 1 && emit('set-page', currentPage - 1)">
          Previous
        </a>
      </li>
      <li v-for="pageNumber in numPages" :key="pageNumber" class="page-item" :class="{ active: pageNumber === currentPage }">
        <a class="page-link" href="#" @click="emit('set-page', pageNumber)">
          {{ pageNumber }}
        </a>
      </li>
      <li class="page-item">
        <a
class="page-link" href="#"
           @click="currentPage < numPages && emit('set-page', currentPage + 1)">
          Next
        </a>
      </li>
    </ul>
  </nav>
</template>
