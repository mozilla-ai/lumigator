import { SENTRY_CONSENT_LOCAL_STORAGE_KEY } from '@/composables/useSentryConsent'
import { browserTracingIntegration, init, replayIntegration } from '@sentry/vue'
import type { App } from 'vue'
import type { Router } from 'vue-router'

export function setupSentry(app: App<Element>, router: Router) {
  const hasGivenConsent = window.localStorage.getItem(SENTRY_CONSENT_LOCAL_STORAGE_KEY) === 'true'
  const isProdBuild = import.meta.env.PROD

  if (hasGivenConsent && isProdBuild) {
    return init({
      app,
      sendDefaultPii: false, // Ensures Sentry doesn't auto-collect user PII
      dsn: import.meta.env.VITE_APP_LUMIGATOR_SENTRY_DSN,
      integrations: [browserTracingIntegration({ router }), replayIntegration()],
      beforeBreadcrumb(breadcrumb) {
        if (
          breadcrumb.message?.includes('/secrets') ||
          breadcrumb.data?.url?.includes('/secrets')
        ) {
          return { ...breadcrumb, message: '[REDACTED]' }
        }
        return breadcrumb
      },
      beforeSend(event) {
        if (event.request) {
          // Redact sensitive request details
          if (event.request.url?.includes('settings/secrets')) {
            event.request.data = '[REDACTED]'
            event.request.query_string = '[REDACTED]'
          }

          // Remove sensitive headers (We don't really have auth or api keys in our app, but this is here for future-proofing)
          if (event.request.headers) {
            delete event.request.headers['Authorization']
            delete event.request.headers['X-API-Key']
          }
        }

        return event // Return null if you want to drop the event
      },
    })
  }
}
