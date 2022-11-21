import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";

/** Note: Bootstrap *must* be loaded into the SPA at least while running with mock data. `mock-dev` mocks the backend
 * API and with no backend serving the html containing the Bootstrap library, there's no styling.
 * This is not ideal. Bootstrap and the nav bar should reside *within the frontend* to avoid further dependency issues.
 */
if (import.meta.env.MODE === "mock") {
  import("bootstrap/dist/css/bootstrap.min.css");
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  import("bootstrap");
}

const pinia = createPinia();
const app = createApp(App);

app.use(pinia)
  .mount("#app");
