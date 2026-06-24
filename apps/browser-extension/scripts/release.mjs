/**
 * Bumps the manifest version, builds for Chrome and Firefox, and produces
 * extension-chrome.zip / extension-firefox.zip in the project root.
 *
 * Usage (via yarn):
 *   yarn release           # patch bump  (1.0.1 → 1.0.2)
 *   yarn release minor     # minor bump  (1.0.1 → 1.1.0)
 *   yarn release major     # major bump  (1.0.1 → 2.0.0)
 */

import { readFileSync, rmSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');
const MANIFEST_PATH = resolve(root, 'public/manifest.json');

// ── Version bump ──────────────────────────────────────────────────────────────
const bumpType = process.argv.find(a => ['major', 'minor', 'patch'].includes(a)) ?? 'patch';

const manifest = JSON.parse(readFileSync(MANIFEST_PATH, 'utf-8'));
const [maj, min, pat] = manifest.version.split('.').map(Number);

const newVersion =
  bumpType === 'major' ? `${maj + 1}.0.0` :
  bumpType === 'minor' ? `${maj}.${min + 1}.0` :
                         `${maj}.${min}.${pat + 1}`;

console.log(`\nVersion: ${manifest.version} → ${newVersion}  (${bumpType} bump)\n`);

// ── Helpers ───────────────────────────────────────────────────────────────────
function run(cmd) {
  execSync(cmd, { stdio: 'inherit', cwd: root, shell: true });
}

function prepareManifest(firefox = false) {
  const flag = firefox ? '--firefox' : '';
  run(`VERSION=${newVersion} node scripts/prepare-release.mjs ${flag}`);
}

function buildExtension() {
  run('yarn build:prod');
}

function zip(outputFile) {
  const dest = resolve(root, outputFile);
  if (existsSync(dest)) rmSync(dest);
  // zip from inside dist so paths inside the archive are flat
  execSync(`zip -r "${dest}" .`, { stdio: 'inherit', cwd: resolve(root, 'dist'), shell: true });
  console.log(`  → ${outputFile}`);
}

// ── Chrome ────────────────────────────────────────────────────────────────────
console.log('── Chrome ───────────────────────────────────────────────────────');
prepareManifest(false);
buildExtension();
zip('extension-chrome.zip');

// ── Firefox ───────────────────────────────────────────────────────────────────
console.log('\n── Firefox ──────────────────────────────────────────────────────');
prepareManifest(true);
buildExtension();
zip('extension-firefox.zip');

// ── Restore manifest to Chrome/neutral form for source control ────────────────
prepareManifest(false);

console.log(`\nDone! v${newVersion} ready — extension-chrome.zip & extension-firefox.zip\n`);
