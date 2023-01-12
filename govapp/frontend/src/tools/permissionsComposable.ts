import { computed, ComputedRef, ref } from "vue";
import { Group, User } from "../backend/backend.api";
import { userProvider } from "../providers/userProvider";
import { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
import { catalogueEntryProvider } from "../providers/catalogueEntryProvider";

export function usePermissionsComposable(catalogueEntry?: CatalogueEntry) {
  const groups = ref<Group[]>([]);
  const users = ref<User[]>([]);
  const me = ref<User>();
  userProvider.groups.then(result => groups.value = result);
  userProvider.users.then(result => users.value = result);
  userProvider.me.then(result => me.value = result);

  const currentEntry = ref<CatalogueEntry | undefined>(catalogueEntry);
  const isAdmin = (user: User) => !!user.groups.find(group => group.name === "Administrator");
  const isEntryEditor = (user: User) => {
    if (!currentEntry.value) {
      calledWithoutEntry("isEntryEditor");
    }
    return !!currentEntry.value?.editors.find(editor => editor.id === user.id);
  }

  const inEditorGroup = (user: User) => !!user.groups.find(group => group.name === "Catalogue Editor");

  const isAssigned = (user: User) => {
    if (!currentEntry.value) {
      calledWithoutEntry("isAssigned");
    }
    return user.id === currentEntry.value?.assignedTo?.id;
  };

  const userCanLock = (user: User | undefined) => {
    let canLock: boolean = false;
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

  const canAssign = computed(() => userCanAssign(me.value));

  const canLock = computed(() => {
    return !!currentEntry.value && userCanLock(me.value) &&
      ["Draft", "New Draft"].indexOf(currentEntry.value.status.label) >= 0;
  });

  const canUnlock = computed(() => {
    if (!currentEntry.value) {
      calledWithoutEntry("canUnlock");
    }
    return !!currentEntry.value && userCanLock(me.value) &&
      ["Locked", "Pending"].indexOf(currentEntry.value?.status.label) >= 0;
  });

  const assignableUsers: ComputedRef<User[]> = computed(() => users.value.filter(user => userCanAssign(user)));

  async function lockClicked () {
    if (!currentEntry.value) {
      calledWithoutEntry("lockClicked");
    } else if (canLock.value) {
      await catalogueEntryProvider.lock(currentEntry.value.id);
    } else if (canUnlock) {
      await catalogueEntryProvider.unlock(currentEntry.value.id);
    }
  }

  async function declineClicked () {
    if (!currentEntry.value) {
      calledWithoutEntry("declineClicked");
    } else if (canLock) { // `canDecline` has the same permission requirements as `canLock`
      await catalogueEntryProvider.decline(currentEntry.value.id)
    }
  }

  async function assignUser (userId?: number) {
    const uid = userId;

    if (!currentEntry.value) {
      calledWithoutEntry("assignUser");
    } else if (uid) {
      await catalogueEntryProvider.assignUser(currentEntry.value.id, uid);
    } else {
      await catalogueEntryProvider.unassignUser(currentEntry.value.id);
    }
  }

  async function assignMe () {
    if (!currentEntry.value) {
      calledWithoutEntry("assignMe");
    } else if (me.value) {
      await catalogueEntryProvider.assignUser(currentEntry.value.id, me.value.id);
    }
  }
  
  function updateCurrentEntry (newEntry: CatalogueEntry | undefined) {
    currentEntry.value = newEntry;
  }

  function calledWithoutEntry (method: string) {
    console.warn(`\`${method}\`: CatalogueEntry was not set in the permissions composable.`);
  }
  
  return { currentEntry, hasLockPermissions, canLock, canUnlock, lockClicked, assignableUsers, assignUser, assignMe,
  canAssign, declineClicked, updateCurrentEntry };
}