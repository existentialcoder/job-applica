import en from '~/locales/en.json'

/**
 * Returns the English translation object.
 * Drop-in compatible with @nuxtjs/i18n when multi-locale is needed later.
 */
export function useT() {
  return en
}
