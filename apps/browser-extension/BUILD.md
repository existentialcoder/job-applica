# Build Instructions — Job Applica Tracker (Firefox Extension)

## Requirements

- **OS**: Linux, macOS, or Windows
- **Node.js**: v18 or higher — https://nodejs.org
- **Yarn**: v1.x — install with `npm install -g yarn`

## Steps

```bash
# 1. Install dependencies
yarn install

# 2. Build the extension
yarn build
```

The output is placed in the `dist/` folder.

## What the build produces

- `dist/popup.js` — compiled popup UI (Vue 3)
- `dist/popup.html` / `dist/popup.css` / `dist/main.css` — popup page and styles
- `dist/background.js` — background script (cross-browser, unmodified from source)
- `dist/content/linkedin.js` — LinkedIn content script
- `dist/content/indeed.js` — Indeed content script
- `dist/content/glassdoor.js` — Glassdoor content script
- `dist/content/monster.js` — Monster content script
- `dist/content/ziprecruiter.js` — ZipRecruiter content script
- `dist/content/jobscan.js` — Jobscan content script
- `dist/content/webapp.js` — JobApplica web app bridge script
- `dist/manifest.json` — copied from `public/manifest.json`
- `dist/icon-*.png` / `dist/icon-*.svg` — copied from `public/`

## Reproducing the submitted zip

```bash
yarn install
yarn build
cd dist
zip -r ../extension-firefox.zip . --exclude "*.map" --exclude "tailwind.js"
```

## Tools used

| Tool | Version | Purpose |
|------|---------|---------|
| Vite | 5.x | Bundles popup (Vue SFC → JS) |
| Rollup (via Vite) | — | Bundles content scripts as IIFE |
| Vue 3 | 3.x | Popup UI framework |
| Tailwind CSS | 3.x | Utility CSS (compiled to static CSS, no runtime) |
| TypeScript | 5.x | Type checking only; compiled away |
