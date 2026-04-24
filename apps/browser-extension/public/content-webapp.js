/**
 * Content script running on the Job Applica web app (localhost:5173).
 *
 * Web app → Extension: listens for ja:auth custom events dispatched by the auth
 *   store on login/logout, then forwards the token to the background worker via
 *   SYNC_AUTH so the extension popup stays in sync.
 *
 * Extension → Web app: listens for APPLY_TOKEN messages from the background
 *   worker (triggered when the extension logs in/out) and re-dispatches them as
 *   ja:token-from-extension so App.vue can update the auth store.
 *
 * suppressNextSync prevents an echo loop: when the web app applies a token that
 *   came from the extension, it must not immediately re-send it back.
 */
(function () {
  let suppressNextSync = false;

  // Sync current token on initial load
  const token = localStorage.getItem('access_token');
  if (token) {
    chrome.runtime.sendMessage({ type: 'SYNC_AUTH', access_token: token });
  }

  // Web app dispatches this custom event after every login / logout
  window.addEventListener('ja:auth', (e) => {
    if (suppressNextSync) {
      suppressNextSync = false;
      return;
    }
    const detail = /** @type {CustomEvent} */ (e).detail;
    chrome.runtime.sendMessage({ type: 'SYNC_AUTH', access_token: detail?.token || null });
  });

  // Background worker sends this when extension storage changes (extension login/logout)
  chrome.runtime.onMessage.addListener((message) => {
    if (message.type !== 'APPLY_TOKEN') return;
    suppressNextSync = true;
    window.dispatchEvent(new CustomEvent('ja:token-from-extension', {
      detail: {
        access_token: message.access_token || null,
        refresh_token: message.refresh_token || null,
      },
    }));
  });
})();
