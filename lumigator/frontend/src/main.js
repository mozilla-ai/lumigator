import '@/styles/app.scss';
import { createApp } from 'vue';
import Tooltip from 'primevue/tooltip';
import App from './App.vue';
import { createPinia } from 'pinia';
import router from '@/router';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';
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
app.use(ConfirmationService);
app.use(ToastService);
app.directive('tooltip', Tooltip);
app.mount('#app');
