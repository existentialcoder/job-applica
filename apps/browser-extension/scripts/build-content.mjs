/**
 * Builds each content script as a self-contained IIFE.
 * Rollup's IIFE format requires a single entry per build, so we run one
 * build per provider via Vite's programmatic API.
 */
import { build } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const outDir = path.resolve(root, 'dist');

const scripts = [
  'linkedin',
  'indeed',
  'glassdoor',
  'monster',
  'ziprecruiter',
  'jobscan',
  'webapp',
];

for (const name of scripts) {
  await build({
    configFile: false,
    logLevel: 'warn',
    resolve: {
      alias: [{ find: '@', replacement: path.resolve(root, 'src') }],
    },
    build: {
      outDir,
      emptyOutDir: false,
      sourcemap: true,
      lib: {
        entry: path.resolve(root, `src/content/${name}.ts`),
        formats: ['iife'],
        name: '__ja',
      },
      rollupOptions: {
        output: {
          entryFileNames: `content/${name}.js`,
          assetFileNames: '[name][extname]',
        },
      },
    },
  });
  console.log(`  content/${name}.js`);
}
