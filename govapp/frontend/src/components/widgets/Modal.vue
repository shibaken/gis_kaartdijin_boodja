<script lang="ts" setup>
  import { useModalStore } from "../../stores/ModalStore";

  const props = withDefaults(defineProps<{
      modalId: string,
      show: boolean,
      modalSize?: "modal-sm" | "modal-md" | "modal-lg" | "modal-xl",
      showSaveButton?: boolean,
      enableSaveButton?: boolean,
      saveButtonText?: string
    }>(),
    {
    enableSaveButton: true
  });

  const emit = defineEmits<{
    (e: "close"): void
    (e: "save"): void
  }>();

  const modalStore = useModalStore();

  function hide () {
    modalStore.hideModal();
  }
</script>

<template>
  <div :id="`modal-${modalId}`" class="modal fade" :class="{ 'show d-block': show }" tabindex="-1"
       aria-labelledby="modalLabel" aria-hidden="true" @click="hide">
    <div class="modal-dialog" :class="modalSize" @click.stop>
      <div class="modal-content">
        <div class="modal-header">
          <slot name="header">
            <h1 class="modal-title fs-5" id="modalLabel"></h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </slot>
        </div>
        <div class="modal-body">
          <slot name="body"/>
        </div>
        <div class="modal-footer">
          <slot name="footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" @click="emit('close')">Close</button>
            <button type="button" class="btn btn-primary" v-if="showSaveButton" @click="emit('save')"
                    :disabled="!enableSaveButton">
              {{ saveButtonText ?? "Save" }}
            </button>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>
