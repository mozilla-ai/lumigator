import '@/styles/app.scss';
// main.js
import { createApp } from 'vue';
import App from './App.vue';

import PrimeVue from 'primevue/config';

const app = createApp(App);
app.use(PrimeVue);
app.mount('#app');
