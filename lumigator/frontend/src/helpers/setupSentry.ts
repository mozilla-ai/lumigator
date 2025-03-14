import { SENTRY_CONSENT_LOCAL_STORAGE_KEY } from '@/composables/useSentryConsent'
import { browserTracingIntegration, init, replayIntegration } from '@sentry/vue'
import type { App } from 'vue'
import type { Router } from 'vue-router'

export function setupSentry(app: App<Element>, router: Router) {
  const consent = window.localStorage.getItem(SENTRY_CONSENT_LOCAL_STORAGE_KEY)

  if (consent === 'true') {
    return init({
      app,
      dsn: import.meta.env.VITE_APP_LUMIGATOR_SENTRY_DSN,
      integrations: [browserTracingIntegration({ router }), replayIntegration()],
      beforeSend(event) {
        console.log(event)
        const consent = window.localStorage.getItem(SENTRY_CONSENT_LOCAL_STORAGE_KEY)
        if (!consent) {
          return null
        } else {
          return event
        }
      },
      // Tracing
      // tracesSampleRate: 1.0, //  Capture 100% of the transactions
      // Set 'tracePropagationTargets' to control for which URLs distributed tracing should be enabled
      // tracePropagationTargets: ["localhost", /^https:\/\/yourserver\.io\/api/],
      // Session Replay
      // replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
      // replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
    })
  }
}
