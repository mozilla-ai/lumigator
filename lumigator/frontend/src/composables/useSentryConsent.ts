import { ref } from 'vue'

export const SENTRY_CONSENT_LOCAL_STORAGE_KEY = 'sentry-consent'

export function useSentryConsent() {
  const hasResponded = ref(window.localStorage.getItem(SENTRY_CONSENT_LOCAL_STORAGE_KEY) !== null)
  const hasConsented = ref(window.localStorage.getItem(SENTRY_CONSENT_LOCAL_STORAGE_KEY) === 'true')

  const acceptConsent = () => {
    window.localStorage.setItem(SENTRY_CONSENT_LOCAL_STORAGE_KEY, 'true')
    hasResponded.value = true
    hasConsented.value = true
    window.location.reload()
  }

  const rejectConsent = () => {
    window.localStorage.setItem(SENTRY_CONSENT_LOCAL_STORAGE_KEY, 'false')
    hasResponded.value = true
    hasConsented.value = false
    window.location.reload()
  }

  const setConsent = (consent: boolean) => {
    if (consent) {
      acceptConsent()
    } else {
      rejectConsent()
    }
  }

  return { hasResponded, hasConsented, setConsent, acceptConsent, rejectConsent }
}
