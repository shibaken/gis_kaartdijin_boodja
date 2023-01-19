<script lang="ts" setup>
  import DataTablePagination from "./DataTablePagination.vue";
  import FormSelect from "../widgets/FormSelect.vue";
  import { ref, Ref } from "vue";
  import FormInput from "../widgets/FormInput.vue";

  const props = withDefaults(defineProps<{
    total: number,
    paginate: boolean
  }>(), {
    total: 0,
    paginate: true
  });

  const pageSize: Ref<number> = ref(10);

  const emit = defineEmits<{
    (e: "set-page", pageNumber: number): void
    (e: "set-page-size", pageSize: number): void
  }>();

  function setPage (page: number) {
    emit('set-page', page);
  }

  function setPageSize (_: string, page: string) {
    pageSize.value = parseInt(page);
    emit('set-page-size', parseInt(page));
  }
</script>

<template>
  <slot v-if="paginate" name="settings">
    <div class="pre-table-row mb-2">
      <form-select name="Page Size" field="pageSize" :value="pageSize.toString()"
                 :values="[['10', 10], ['50', 50], ['100', 100]]" :show-empty="false"
                 @value-updated="setPageSize"/>
      <form-input class="d-flex align-content-end" field="search" name="Search" type="string"/>
    </div>
  </slot>
  <div class="table-responsive">
    <table class="table table-bordered table-hover accordion mb-1">
      <thead>
        <slot name="headers"/>
      </thead>
      <tbody>
        <slot name="data"/>
      </tbody>
    </table>
  </div>
  <slot v-if="paginate" name="pagination">
    <DataTablePagination :total="total" :page-size="pageSize" @set-page="setPage"/>
  </slot>
</template>

<style lang="scss">
  .pre-table-row {
    display: grid;
    grid-auto-flow: column;

    div.form-floating:last-child {
      justify-self: flex-end;
    }
  }
</style>
