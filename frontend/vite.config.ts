import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  // Relative asset URLs: Home Assistant ingress serves the app under a dynamic base path.
  base: './',
  plugins: [react()],
  build: {
    // One bundle (~160 kB gzipped) served locally through ingress and cached as immutable.
    chunkSizeWarningLimit: 800,
  },
  server: {
    proxy: { '/api': 'http://127.0.0.1:8099' },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
  },
});
