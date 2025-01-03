import { createI18n } from 'vue-i18n';

import en from '@/locales/en.json';

// If you plan to support multiple languages, you can load them conditionally or eagerly.
// For now, we load only English:
const setupI18n = () => {
  const instance = createI18n({
    globalInjection: true, // Allows using $t in templates globally
    allowComposition: true,
    legacy: false, // Use Composition API style
    warnHtmlMessage: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages: {
      en,
    },
  });
  instance.global.locale.value = 'en';
  return instance;
};

const i18n = setupI18n();

export default i18n;
