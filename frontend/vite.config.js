import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  
  // Proxy für die API-Anfragen
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', //http://167.233.33.166
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/media': {
        target: 'http://127.0.0.1:8000', //http://167.233.33.166
        changeOrigin: true
      }
    }
  }
})
