<script lang="ts" setup async>
  import DataTable from "./DataTable.vue";
  import { Attribute } from "../../providers/relatedEntityProvider.api";
  import { NavigationEmits } from "../viewState.api";
  import { ModalTypes } from "../../stores/ModalStore.api";
  import { useModalStore } from "../../stores/ModalStore";
  import { useAttributeStore } from "../../stores/AttributeStore";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";

  const props = defineProps<{
    attributes: Array<Attribute>
  }>();

  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();

  const modalStore = useModalStore();
  const attributeStore = useAttributeStore();

  function onEditClick (attribute: Attribute) {
    attributeStore.editingAttribute = attribute;
    modalStore.showModal(ModalTypes.ATTRIBUTE_EDIT);
  }

  function onDeleteClick (id: number) {
    attributeStore.editingAttribute = { id };
    modalStore.showModal(ModalTypes.ATTRIBUTE_DELETE);
  }
</script>

<template>
  <data-table :paginate="false">
    <template #headers>
      <tr>
        <th>Number</th>
        <th>Name</th>
        <th>Type</th>
        <th>Order</th>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <tr v-for="(row, index) in attributes" :key="index">
        <td>{{ row.id }}</td>
        <td>{{ row.name }}</td>
        <td>{{ row.type }}</td>
        <td>{{ row.order }}</td>
        <td>
          <a href="#" class="me-2" @click="onEditClick(row)">Edit</a>
          <a href="#" @click="onDeleteClick(row.id)">Delete</a>
        </td>
      </tr>
    </template>
  </data-table>
</template>
