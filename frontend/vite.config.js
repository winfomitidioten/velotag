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
<<<<<<< Updated upstream
        target: 'http://167.233.33.166',
//        target: 'http://127.0.0.1:8000',      // Für die Entwicklung: das hier auskommentieren und das andere target kommentieren    
=======
//        target: 'http://167.233.33.166',
        target: 'http://10.0.2.2:8000',      // Für die Entwicklung: das hier auskommentieren und das andere target kommentieren    
>>>>>>> Stashed changes
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/media': {
<<<<<<< Updated upstream
        target: '//http://167.233.33.166',
//        target: 'http://127.0.0.1:8000',      // Für die Entwicklung: das hier auskommentieren und das andere target kommentieren
=======
//        target: '//http://167.233.33.166',
        target: 'http://10.0.2.2:8000',      // Für die Entwicklung: das hier auskommentieren und das andere target kommentieren
>>>>>>> Stashed changes
        changeOrigin: true
      }
    }
  }
})
