/**
 * Utilities shared by all content scripts.
 * Imported here; inlined by Rollup into each bundle — no runtime shared chunk.
 */

export function sendMessage(msg: Record<string, unknown>): void {
  const rt =
    (typeof chrome !== 'undefined' && chrome?.runtime ? chrome.runtime : null) ??
    (typeof browser !== 'undefined' && browser?.runtime ? browser.runtime : null);
  if (!rt) return;
  try { void rt.sendMessage(msg); } catch { /* extension reloaded mid-flight */ }
}

/**
 * Returns the first element matching any selector that has non-empty text.
 * `root` defaults to `document`; pass a panel element to scope the search.
 */
export function first(
  selectors: string[],
  root: Element | Document = document,
): Element | null {
  for (const sel of selectors) {
    const el = root.querySelector(sel);
    if (el?.textContent?.trim()) return el;
  }
  return null;
}

/** Infers Remote / Hybrid / On-site from location string and job description. */
export function inferWorkModel(
  location: string | null,
  description: string | null,
): 'Remote' | 'Hybrid' | 'On-site' {
  const combined = `${location ?? ''} ${description ?? ''}`.toLowerCase();
  if (combined.includes('fully remote') || location?.toLowerCase() === 'remote') return 'Remote';
  if (combined.includes('remote')) return 'Remote';
  if (combined.includes('hybrid')) return 'Hybrid';
  return 'On-site';
}
