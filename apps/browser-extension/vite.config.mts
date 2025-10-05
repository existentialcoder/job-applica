import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/postcss'
import autoprefixer from 'autoprefixer'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  const isProd = env.NODE_ENV === 'production'

  return {
    base: './',
    plugins: [vue()],
    css: {
      postcss: {
        plugins: [tailwindcss(), autoprefixer()],
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    build: {
      outDir: path.resolve(__dirname, 'dist'),
      emptyOutDir: true,
      sourcemap: !isProd,
      rollupOptions: {
        // 👇 set your actual entry file (source)
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
