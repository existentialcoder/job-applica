/**
 * Background service worker — cross-browser (Chrome MV3, Firefox MV3).
 *
 * 1. OAuth relay: watches for /auth/relay on both dev and prod origins,
 *    extracts tokens, saves to storage, closes the tab.
 * 2. Web app session sync (web → ext): receives SYNC_AUTH messages from
 *    content/webapp.js and mirrors the token into extension storage.
 * 3. Extension session sync (ext → web): when extension storage changes
 *    (e.g. popup login/logout), notifies open web app tabs via APPLY_TOKEN.
 */

const ext = globalThis.browser ?? globalThis.chrome;

const RELAY_ORIGINS = ['http://localhost:5173', 'https://app.jobapplica.io'];
const RELAY_PATH = '/auth/relay';
const WEBAPP_URL_PATTERNS = ['http://localhost:5173/*', 'https://app.jobapplica.io/*'];

// ── OAuth relay ───────────────────────────────────────────────────────────────

ext.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'loading') return;

  const url = tab.url || changeInfo.url;
  if (!url) return;

  let parsed;
  try { parsed = new URL(url); } catch { return; }

  if (!RELAY_ORIGINS.includes(parsed.origin) || parsed.pathname !== RELAY_PATH) return;

  const accessToken = parsed.searchParams.get('access_token');
  const refreshToken = parsed.searchParams.get('refresh_token');
  if (!accessToken) return;

  const items = { access_token: accessToken };
  if (refreshToken) items.refresh_token = refreshToken;

  const stored = ext.storage.local.set(items);
  const close = () => ext.tabs.remove(tabId);
  if (stored && typeof stored.then === 'function') {
    stored.then(close);
  } else {
    ext.storage.local.set(items, close);
  }
});

// ── Web app → Extension (SYNC_AUTH) ──────────────────────────────────────────

ext.runtime.onMessage.addListener((message) => {
  if (message.type !== 'SYNC_AUTH') return;

  if (message.access_token) {
    ext.storage.local.set({ access_token: message.access_token });
  } else {
    ext.storage.local.remove(['access_token', 'refresh_token']);
  }
});

// ── Extension → Web app (storage.onChanged → APPLY_TOKEN) ────────────────────

ext.storage.onChanged.addListener(async (changes, area) => {
  if (area !== 'local' || !('access_token' in changes)) return;

  const newToken = changes.access_token?.newValue || null;
  const oldToken = changes.access_token?.oldValue || null;
  // Skip if the token value didn't actually change — avoids spurious APPLY_TOKEN
  // messages that would trigger redundant fetchMe() calls in the web app.
  if (newToken === oldToken) return;

  const tabArrays = await Promise.all(
    WEBAPP_URL_PATTERNS.map(pattern => ext.tabs.query({ url: pattern }).catch(() => []))
  );
  const tabs = tabArrays.flat();

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
});
