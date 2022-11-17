import { PaginationFilter } from "./providerCommon.api";

export interface UserFilter extends PaginationFilter {
  ids?: Array<number>
  usernames?: Array<string>
}
