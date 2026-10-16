import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

// Resolve junction/symlink paths (e.g. C:\GSPR) to the real project directory
const root = fs.realpathSync.native(path.dirname(fileURLToPath(import.meta.url)))

// https://vite.dev/config/
export default defineConfig({
  root,
  plugins: [
    react(),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/auth': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/ping': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  },
  test: {
    include: ['tests/**/*.test.{js,jsx}'],
    environment: 'jsdom',
    globals: true,
    setupFiles: [path.join(root, 'vitest.setup.js')],
  },
})
