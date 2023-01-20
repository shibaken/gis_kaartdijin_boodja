import { defineStore } from "pinia";
import { ref } from "vue";
import { ModalTypes } from "./ModalStore.api";

export const useModalStore = defineStore("modal",  () => {
  const activeModal = ref<ModalTypes>(ModalTypes.NONE);

  function showModal (modal: ModalTypes) {
    activeModal.value = modal;
  }

  function hideModal () {
    activeModal.value = ModalTypes.NONE;
  }

  return { activeModal, showModal, hideModal };
});
