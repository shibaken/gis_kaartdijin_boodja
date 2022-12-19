import { ComputedRef, Ref } from "vue";
import { User } from "../backend/backend.api";
import { CatalogueEntry } from "../providers/catalogueEntryProvider.api";

export interface WorkFlowComposable {
  hasLockPermissions: ComputedRef<boolean>;
  canLock: ComputedRef<boolean>;
  canUnlock: ComputedRef<boolean>;
  canAssign: ComputedRef<boolean>;
  assignableUsers: ComputedRef<User[]>;
  lockClicked: () => void;
  declineClicked: () => void;
  currentEntry: Ref<CatalogueEntry>;
  assignUser: (userId?: number) => void;
  assignMe: () => void;
}