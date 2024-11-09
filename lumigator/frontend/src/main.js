import '@/styles/app.scss';
// main.js
import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import router from '@/router';
import PrimeVue from 'primevue/config';

import LumiPreset from './libs/primevue.config.js';
const app = createApp(App);

app.use(router)
  .use(createPinia())
app.use(PrimeVue, {
  theme: {
		preset: LumiPreset,
		options: {
			prefix: 'l',
			darkModeSelector: '.l-always-dark',
			cssLayer: false
		}
  },
});

app.mount('#app');
