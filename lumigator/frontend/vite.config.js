// vite.config.js
import { fileURLToPath, URL } from 'node:url';
import { resolve, dirname } from 'node:path';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  envPrefix: 'VUE_APP_',
  envDir: '../../',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Adds '@' alias for 'src' directory
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
  },
  server: {
    host: 'localhost',
    port: 3000,
    strictPort: true,
    proxy: {
      '/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/v1/, '/api/v1'),
      },
    },
  },
  build: {
    target: 'esnext',
  },
});
