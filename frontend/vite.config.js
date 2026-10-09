import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    proxy: {
      '/api': process.env.API_PROXY_TARGET || 'http://127.0.0.1:8000',
      '/uploads': process.env.API_PROXY_TARGET || 'http://127.0.0.1:8000',
    },
  },
});