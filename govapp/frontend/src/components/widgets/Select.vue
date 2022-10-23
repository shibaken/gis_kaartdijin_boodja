<script lang="ts" setup>
  import { toCamelCase } from '../../util/strings';

  const { name, values, value = '' } = defineProps<{
    name: string,
    values: Array<string>
    value?: string
  }>();

  const emit = defineEmits<{
    (e: 'value-updated', name: string, value: string): void
  }>()

  function valueUpdated (event: Event) {
    emit('value-updated', name, (event.target as HTMLInputElement).value);
  }
</script>

<template>
  <div class="form-floating">
    <select :id="`${toCamelCase(name)}Select`" class="form-select form-select-sm w-auto" aria-label="{{ name }} select"
            @change="valueUpdated">
      <option :value="null"></option>
      <option v-for="value in values" :value="toCamelCase(name)">{{ value }}</option>
    </select>
    <label :for="`${toCamelCase(name)}Select`">{{ name }}</label>
  </div>
</template>

<style lang="scss">
  select {
    min-width: 7.5rem;
  }
</style>
