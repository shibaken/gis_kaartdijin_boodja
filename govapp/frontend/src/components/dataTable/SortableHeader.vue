<script setup lang="ts">
  import IconArrowhead from "../../icons/IconArrowhead.vue";
  import { SortDirection } from "../viewState.api";

  const props = withDefaults(
    defineProps<{
      column: string,
      name: string,
      direction: SortDirection,
      altField?: string
    }>(),
    { direction: SortDirection.None }
  );

  const emit = defineEmits<{
    (e: "sort", column: string): void
  }>();

  function onSortClicked () {
    emit('sort', props.altField ?? props.column);
  }
</script>

<template>
  <th @click="onSortClicked">
    <div class="d-flex">
      <span class="me-2" :title="name">{{name}}</span>
      <div class="chevron-container ms-auto">
        <div class="chevron" :class="{
            'sort-chevron-selected': direction === SortDirection.Ascending,
            'sort-chevron': direction !== SortDirection.Ascending
        }">
          <IconArrowhead/>
        </div>
        <div class="chevron" :class="{
          'sort-chevron-selected': direction === SortDirection.Descending,
          'sort-chevron': direction !== SortDirection.Descending
        }">
          <IconArrowhead/>
        </div>
      </div>
    </div>
  </th>
</template>
<style lang="scss">
  .chevron-container {
    margin-top: -.25rem;
    .chevron {
      height: .5rem;
      &:first-child {
        svg {
          transform: rotate(180deg);
        }
      }

      &.sort-chevron svg #Icons :is(line, path, circle, polyline) {
        stroke: currentColor;
        fill: currentColor;
        color: #E6E6E6;
      }

      &.sort-chevron-selected svg #Icons :is(line, path, circle, polyline) {
        stroke: currentColor;
        fill: currentColor;
        color: #B5B5B5;
      }
    }
  }
</style>
