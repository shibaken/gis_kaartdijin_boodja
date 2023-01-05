<script lang="ts" setup async>
  import DataTable from "./DataTable.vue";
  import { Attribute } from "../../providers/relatedEntityProvider.api";

  const props = defineProps<{
    attributes: Array<Attribute>
  }>();
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
          <a href="#" class="me-2">Edit</a>
          <a href="#">Delete</a>
        </td>
      </tr>
    </template>
  </data-table>
</template>
