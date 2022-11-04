<script lang="ts" setup>
  import PlusCircleFill from "../icons/plusCircleFill.vue";

  const props = defineProps<{ id: number }>();
  const { id } = $(props);
</script>

<template>
  <tr data-bs-toggle="collapse" :data-bs-target="`#row-${id}`">
    <th scope="row"><PlusCircleFill colour="#4284BC" class="me-2" /></th>
    <slot name="cells" />
  </tr>
  <tr :id="`row-${id}`" class="collapse accordion-collapse" data-bs-parent=".table">
    <slot name="content" />
  </tr>
</template>
