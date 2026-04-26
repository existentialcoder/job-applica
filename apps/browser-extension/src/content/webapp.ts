/**
 * Runs on the Job Applica web app (localhost:5173).
 *
 * Web app → Extension: forwards ja:auth events as SYNC_AUTH to background.
 * Extension → Web app: receives APPLY_TOKEN and re-dispatches as
 *   ja:token-from-extension so App.vue can update the auth store.
 *
 * suppressNextSync stops the echo loop when a token arrived from the extension.
 */

let suppressNextSync = false;
let contextValid = true;

function trySend(msg: Record<string, unknown>): void {
  if (!contextValid) return;
  const rt =
    (typeof chrome !== 'undefined' && chrome?.runtime ? chrome.runtime : null) ??
    (typeof browser !== 'undefined' && browser?.runtime ? browser.runtime : null);
  if (!rt) return;
  try {
    void rt.sendMessage(msg);
  } catch (e: unknown) {
    if (e instanceof Error && e.message.includes('Extension context invalidated')) {
      contextValid = false;
      window.removeEventListener('ja:auth', onAuth);
    }
  }
}

// Sync current token on initial load
const token = localStorage.getItem('access_token');
if (token) {
  trySend({ type: 'SYNC_AUTH', access_token: token });
}

function onAuth(e: Event): void {
  if (suppressNextSync) {
    suppressNextSync = false;
    return;
  }
  const detail = (e as CustomEvent<{ token?: string | null }>).detail;
  trySend({ type: 'SYNC_AUTH', access_token: detail?.token ?? null });
}

window.addEventListener('ja:auth', onAuth);

const rt =
  (typeof chrome !== 'undefined' && chrome?.runtime ? chrome.runtime : null) ??
  (typeof browser !== 'undefined' && browser?.runtime ? browser.runtime : null);

rt?.onMessage.addListener((message: unknown) => {
  const msg = message as { type?: string; access_token?: string | null; refresh_token?: string | null };
  if (msg.type !== 'APPLY_TOKEN') return;
  suppressNextSync = true;
  window.dispatchEvent(new CustomEvent('ja:token-from-extension', {
    detail: {
      access_token: msg.access_token ?? null,
      refresh_token: msg.refresh_token ?? null,
    },
  }));
});
