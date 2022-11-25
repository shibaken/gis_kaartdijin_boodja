import { PaginationFilter } from "./providerCommon.api";

export interface UserFilter extends PaginationFilter {
  ids?: Array<number>
  usernames?: Array<string>
}

export interface Custodian {
  id:	number;
  name:	string;
  description?: string;
  contactName?: string;
  contactEmail?: string;
  contactPhone?: string;
}