<script lang="ts" setup async>
  import DataTable from "./DataTable.vue";
  import { Attribute } from "../../providers/relatedEntityProvider.api";
  import { NavigationEmits } from "../viewState.api";
  import { ModalTypes } from "../../stores/ModalStore.api";
  import { useModalStore } from "../../stores/ModalStore";
  import { useAttributeStore } from "../../stores/AttributeStore";
  import { computed, ComputedRef } from "vue";
  import { storeToRefs } from "pinia";
  import { AttributeCrudType } from "../../stores/AttributeStore.api";

  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();

  const modalStore = useModalStore();
  const attributeStore = useAttributeStore();
  const { attributes, editingAttribute, attributeCrudType } = storeToRefs(attributeStore);

  const filteredAttributes: ComputedRef<Attribute[]> = computed(() => {
    const filtered = attributes.value.filter(attribute => attribute.id !== editingAttribute.value?.id);
    if (editingAttribute.value) {
      filtered.concat([editingAttribute.value as Attribute]);
    }
    return filtered;
  });

  function onEditClick (attribute: Attribute) {
    editingAttribute.value = attribute;
    attributeCrudType.value = AttributeCrudType.Edit;
    modalStore.showModal(ModalTypes.ATTRIBUTE_EDIT);
  }

  function onDeleteClick (attribute: Attribute) {
    editingAttribute.value = attribute;
    attributeCrudType.value = AttributeCrudType.Delete;
    modalStore.showModal(ModalTypes.ATTRIBUTE_DELETE);
  }

  function onEditEditingClick () {
    modalStore.showModal(ModalTypes.ATTRIBUTE_EDIT);
    attributeCrudType.value = AttributeCrudType.Edit;
  }

  function onClearClick () {
    editingAttribute.value = undefined;
    attributeCrudType.value = AttributeCrudType.None;
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
      <tr v-if="filteredAttributes.length > 0" v-for="(row, index) in filteredAttributes" :key="index">
        <td>{{ row.id }}</td>
        <td>{{ row.name }}</td>
        <td>{{ row.type }}</td>
        <td>{{ row.order }}</td>
        <td>
          <a href="#" class="me-2" @click="onEditClick(row)">Edit</a>
          <a href="#" @click="onDeleteClick(row)">Delete</a>
        </td>
      </tr>
      <tr v-if="editingAttribute" :class="{
        'table-info': attributeCrudType === AttributeCrudType.Edit,
        'table-danger': attributeCrudType === AttributeCrudType.Delete,
        'table-success': attributeCrudType === AttributeCrudType.New
      }">
        <td>{{ editingAttribute.id || "" }}</td>
        <td>{{ editingAttribute.name }}</td>
        <td>{{ editingAttribute.type }}</td>
        <td>{{ editingAttribute.order }}</td>
        <td>
          <a href="#" class="me-2" @click="onEditEditingClick">Edit</a>
          <a href="#" @click="onClearClick">Clear</a>
        </td>
      </tr>
    </template>
  </data-table>
</template>
