import { computed, ComputedRef, ref } from "vue";
import { Group, User } from "../backend/backend.api";
import { userProvider } from "../providers/userProvider";
import { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
import { catalogueEntryProvider } from "../providers/catalogueEntryProvider";

export function useEntryWorkflowComposable(catalogueEntry: CatalogueEntry) {

  const groups = ref<Group[]>([]);
  const users = ref<User[]>([]);
  const me = ref<User>();
  userProvider.groups.then(result => groups.value = result.results);
  userProvider.users.then(result => users.value = result);
  userProvider.me.then(result => me.value = result);

  const currentEntry = ref<CatalogueEntry>(catalogueEntry);
  const hasLockPermissions = computed(() => (me.value && me.value?.id === currentEntry.value.assignedTo?.id) ||
      groups.value.findIndex(group => group.id === me.value?.id) >= 0);

  const canLock = computed(() => hasLockPermissions.value && ["Draft", "New Draft"]
    .indexOf(currentEntry.value.status.label) >= 0);

  const canUnlock = computed(() => {
    return hasLockPermissions.value && ["Locked", "Pending"].indexOf(currentEntry.value.status.label) >= 0;
  });

  const assignableUsers: ComputedRef<User[]> = computed(() => {
    return users.value;
  });

  async function lockClicked() {
    if (canLock.value && hasLockPermissions.value) {
      await catalogueEntryProvider.lock(currentEntry.value.id);
    } else if (canUnlock) {
      await catalogueEntryProvider.unlock(currentEntry.value.id);
    }
  }

  async function assignUser (userId?: number) {
    const uid = userId ?? me.value?.id;
    if (uid) {
      await catalogueEntryProvider.assignUser(currentEntry.value.id, uid);
    }
  }

  return { currentEntry, hasLockPermissions, canLock, canUnlock, lockClicked, assignableUsers, assignUser };
}