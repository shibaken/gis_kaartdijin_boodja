<script lang="ts" setup>
  const props = defineProps<{
    field: string,
    name: string,
    value?: string,
    placeholder?: string,
    type: string | undefined
  }>();
  const { field, name, placeholder, type } = $(props);

  const emit = defineEmits<{
    (e: "value-updated", field: string, value: string): void
  }>();

  function valueUpdated (event: Event) {
    emit("value-updated", field, (event.target as HTMLInputElement).value);
  }
</script>

<template>
  <div class="form-floating">
    <input :id="`${field}Input`" :type="type" class="form-control w-auto" :placeholder="placeholder"
           @change="valueUpdated">
    <label :for="`${field}Input`" class="w-max-content">{{ name }}</label>
  </div>
</template>

<style scoped lang="scss">
  div.form-floating > label {
    width: max-content;
  }
</style>
