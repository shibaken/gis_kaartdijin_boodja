# Kaartdijin Boodja frontend
 - Vue 3 composition API
 - Pinia
 - Bootstrap 5.2

## Architecture
Instruction flows from component to API and back:
Component --> Provider --> Backend --> API
Component <-- Provider <-- Backend <--

Information should likewise flow from higher to lower layers:
 - Vue components request presentation-ready information from the data providers,
 - Providers build `Backend` request filters, construct complex data structures, normalise property names, and resolve nested foreign keyed properties from raw `Backend` data types
 - Backend methods fetch the raw data from the API and simply handle conversion of payloads to an appropriate format

Information should not flow upstream. This includes knowledge of types. The `Backend` should never need to reference any `Provider` or `Component` type or method.

### Typing in Typescript
It's strongly advised that you be as narrow and specific as possible when typing, avoid using type assertions (`!`, `niceSafe = maybeUnsafe as <NiceSafeType>`) or `unknown`s, and avoid `any` like the plague.
This will catch the majority of errors before they're committed.
Unsafe type assertions should generally only occur when introducing data from an external source ie. and API, where it should be checked for validity.

### Component / presentation layer
Components such as datatables, modals, sortable headers, etc. are as generic and reusable as possible.
Stores are used where state can't be contained within one component or in a straight hierarchical line between a child, and it's ancestor.
There are also composables for reusing common functionality such as filters.


### Provider
The guts of application. Mediates between the presentation layer and the backend.
Types are provided in adjacent .api.ts files of the same name.

### Backend
Handles the API calls.
Use the `fetcher` wrapper to send `PATCH`, `POST`, or `DELETE` requests

### Stores
Pinia stores hold global component state, entries from the API, and record caches.
See gotchas: `storeToRefs` in https://pinia.vuejs.org/core-concepts/

### Navigation
Navigation is somewhat inconsistent because not all the app frontend exists inside the SPA.
Navigation between the `Catalogue` and `Publisher` is handled by listening for `hashchange` events in the URL. This stops the page from reloading and wiping the state.
Within these two pages, navigation is handles by setting the appropriate view, tab, and mode in the ViewState and passing it to child components.


## Development checklist
 - Start the python backend
 - Start the dev server `npm dev`
 - Add any new backend methods to `backend.stub.ts`
 - Run `npm run dev-mock` (Allows running without a backend, however presently there is a bug and the bootstrap dependency needs to be moved from Django to Vue)
 - Run `npm build` (The frontend can't be run in prod if the build fails)
 - Run `npm run lint`