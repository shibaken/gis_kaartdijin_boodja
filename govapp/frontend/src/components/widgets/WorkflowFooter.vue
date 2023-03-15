<script lang="ts" setup>
  withDefaults(defineProps<{
    disabled: boolean,
    continueDisabled: boolean
  }>(), {
    disabled: false,
    continueDisabled: false
  });

  const emit = defineEmits<{
    (e: "save-exit"): void,
    (e: "save-continue"): void,
    (e: "reset"): void
  }>();
</script>

<template>
  <div class="footer-buttons mt-3">
    <button type="button" class="reset-button btn btn-outline-danger mx-1" :disabled="disabled"
            @click="emit('reset')">Reset</button>
    <button v-if="!continueDisabled" type="button" class="save-button btn btn-primary mx-1" :disabled="disabled"
            @click="emit('save-continue')">Save and Continue</button>
    <button type="button" class="save-button btn btn-primary mx-1" :disabled="disabled"
            @click="emit('save-exit')">Save and Exit</button>
  </div>
</template>

<style lang="scss">
  div.footer-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    .delete-button,
    .reset-button {
      justify-self: flex-start;
    }
    .save-button {
      justify-self: flex-end;
    }
  }
</style>