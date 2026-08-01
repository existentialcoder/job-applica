/**
 * Background service worker — cross-browser (Chrome MV3, Firefox MV3).
 *
 * 1. OAuth relay: watches for /auth/relay on both dev and prod origins,
 *    extracts tokens, saves to storage, closes the tab.
 * 2. Web app session sync (web → ext): receives SYNC_AUTH messages from
 *    content/webapp.js and mirrors the token into extension storage.
 * 3. Extension session sync (ext → web): when extension storage changes
 *    (e.g. popup login/logout), notifies open web app tabs via APPLY_TOKEN.
 *
 * Sessions are stored per-origin (session_<origin>), not as one flat value —
 * a token issued by the local dev backend is meaningless to the production
 * backend (different signing secret) and vice versa. Treating them as one
 * shared value let a stale/logged-out tab on one origin silently wipe a
 * perfectly valid session on the other, cascading a forced logout everywhere.
 */

const ext = globalThis.browser ?? globalThis.chrome;

const RELAY_PATH = '/auth/relay';
const WEBAPP_ORIGINS = ['http://localhost:5173', 'https://app.jobapplica.io'];

function sessionKey(origin) {
  return `session_${origin}`;
}

// ── OAuth relay ───────────────────────────────────────────────────────────────

ext.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'loading') return;

  const url = tab.url || changeInfo.url;
  if (!url) return;

  let parsed;
  try { parsed = new URL(url); } catch { return; }

  if (!WEBAPP_ORIGINS.includes(parsed.origin) || parsed.pathname !== RELAY_PATH) return;

  const accessToken = parsed.searchParams.get('access_token');
  const refreshToken = parsed.searchParams.get('refresh_token');
  if (!accessToken) return;

  const session = { access_token: accessToken };
  if (refreshToken) session.refresh_token = refreshToken;

  const items = { [sessionKey(parsed.origin)]: session };
  const stored = ext.storage.local.set(items);
  const close = () => ext.tabs.remove(tabId);
  if (stored && typeof stored.then === 'function') {
    stored.then(close);
  } else {
    ext.storage.local.set(items, close);
  }
});

// ── Web app → Extension (SYNC_AUTH) ──────────────────────────────────────────

ext.runtime.onMessage.addListener((message, sender) => {
  if (message.type !== 'SYNC_AUTH') return;

  const origin = sender?.tab?.url ? new URL(sender.tab.url).origin : null;
  if (!origin || !WEBAPP_ORIGINS.includes(origin)) return;

  if (message.access_token) {
    ext.storage.local.set({ [sessionKey(origin)]: { access_token: message.access_token } });
  } else {
    ext.storage.local.remove([sessionKey(origin)]);
  }
});

// ── Extension → Web app (storage.onChanged → APPLY_TOKEN) ────────────────────

ext.storage.onChanged.addListener(async (changes, area) => {
  if (area !== 'local') return;

  for (const origin of WEBAPP_ORIGINS) {
    const key = sessionKey(origin);
    if (!(key in changes)) continue;

    const newToken = changes[key].newValue?.access_token || null;
    const oldToken = changes[key].oldValue?.access_token || null;
    // Skip if the token value didn't actually change — avoids spurious APPLY_TOKEN
    // messages that would trigger redundant fetchMe() calls in the web app.
    if (newToken === oldToken) continue;

    const tabs = await ext.tabs.query({ url: `${origin}/*` }).catch(() => []);
    for (const tab of tabs) {
      if (!tab.id) continue;
      try {
        // Ensure content script is live in this tab before messaging
        await ext.scripting.executeScript({ target: { tabId: tab.id }, files: ['content/webapp.js'] });
      } catch { /* already injected or inaccessible */ }
      try {
        await ext.tabs.sendMessage(tab.id, { type: 'APPLY_TOKEN', access_token: newToken });
      } catch { /* tab may have closed */ }
    }
  }
});
