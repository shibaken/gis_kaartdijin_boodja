import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
// Boot strap import not required as its imported in the main template
// import 'bootstrap/dist/css/bootstrap.min.css';
//import 'bootstrap';

const pinia = createPinia();
const app = createApp(App);

app.use(pinia)
  .mount('#app');
