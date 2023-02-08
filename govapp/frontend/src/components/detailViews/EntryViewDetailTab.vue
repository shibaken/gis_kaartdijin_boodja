<script lang="ts" setup>
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import Accordion from "../widgets/Accordion.vue";
  import FormInput from "../widgets/FormInput.vue";
  import FormTextarea from "../widgets/FormTextarea.vue";
  import NotificationsCard from "../widgets/NotificationsCard.vue";
  import { usePermissionsComposable } from "../../tools/permissionsComposable";
  import { computed, onMounted, Ref, ref } from "vue";
  import { catalogueEntryProvider } from "../../providers/catalogueEntryProvider";
  import { CatalogueDetailViewTabs, CatalogueTab, CatalogueView, NavigationEmits } from "../viewState.api";
  import WorkflowFooter from "../widgets/WorkflowFooter.vue";
  import FormSelect from "../widgets/FormSelect.vue";
  import { userProvider } from "../../providers/userProvider";
  import { Custodian } from "../../providers/userProvider.api";

  const props = defineProps<{
    entry: CatalogueEntry
  }>();

  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();

  const editingEntry: Ref<CatalogueEntry> = ref(props.entry);

  async function onSave (exit: boolean) {
    await catalogueEntryProvider.updateCatalogueEntry(editingEntry.value.id, editingEntry.value);

    if (exit) {
      emit('navigate', CatalogueTab.CatalogueEntries, CatalogueView.List);
    } else {
      emit('navigate', CatalogueTab.CatalogueEntries, CatalogueView.View, {
        viewTab: CatalogueDetailViewTabs.AttributeTable,
        recordId: props.entry.id
      });
    }
  }

  function onValueUpdate (field: string, value: string | number) {
    editingEntry.value = { ...editingEntry.value, [field]: value};
  }

  function onCustodianUpdate (field: string, value: string) {
    let custodian: Custodian | undefined = custodians.value.find(cust => cust.id === parseInt(value));

    editingEntry.value = { ...editingEntry.value, [field]: custodian};
  }

  function onReset () {
    editingEntry.value = props.entry;
  }

  const { isLoggedInUserEditor, isLoggedInUserAdmin } = usePermissionsComposable();
  const canEdit = computed(() => isLoggedInUserAdmin || isLoggedInUserEditor);

  const custodians: Ref<Custodian[]> = ref([]);
  onMounted(async () => {
    custodians.value = await userProvider.fetchCustodians();
  });
</script>

<template>
  <accordion id-prefix="details" header-text="Details" class="mt-4">
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <form-input field="name" name="Name" :value="entry.name" type="text" :readonly="!canEdit"
                    @value-updated="onValueUpdate"/>
        <form-select field="custodian" name="Custodian" :values="custodians.map(cust => [cust.name, cust.id])"
                     :value="entry.custodian?.id.toString()" type="text" :show-empty="true"
                     :readonly="!canEdit" @value-updated="onCustodianUpdate"/>
      </div>
    </template>
  </accordion>
  <accordion id-prefix="description" header-text="Description" class="mt-4">
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <form-textarea field="description" name="Description" :value="entry.description"
                       :readonly="!canEdit" @value-updated="onValueUpdate"/>
      </div>
    </template>
  </accordion>
  <notifications-card :entry="entry"/>
  <workflow-footer :disabled="!canEdit" @reset="onReset" @save-continue="onSave(false)" @save-exit="onSave(true)"/>
</template>
