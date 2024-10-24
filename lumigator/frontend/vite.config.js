// vite.config.js
import { fileURLToPath, URL } from 'node:url';
import { resolve, dirname } from 'node:path';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Optional: Adds '@' alias for 'src' directory
    }
	},
	server: {
    host: 'localhost', // Specify the host
    port: 3000,        // Specify the port
		strictPort: true,  // Fail if the port is already in use
		proxy: {
      '/api/v1': {
        target: 'http://localhost:8000', // Your backend's base URL
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/v1/, '/api/v1'), // Ensure `/api/v1` is kept in the path
      },
    },
  },
  build: {
    target: 'esnext' // Ensures support for the latest JavaScript features
  }
});
