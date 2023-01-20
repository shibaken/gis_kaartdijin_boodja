<script lang="ts" setup>
  const props = withDefaults(defineProps<{
    field: string,
    name: string,
    values: Array<[string, string | number]>
    value?: string,
    classes?: string,
    disabled?: boolean,
    isInvalid?: boolean,
    showEmpty?: boolean
  }>(),
    {
      classes: ""
    });
  const { field, name, values } = $(props);

  const emit = defineEmits<{
    (e: "value-updated", field: string, value: string): void
  }>();

  function valueUpdated (event: Event) {
    emit("value-updated", field, (event.target as HTMLInputElement).value);
  }
</script>

<template>
  <div class="form-floating mt-2">
    <select :id="`${field}Select`" class="form-select"
            :class="{ [classes]: !!classes, 'is-invalid': !!isInvalid }" :aria-label="`${name} select`"
            @change="valueUpdated" :value="value" :disabled="disabled">
      <option v-if="showEmpty" :value="null"></option>
      <option v-for="[optionName, optionValue] in values" :key="optionName" :value="optionValue">
        {{ optionName }}
      </option>
    </select>
    <label :for="`${field}Select`">{{ name }}</label>
  </div>
</template>

<style lang="scss">
  .form-floating {
    > label {
      width: max-content;
    }
    > select {
      width: 13rem;
    }
  }
</style>
