import { BackendService } from "../backend/backend.service";
import { BackendServiceStub } from "../backend/backend.stub";
import { RawUserFilter, User } from "../backend/backend.api";
import { UserFilter } from "./userProvider.api";

export class UserProvider {
  // Get the backend stub if the test flag is used.
  private backend: BackendService = import.meta.env.MODE === "mock" ? new BackendServiceStub() : new BackendService();

  public async fetchUser (userId: number): Promise<User> {
    return await this.backend.getUser(userId);
  }

  public async fetchUsers ({ ids, usernames }: UserFilter): Promise<Array<User>> {
    const filters = {
      id__in: ids,
      username__in: usernames
    } as RawUserFilter;

    const users = await this.backend.getUsers(filters);
    return users.results;
  }

  // We don't need to paginate here so unwrap the results
  public static getUserFromId (userId: number | undefined, users: Array<User>): User | undefined {
    return userId !== null ? users.find(user => user.id === userId) : undefined;
  }

  public static getUniqueUsers (userObjects: Array<User>): Array<User> {
    return userObjects
      .reduce((previous, current) => {
        return current && previous.findIndex(value => value.id === current.id) === -1 ? [...previous, current] : previous;
      }, [] as Array<User>);
  }

  /**
   * Get list of unique `User` ids across multiple fields
   * @param userObjectList - An array of object containing column values e.g. `[{ custodian: 4, assignedTo: 5 }]`
   */
  public static getUniqueUserIds (userObjectList: Array<Record<string, number | undefined>>) {
    // Extract all keys and remove dupes
    return userObjectList
      .map(userObject => Array.from(Object.values(userObject)))
      .flat()
      .filter((value, index, self) => {
        return value !== null && self.indexOf(value) === index;
      }) as Array<number>;
  }
}
