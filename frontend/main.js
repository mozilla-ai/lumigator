import { createApp } from 'vue';
import App from './App.vue';
import quasar from './quasar';  // Import the quasar plugin setup
import router from './router';  // Import router
import store from './store';    // Import state management (Vuex or Pinia)

import 'quasar/src/css/index.sass'; // Optional: Quasar custom styles

createApp(App)
  .use(quasar)
  .use(router)
  .use(store)
  .mount('#app');
