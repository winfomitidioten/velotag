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
  // changeOrigin: false ist wichtig - Django baut die Bild-URLs mit build_absolute_uri()
  // aus dem Host-Header. Mit changeOrigin: true käme dort 127.0.0.1:8000 an, was im
  // Android-Emulator auf das Gerät selbst zeigt und die Bilder ins Leere laufen lässt.
  // So bleibt der Host des Dev-Servers stehen und die Bilder kommen wieder über den Proxy zurück.
  server: {
    host: true,
    proxy: {
      '/api': {
<<<<<<< Updated upstream
        target: 'http://167.233.33.166',
//        target: 'http://127.0.0.1:8000',      // Für die Entwicklung: das hier auskommentieren und das andere target kommentieren
        changeOrigin: false,
        rewrite: (path) => path
      },
      '/media': {
<<<<<<< Updated upstream
        target: '//http://167.233.33.166',
//        target: 'http://127.0.0.1:8000',      // Für die Entwicklung: das hier auskommentieren und das andere target kommentieren
        changeOrigin: false
      }
    }
  }
})