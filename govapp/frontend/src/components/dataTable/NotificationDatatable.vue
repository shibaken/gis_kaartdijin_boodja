<script lang="ts" setup async>
  import DataTable from "./DataTable.vue";
  import { storeToRefs } from "pinia";
  import { onMounted } from "vue";
  import { useNotificationStore } from "../../stores/NotificationStore";

  const notificationStore = useNotificationStore();
  // get Stores and fetch with `storeToRef` to
  const { getNotifications } = notificationStore;
  const { allNotifications } = storeToRefs(notificationStore);

  onMounted(() => {
    getNotifications();
  });
</script>

<template>
  <data-table>
    <template #headers>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>URL</th>
        <th>Type</th>
        <th>Action</th>
      </tr>
    </template>
    <template #data>
      <tr v-for="(row, index) in allNotifications" :id="index" :key="index">
          <td>{{ row.name }}</td>
          <td>{{ row.email }}</td>
          <td>{{ row.url }}</td>
          <td>{{ row.type.label }}</td>
          <td>
            <a href="#" class="me-2">Edit</a>
            <a href="#">Disable/Enable</a>
          </td>
      </tr>
    </template>
  </data-table>
</template>
