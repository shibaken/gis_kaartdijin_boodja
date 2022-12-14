import { defineStore } from "pinia";
import { ref } from "vue";
import { User } from "../backend/backend.api";

export const useUserStore = defineStore("user", () => {
  const users = ref<User[]>([]);

  return { users };
});