<script lang="ts" setup>
  import Modal from "../../components/widgets/Modal.vue";
  import CommunicationsLogDatatable from "../dataTable/CommunicationsLogDatatable.vue";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import CommunicationsLogAddForm from "../detailViews/CommunicationsLogAddForm.vue";
  import { useModalStore } from "../../stores/ModalStore";
  import { ref, Ref } from "vue";
  import { CommunicationLog } from "../../providers/logsProvider.api";
  import { logsProvider } from "../../providers/logsProvider";
  import { ModalTypes } from "../../stores/ModalStore.api";

  const props = defineProps<{
    show: boolean,
    catalogueEntry: CatalogueEntry,
    addLog: boolean
  }>();

  const modalStore = useModalStore();
  const formValues: Ref<Partial<CommunicationLog> | undefined> = ref();
  const formDirty = ref(false);

  async function saveLog() {
    formDirty.value = true;
    if (formValues.value) {
      await logsProvider.addCommunicationLog(props.catalogueEntry.id, formValues.value as CommunicationLog);
      modalStore.activeModal = ModalTypes.COMMS_LOG;
    }
  }

  function valuesUpdated (values: Partial<CommunicationLog>) {
    if (!formValues.value) {
      formValues.value = {};
    }
    formValues.value = values;
  }

  function onClose () {
    modalStore.hideModal();
    formDirty.value = false;
  }
</script>

<template>
  <Modal :show="show" modal-id="comms-log" :modal-size="addLog ? 'modal-lg' : 'modal-xl'" :show-save-button="addLog"
         :enable-save-button="true" @close="onClose" @save="saveLog">
    <template #header>
      <h1>Communications Log</h1>
    </template>
    <template #body v-if="catalogueEntry">
      <communications-log-datatable v-if="!addLog" :catalogue-entry="catalogueEntry"/>
      <communications-log-add-form v-if="addLog" @valid-value-updated="valuesUpdated" :form-dirty="formDirty"/>
    </template>
  </Modal>
</template>
