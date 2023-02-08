<script lang="ts" setup>
  const props = withDefaults(defineProps<{
      field: string,
      name: string,
      value?: string,
      placeholder?: string,
      type: string | undefined,
      classes?: string,
      readonly?: boolean,
      isInvalid?: boolean
    }>(),
    {
      classes: "",
      isInvalid: false
    });
  const { field, name, placeholder, type } = $(props);

  const emit = defineEmits<{
    (e: "value-updated", field: string, value: string | number): void,
    (e: "value-blurred", field: string, value: string | number): void
  }>();

  const classList: Record<string, boolean> = { 'is-invalid': props.isInvalid }
  if (props.classes) {
    classList[props.classes] = true;
  }

  function valueUpdated (event: Event) {
    emit("value-updated", field, (event.target as HTMLInputElement).value);
  }

  function valueBlurred (event: Event) {
    emit("value-blurred", field, (event.target as HTMLInputElement).value);
  }
</script>

<template>
    <div class="form-floating mt-2">
      <input :id="`${field}Input`" :type="type" class="form-control"
             :class="{ [classes]: !!classes, 'is-invalid': !!isInvalid }" :placeholder="placeholder" :readonly="readonly"
             :value="value" @change="valueUpdated" @blur="valueBlurred">
      <label :for="`${field}Input`" class="w-max-content">{{ name }}</label>
    </div>
</template>

<style scoped lang="scss">
  div.form-floating {
    > label {
      width: max-content;
    }
    input {
      width: 13rem;
    }
  }
</style>
