<script lang="ts" setup>
  import PlusCircleFill from '../icons/plusCircleFill.vue';

  defineProps<{ id: number }>()
</script>

<template>
  <tr data-bs-toggle="collapse" :data-bs-target="`#row-${id}`">
    <th scope="row"><PlusCircleFill colour="#4284BC" class="me-2"/></th>
    <slot name="cells"/>
  </tr>
  <tr class="collapse accordion-collapse" :id="`row-${id}`" data-bs-parent=".table">
    <slot name="content"/>
  </tr>
</template>
