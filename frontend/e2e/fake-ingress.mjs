// Simulates Home Assistant ingress for local testing and e2e tests.
//
// Like the Supervisor, it serves the app under a nested base path, strips that path
// before proxying, drops any identity headers the browser sent and adds its own, plus
// X-Ingress-Path. The backend must trust 127.0.0.1 (HF_TRUSTED_PROXIES=127.0.0.1).
import http from 'node:http';

const PORT = Number(process.env.INGRESS_PORT ?? 8123);
const BACKEND_PORT = Number(process.env.BACKEND_PORT ?? 8099);
const PREFIX = (process.env.INGRESS_PREFIX ?? '/api/hassio_ingress/dev').replace(/\/$/, '');

const IDENTITY = {
  'x-remote-user-id': process.env.INGRESS_USER_ID ?? 'local-test-user',
  'x-remote-user-name': 'tester',
  'x-remote-user-display-name': 'Local Tester',
};

const server = http.createServer((request, response) => {
  const url = request.url ?? '/';
  if (url !== PREFIX && !url.startsWith(`${PREFIX}/`)) {
    response.writeHead(404, { 'content-type': 'text/plain' });
    response.end(`Not under the ingress path ${PREFIX}/`);
    return;
  }
  const headers = { ...request.headers, host: `127.0.0.1:${BACKEND_PORT}` };
  for (const name of Object.keys(IDENTITY)) {
    delete headers[name];
  }
  Object.assign(headers, IDENTITY, { 'x-ingress-path': PREFIX });

  const upstream = http.request(
    {
      host: '127.0.0.1',
      port: BACKEND_PORT,
      method: request.method,
      path: url.slice(PREFIX.length) || '/',
      headers,
    },
    (backendResponse) => {
      response.writeHead(backendResponse.statusCode ?? 502, backendResponse.headers);
      backendResponse.pipe(response);
    },
  );
  upstream.on('error', (error) => {
    response.writeHead(502, { 'content-type': 'text/plain' });
    response.end(`Backend not reachable: ${error.message}`);
  });
  request.pipe(upstream);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Fake ingress: http://127.0.0.1:${PORT}${PREFIX}/ -> backend port ${BACKEND_PORT}`);
});
