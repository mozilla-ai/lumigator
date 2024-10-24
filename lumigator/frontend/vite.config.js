// vite.config.js
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
  },
  build: {
    target: 'esnext' // Ensures support for the latest JavaScript features
  }
});
