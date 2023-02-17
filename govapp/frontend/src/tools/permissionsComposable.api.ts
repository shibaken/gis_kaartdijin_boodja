import { ComputedRef, Ref } from "vue";
import { User } from "../backend/backend.api";
import { CatalogueEntry } from "../providers/catalogueEntryProvider.api";
import { PublishEntry } from "../providers/publisherProvider.api";

export interface PermissionsComposable {
  hasLockPermissions: ComputedRef<boolean>;
  isAdmin: (_user?: User, _me?: boolean) => boolean;
  isEntryEditor: (entry: CatalogueEntry | PublishEntry, user?: User) => boolean;
  isCurrentEntryEditor: (_user?: User, _me?: boolean) => boolean;
  canLock: ComputedRef<boolean>;
  canUnlock: ComputedRef<boolean>;
  canAssign: ComputedRef<boolean>;
  assignableUsers: ComputedRef<User[]>;
  lockClicked: () => void;
  declineClicked: () => void;
  currentEntry: Ref<CatalogueEntry | PublishEntry | undefined>;
  assignUser: (userId?: number) => void;
  assignMe: () => void;
  updateCurrentEntry: (newEntry: CatalogueEntry | PublishEntry | undefined) => void;
  isLoggedInUserAdmin: ComputedRef<boolean>
}