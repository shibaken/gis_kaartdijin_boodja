import { defineStore } from "pinia";
import { ref } from "vue";
import { ModalTypes } from "./ModalStore.api";

export const useModalStore = defineStore("modal",  () => {
  const activeModal = ref<ModalTypes>(ModalTypes.None);

  function showModal (modal: ModalTypes) {
    activeModal.value = modal;
  }

  function hideModal () {
    activeModal.value = ModalTypes.None;
  }

  return { activeModal, showModal, hideModal };
});
