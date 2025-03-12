import '@/styles/app.scss'
import { createApp } from 'vue'
import Tooltip from 'primevue/tooltip'
import App from './App.vue'
import { createPinia } from 'pinia'
import { router } from '@/router'
import PrimeVue from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'
import { LumiPreset } from './primevue.config'
import { init, browserTracingIntegration, replayIntegration} from '@sentry/vue'
const app = createApp(App)

app
  .use(router)
  .use(createPinia())
  .use(PrimeVue, {
    theme: {
      preset: LumiPreset,
      options: {
        prefix: 'l',
        darkModeSelector: '.l-always-dark',
        cssLayer: false,
      },
    },
  })
  .use(ConfirmationService)
  .use(ToastService)
  .directive('tooltip', Tooltip)

init({
  app,
  dsn: import.meta.env.VITE_APP_LUMIGATOR_SENTRY_DSN,
  integrations: [
    browserTracingIntegration({ router }),
    replayIntegration(),
  ],
  beforeSend(event) {
    console.log(event)
    // Modify or drop the event here
    if (event.user) {
      // Don't send user's email address
      delete event.user.email;
      return event;
    } else {
      // drop the event
      return null;
    }
  },
   // Tracing
  tracesSampleRate: 1.0, //  Capture 100% of the transactions
  // Set 'tracePropagationTargets' to control for which URLs distributed tracing should be enabled
  tracePropagationTargets: ["localhost", /^https:\/\/yourserver\.io\/api/],
  // Session Replay
  replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
  replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
});

app.mount('#app')
setTimeout(() => {
  throw new Error('test')
}, 2000)
