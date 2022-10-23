<script lang="ts" setup>
  import { toCamelCase } from '../../util/strings';

  const { name, value = '', placeholder, type } = defineProps<{
    name: string,
    value?: string,
    placeholder?: string,
    type: string | undefined
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
    <input :id="`${toCamelCase(name)}Input`" :type="type" class="form-control w-auto" :placeholder="placeholder"
           @change="valueUpdated">
    <label :for="`${toCamelCase(name)}Input`">{{ name }}</label>
  </div>
</template>
