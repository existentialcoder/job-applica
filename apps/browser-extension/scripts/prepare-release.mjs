/**
 * Prepares manifest.json for a production release:
 *  - Updates the version from the VERSION env var
 *  - Replaces localhost host_permissions / content_scripts with production URLs
 *  - Writes an optional Firefox variant with the gecko ID injected
 *  - Writes .env.production so Vite bakes the correct URLs into the JS bundle
 *
 * Usage:
 *   VERSION=1.2.3 \
 *   FRONTEND_URL=https://app.jobapplica.io \
 *   BACKEND_URL=https://api.jobapplica.io \
 *   FIREFOX_EXTENSION_ID=jobapplica@jobapplica.io \
 *   node scripts/prepare-release.mjs [--firefox]
 */

import { readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const MANIFEST_PATH = resolve(__dirname, '../public/manifest.json');

const VERSION       = process.env.VERSION;
const FRONTEND_URL  = process.env.FRONTEND_URL || 'https://app.jobapplica.io';
const BACKEND_URL   = process.env.BACKEND_URL  || 'https://api.jobapplica.io';
const GECKO_ID      = process.env.FIREFOX_EXTENSION_ID || 'jobapplica@jobapplica.io';
const FOR_FIREFOX   = process.argv.includes('--firefox');

const manifest = JSON.parse(readFileSync(MANIFEST_PATH, 'utf-8'));

// ── Version ───────────────────────────────────────────────────────────────────
if (VERSION) {
  // Chrome/Firefox manifests use at most 4 numeric parts (no pre-release tags)
  manifest.version = VERSION.replace(/[^0-9.]/g, '').replace(/\.+$/, '');
}

// ── host_permissions: swap localhost → production ─────────────────────────────
manifest.host_permissions = (manifest.host_permissions || [])
  .filter(p => !p.includes('localhost'))
  .concat([`${FRONTEND_URL}/*`, `${BACKEND_URL}/*`]);

// ── content_scripts: swap localhost → production ──────────────────────────────
if (manifest.content_scripts) {
  manifest.content_scripts = manifest.content_scripts.map(cs => ({
    ...cs,
    matches: cs.matches.map(m =>
      m.includes('localhost') ? `${FRONTEND_URL}/*` : m
    ),
  }));
}

// ── Firefox: inject gecko ID (preserve existing strict_min_version / data_collection_permissions) ──
if (FOR_FIREFOX) {
  const existing = manifest.browser_specific_settings?.gecko || {};
  manifest.browser_specific_settings = {
    gecko: {
      ...existing,
      id: GECKO_ID,
    },
  };
}

writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2) + '\n');
console.log(`manifest.json updated → v${manifest.version}${FOR_FIREFOX ? ' (Firefox)' : ' (Chrome)'}`);

// ── Write .env.production so Vite bakes the right URLs into the JS bundle ─────
// .env.production is gitignored (no secrets, but avoids confusion); this script
// generates it fresh every release so CI doesn't need a committed env file.
const ENV_PATH = resolve(__dirname, '../.env.production');
writeFileSync(
  ENV_PATH,
  `VITE_API_BASE=${BACKEND_URL}/api/v1\nVITE_APP_URL=${FRONTEND_URL}\n`,
);
console.log(`  .env.production written → API: ${BACKEND_URL}/api/v1  App: ${FRONTEND_URL}`);
