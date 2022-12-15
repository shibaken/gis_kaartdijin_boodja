import { computed, ComputedRef, ref } from "vue";
import { Group, User } from "../backend/backend.api";
import { userProvider } from "../providers/userProvider";
import { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
import { catalogueEntryProvider } from "../providers/catalogueEntryProvider";

export function useEntryWorkflowComposable(catalogueEntry: CatalogueEntry) {

  const groups = ref<Group[]>([]);
  const users = ref<User[]>([]);
  const me = ref<User>();
  userProvider.groups.then(result => groups.value = result);
  userProvider.users.then(result => users.value = result);
  userProvider.me.then(result => me.value = result);

  const currentEntry = ref<CatalogueEntry>(catalogueEntry);
  const isAdmin = (user: User) => !!user.groups.find(group => group.name === "Administrator");
  const isEntryEditor = (user: User) => !!catalogueEntry.editors.find(editor => editor.id === user.id);
  const inEditorGroup = (user: User) => !!user.groups.find(group => group.name === "Catalogue Editor");
  const isAssigned = (user: User) => user.id === catalogueEntry.assignedTo?.id;

  const userCanLock = (user: User | undefined) => {
    let canLock = false;
    if (user) {
      canLock = isAdmin(user) || inEditorGroup(user) && isEntryEditor(user) && isAssigned(user);
    }
    return canLock;
  }

  const userCanAssign = (user: User | undefined) => {
    let assignable = false;
    if (user) {
      assignable = isAdmin(user) || inEditorGroup(user) && isEntryEditor(user);
    }
    return assignable;
  }


  const hasLockPermissions = computed(() => userCanLock(me.value));

  const canLock = computed(() =>  userCanLock(me.value) &&
    ["Draft", "New Draft"].indexOf(currentEntry.value.status.label) >= 0);

  const canUnlock = computed(() =>  userCanLock(me.value) &&
    ["Locked", "Pending"].indexOf(currentEntry.value.status.label) >= 0);

  const assignableUsers: ComputedRef<User[]> = computed(() => users.value.filter(user => userCanAssign(user)));

  async function lockClicked() {
    if (canLock.value) {
      await catalogueEntryProvider.lock(currentEntry.value.id);
    } else if (canUnlock) {
      await catalogueEntryProvider.unlock(currentEntry.value.id);
    }
  }

  async function assignUser (userId?: number) {
    const uid = userId;
    if (uid) {
      await catalogueEntryProvider.assignUser(currentEntry.value.id, uid);
    } else {
      await catalogueEntryProvider.unassignUser(currentEntry.value.id);
    }
  }

  async function assignMe () {
    if (me.value) {
      await catalogueEntryProvider.assignUser(currentEntry.value.id, me.value.id);
    }
  }

  return { currentEntry, hasLockPermissions, canLock, canUnlock, lockClicked, assignableUsers, assignUser, assignMe };
}