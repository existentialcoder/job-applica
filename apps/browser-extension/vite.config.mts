import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath } from 'url'
import { createRequire } from 'module'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const uiPkg = path.resolve(__dirname, '../../packages/ui/src')
const require = createRequire(import.meta.url)

// Plugin: resolve bare package imports (e.g. 'class-variance-authority') that
// originate from packages/ui using the extension's own node_modules.
function resolveSharedPkgDeps() {
  return {
    name: 'resolve-shared-pkg-deps',
    resolveId(id: string, importer?: string) {
      if (
        importer?.includes('packages/ui') &&
        !id.startsWith('.') &&
        !id.startsWith('/') &&
        !id.startsWith('@/')
      ) {
        try {
          return require.resolve(id, { paths: [__dirname] })
        } catch {
          // fall through to default resolution
        }
      }
    },
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  const isProd = env.NODE_ENV === 'production'

  return {
    base: './',
    plugins: [resolveSharedPkgDeps(), vue()],
    resolve: {
      // More specific aliases must come before generic '@'
      alias: [
        // Route shared-package internal imports to packages/ui/src
        { find: /^@\/components\/ui(.*)$/, replacement: `${uiPkg}/components/ui$1` },
        { find: /^@\/lib\/utils$/, replacement: `${uiPkg}/lib/utils` },
        // Named package import from extension code
        { find: '@job-applica/ui', replacement: uiPkg },
        // Extension's own source files
        { find: '@', replacement: path.resolve(__dirname, 'src') },
      ],
    },
    build: {
      outDir: path.resolve(__dirname, 'dist'),
      emptyOutDir: true,
      sourcemap: !isProd,
      rollupOptions: {
        input: path.resolve(__dirname, 'src/main.ts'),
        output: {
          entryFileNames: 'popup.js',
          assetFileNames: '[name][extname]',
        },
      },
      target: 'esnext',
      minify: isProd,
    },
  }
})
