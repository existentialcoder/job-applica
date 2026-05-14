const CHROME_URL = 'https://chromewebstore.google.com/detail/job-applica-tracker/pdeohjoaoidbbjlnbmcfccokiblckhcg'
const FIREFOX_URL = 'https://addons.mozilla.org/firefox/addon/job-applica-tracker/'

type Browser = 'chrome' | 'firefox' | 'other'

function detectBrowser(): Browser {
  if (typeof navigator === 'undefined') return 'other'
  const ua = navigator.userAgent
  if (ua.includes('Firefox')) return 'firefox'
  // Edge and other Chromium forks include "Chrome" — all go to Chrome Web Store
  if (ua.includes('Chrome')) return 'chrome'
  return 'other'
}

export function useExtensionLink() {
  const browser = ref<Browser>('other')

  onMounted(() => {
    browser.value = detectBrowser()
  })

  const storeUrl = computed(() =>
    browser.value === 'firefox' ? FIREFOX_URL : CHROME_URL
  )

  const storeName = computed(() =>
    browser.value === 'firefox' ? 'Firefox Add-ons' : 'Chrome Web Store'
  )

  return { browser, storeUrl, storeName }
}
