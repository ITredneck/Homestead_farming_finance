// Runs the built app behind the fake ingress proxy, like Home Assistant would serve it.
// Usage: pnpm build && pnpm ingress   then open the printed URL.
import { spawn } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const frontend = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const backend = path.join(frontend, '..', 'backend');
const BACKEND_PORT = '8099';
const INGRESS_PORT = '8123';
const INGRESS_PREFIX = '/api/hassio_ingress/dev';

const children = [
  spawn(
    'uv',
    [
      ...['run', '--project', backend, 'python', '-m', 'homestead_finance'],
      ...['--host', '127.0.0.1', '--port', BACKEND_PORT],
    ],
    {
      stdio: 'inherit',
      env: {
        ...process.env,
        HF_TRUSTED_PROXIES: '127.0.0.1',
        HF_STATIC_DIR: path.join(frontend, 'dist'),
        HF_DATA_DIR: path.join(os.tmpdir(), 'homestead-finance-ingress'),
      },
    },
  ),
  spawn(process.execPath, [path.join(frontend, 'e2e', 'fake-ingress.mjs')], {
    stdio: 'inherit',
    env: { ...process.env, INGRESS_PORT, BACKEND_PORT, INGRESS_PREFIX },
  }),
];

const stop = () => {
  for (const child of children) {
    child.kill();
  }
  process.exit(0);
};
process.on('SIGINT', stop);
process.on('SIGTERM', stop);
for (const child of children) {
  child.on('exit', stop);
}
