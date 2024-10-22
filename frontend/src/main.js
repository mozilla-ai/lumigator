// main.js
import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import router from './router/index.js';
import quasar from './quasar'; // Import your Quasar configuration

import 'quasar/src/css/index.sass'; // Import Quasar styles

createApp(App)
  .use(createPinia())
  .use(router)
  .use(quasar)
  .mount('#app');
