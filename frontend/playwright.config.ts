import os from 'node:os';
import path from 'node:path';

import { defineConfig, devices } from '@playwright/test';

// Ports apart from the usual dev ports (8099/8123), so a running dev setup doesn't clash.
const BACKEND_PORT = '18100';
const INGRESS_PORT = '18123';
export const INGRESS_PREFIX = '/api/hassio_ingress/e2e';

const backendDir = path.resolve(import.meta.dirname, '..', 'backend');

/** Runs the built app (`pnpm build` first) behind the fake ingress proxy. */
export default defineConfig({
  testDir: './e2e',
  // One worker: the tests share one backend and its spike table.
  workers: 1,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: `http://127.0.0.1:${INGRESS_PORT}`,
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'phone', use: { ...devices['Pixel 7'] } },
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } },
    },
  ],
  webServer: [
    {
      command: `uv run --project "${backendDir}" python -m homestead_finance --host 127.0.0.1 --port ${BACKEND_PORT}`,
      url: `http://127.0.0.1:${BACKEND_PORT}/api/health`,
      env: {
        HF_TRUSTED_PROXIES: '127.0.0.1',
        HF_STATIC_DIR: path.resolve(import.meta.dirname, 'dist'),
        HF_DATA_DIR: path.join(os.tmpdir(), 'homestead-finance-e2e'),
        HF_VERSION: 'e2e',
        HF_LOG_LEVEL: 'warning',
      },
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: 'node e2e/fake-ingress.mjs',
      url: `http://127.0.0.1:${INGRESS_PORT}${INGRESS_PREFIX}/`,
      env: { INGRESS_PORT, BACKEND_PORT, INGRESS_PREFIX },
      reuseExistingServer: !process.env.CI,
    },
  ],
});
