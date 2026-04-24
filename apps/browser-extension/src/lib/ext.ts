/**
 * Cross-browser WebExtension API wrapper.
 *
 * Modern Chrome (v130+) exposes `browser` as an alias for `chrome`.
 * Firefox MV3 uses `browser` natively with Promise-based APIs.
 * For older Chrome where `browser` is undefined, we fall back to `chrome`
 * and manually promisify the callback-based APIs.
 */

function getExtApi(): BrowserExtension {
  // Firefox and modern Chrome expose `browser` natively
  if (typeof browser !== 'undefined') return browser;
  // Older Chrome only has `chrome` — wrap callbacks in Promises
  if (typeof chrome !== 'undefined') return wrapChrome(chrome);
  // Dev / test environment fallback (e.g. running outside extension context)
  return createNoopApi();
}

function wrapChrome(cr: typeof chrome): BrowserExtension {
  return {
    storage: {
      local: {
        get: (keys) =>
          new Promise((resolve) =>
            cr.storage.local.get(keys as any, (result: Record<string, any>) => resolve(result))
          ),
        set: (items) =>
          new Promise<void>((resolve) => (cr.storage.local as any).set(items, resolve)),
        remove: (keys) =>
          new Promise<void>((resolve) => (cr.storage.local as any).remove(keys, resolve)),
      },
      onChanged: cr.storage.onChanged,
    },
    tabs: {
      query: (queryInfo) =>
        new Promise((resolve) =>
          (cr.tabs as any).query(queryInfo, resolve)
        ),
      create: (props) =>
        new Promise((resolve) => (cr.tabs as any).create(props, resolve)),
      remove: (tabIds) =>
        new Promise<void>((resolve) => (cr.tabs as any).remove(tabIds, resolve)),
      sendMessage: (tabId, message) =>
        new Promise((resolve) => (cr.tabs as any).sendMessage(tabId, message, resolve)),
      onUpdated: cr.tabs.onUpdated,
    },
    scripting: cr.scripting,
    runtime: cr.runtime,
  };
}

function createNoopApi(): BrowserExtension {
  const noop = () => Promise.resolve({} as any);
  return {
    storage: {
      local: { get: noop, set: noop, remove: noop },
      onChanged: { addListener: () => {}, removeListener: () => {} },
    },
    tabs: {
      query: () => Promise.resolve([]),
      create: () => Promise.resolve({}),
      remove: noop,
      sendMessage: noop,
      onUpdated: { addListener: () => {}, removeListener: () => {} },
    },
    scripting: { executeScript: noop },
    runtime: {
      sendMessage: noop,
      onMessage: { addListener: () => {}, removeListener: () => {} },
    },
  };
}

const ext = getExtApi();
export default ext;
