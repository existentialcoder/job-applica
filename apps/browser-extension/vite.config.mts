import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwind from 'tailwindcss';
import autoprefixer from 'autoprefixer';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import { fileURLToPath } from 'url';
import path from 'path';

// emulate __dirname in ESM
const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, __dirname, '')
  const production = env.NODE_ENV === 'production'

  return {
    root: __dirname,
    base: './', // relative for extension
    appType: 'spa',
    plugins: [
      vue(),
      viteStaticCopy({
        targets: [
          { src: 'src/manifest.json', dest: '.' },
          { src: 'src/assets/*', dest: 'assets' }
        ],
      }),
    ],
    css: {
      postcss: {
        plugins: [tailwind(), autoprefixer()],
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    build: {
      minify: production,
      sourcemap: !production,
      outDir: 'dist',
      rollupOptions: {
        input: {
          popup: path.resolve(__dirname, 'src/popup.html'),
          background: path.resolve(__dirname, 'src/background.ts'),
          content: path.resolve(__dirname, 'src/content.ts'),
          options: path.resolve(__dirname, 'src/options.html'),
        },
        output: {
          entryFileNames: 'assets/[name].js',
          chunkFileNames: 'assets/[name].js',
          assetFileNames: 'assets/[name].[ext]',
        },
      },
    },
  }
})
