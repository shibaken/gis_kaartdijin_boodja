<script lang="ts" setup>
  const props = defineProps<{
    field: string,
    name: string,
    values: Array<[string, string | number]>
    value?: string,
    classes?: string
  }>();
  const { field, name, values } = $(props);

  const emit = defineEmits<{
    (e: "value-updated", field: string, value: string): void
  }>();

  function valueUpdated (event: Event) {
    emit("value-updated", field, (event.target as HTMLInputElement).value);
  }
</script>

<template>
  <div class="form-floating">
    <select :id="`${field}Select`" :class="`form-select form-select-sm ${classes ?? ''}`"
            :aria-label="`${name} select`" @change="valueUpdated" :value="value">
      <option :value="null"></option>
      <option v-for="[optionName, optionValue] in values" :key="optionName" :value="optionValue">
        {{ optionName }}
      </option>
    </select>
    <label :for="`${field}Select`">{{ name }}</label>
  </div>
</template>

<style lang="scss">
  select {
    min-width: 7.5rem;
  }
</style>
