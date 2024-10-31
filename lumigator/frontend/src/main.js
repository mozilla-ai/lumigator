import '@/styles/app.scss';
// main.js
import { createApp } from 'vue';
import App from './App.vue';
import PrimeVue from 'primevue/config';

import LumiPreset from './libs/primevue.config.js';
const app = createApp(App);

app.use(PrimeVue, {
  theme: {
		preset: LumiPreset,
		options: {
			prefix: 'l',
			darkModeSelector: '.l-always-dark',
			cssLayer: true
		}
  },
});

app.mount('#app');
