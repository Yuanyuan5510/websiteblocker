import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 16410,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:16411',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
  },
})
