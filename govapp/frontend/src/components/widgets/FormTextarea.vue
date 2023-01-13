<script lang="ts" setup>
  const props = defineProps<{
    field: string,
    name: string,
    value?: string,
    placeholder?: string,
    classes?: string,
    readonly?: boolean
  }>();

  const emit = defineEmits<{
    (e: "value-updated", field: string, value: string): void
  }>();

  function valueUpdated (event: Event) {
    emit("value-updated", props.field, (event.target as HTMLTextAreaElement).value);
  }
</script>

<template>
    <div class="form-floating">
      <textarea :id="`${field}Textarea`" class="form-control" :class="`h-auto ${classes}`" :placeholder="placeholder" rows="8"
                :readonly="readonly" :value="value" @input="valueUpdated"/>
      <label :for="`${field}Textarea`" class="w-max-content">{{ name }}</label>
    </div>
</template>

<style scoped lang="scss">
  div.form-floating > label {
    width: max-content;
  }
</style>
